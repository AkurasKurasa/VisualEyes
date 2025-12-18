import ast
import operator

class CodeParser:
    def __init__(self):
        self.context = {} # Symbol table for variable resolution

    def parse(self, code):
        structures = []
        self.context = {} # Reset context on each parse
        self.output = []  # Capture print() calls
        index_operations = []  # Track subscript operations
        loop_info = {
            "hasLoop": False,
            "target": None,
            "iterator": None,
            "loopDependencies": []
        }

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"structures": [], "error": f"Syntax Error: {e}", "output": []}

        # Iterate over top-level nodes in order to respect variable dependencies
        for node in tree.body:
            self._process_node(node, structures, index_operations, loop_info)

        # Ensure loop iterator exists in structures
        if loop_info["iterator"] and not any(s['name'] == loop_info["iterator"] for s in structures):
             structures.append({"name": loop_info["iterator"], "type": "variable", "data": "?"})
        
        # Ensure loop dependencies exist in structures
        for dep in loop_info["loopDependencies"]:
            dep_name = dep["name"]
            if not any(s['name'] == dep_name for s in structures):
                # Add with initial value from formula if it's a constant
                initial_value = dep.get("formula", "?")
                structures.append({"name": dep_name, "type": "variable", "data": initial_value})

        return {
            "structures": structures,
            "indexOperations": index_operations,
            "output": self.output,
            **loop_info
        }

    def _process_node(self, node, structures, index_operations, loop_info, silent=False):
        """Process a single AST node recursively."""
        try:
            # 1. Assignments
            if isinstance(node, ast.Assign):
                # Check for subscript assignment (e.g., lis[0] = 2)
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript):
                    subscript = node.targets[0]
                    if isinstance(subscript.value, ast.Name):
                        var_name = subscript.value.id
                        try:
                            # Evaluate the new value
                            new_value = self._evaluate(node.value)
                            # Get indices
                            indices = self._extract_indices(subscript.slice)
                            
                            # Update context if variable exists
                            if var_name in self.context and isinstance(self.context[var_name], (list, dict)):
                                for idx in indices:
                                    # Dictionary assignment
                                    if isinstance(self.context[var_name], dict):
                                        self.context[var_name][idx] = new_value
                                    # List assignment
                                    elif isinstance(self.context[var_name], list) and 0 <= idx < len(self.context[var_name]):
                                        self.context[var_name][idx] = new_value
                                        
                                # Update structures (only if not silent)
                                if not silent:
                                    if isinstance(self.context[var_name], list):
                                        self._add_or_update(structures, var_name, 'array', list(self.context[var_name]))
                                    elif isinstance(self.context[var_name], dict):
                                        data = [{"key": str(k), "value": str(v)} for k, v in self.context[var_name].items()]
                                        self._add_or_update(structures, var_name, 'dictionary', data)
                            
                            # Track the operation (only if not silent)
                            if not silent:
                                index_operations.append({
                                    "type": "assign",
                                    "varName": var_name,
                                    "indices": indices,
                                    "newValue": new_value
                                })
                        except Exception as e:
                            self.output.append(f"Runtime Error (Subscript Assign): {e}")
                
                # Regular variable assignment
                elif len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id
                    value_node = node.value
                    
                    data = None
                    type_str = 'variable'

                    # Try to evaluate the expression
                    try:
                        evaluated_value = self._evaluate(value_node)
                        
                        # Determine type based on result
                        if isinstance(evaluated_value, list):
                            type_str = 'array'
                            data = list(evaluated_value)
                        elif isinstance(evaluated_value, set):
                            type_str = 'set'
                            data = list(evaluated_value)
                        elif isinstance(evaluated_value, dict):
                            type_str = 'dictionary'
                            # Format for frontend: [{"key": k, "value": v}]
                            data = [{"key": str(k), "value": str(v)} for k, v in evaluated_value.items()]
                        elif isinstance(evaluated_value, (int, float, str, bool)):
                            type_str = 'variable'
                            data = evaluated_value
                        
                        # Update context for future references
                        self.context[var_name] = evaluated_value
                        # For frontend, we add to structures (only if not silent)
                        if not silent and data is not None:
                            self._add_or_update(structures, var_name, type_str, data)

                    except Exception as e:
                        # Report runtime errors during evaluation
                        self.output.append(f"Runtime Error (Assign {var_name}): {e}")
                
                # Tuple/List unpacking assignment: a, b = [1, 2]
                elif len(node.targets) == 1 and isinstance(node.targets[0], (ast.Tuple, ast.List)):
                    target_node = node.targets[0]
                    try:
                        # Evaluate the value (should be an iterable)
                        evaluated_value = self._evaluate(node.value)
                        
                        if hasattr(evaluated_value, '__iter__'):
                            values = list(evaluated_value)
                            for i, elt in enumerate(target_node.elts):
                                if i < len(values) and isinstance(elt, ast.Name):
                                    var_name = elt.id
                                    val = values[i]
                                    
                                    # Determine type and data for structures
                                    data = val
                                    type_str = 'variable'
                                    if isinstance(val, list):
                                        type_str = 'array'
                                        data = list(val)
                                    elif isinstance(val, set):
                                        type_str = 'set'
                                        data = list(val)
                                    elif isinstance(val, dict):
                                        type_str = 'dictionary'
                                        data = [{"key": str(k), "value": str(v)} for k, v in val.items()]
                                    
                                    # Update context and structures
                                    self.context[var_name] = val
                                    if not silent:
                                        self._add_or_update(structures, var_name, type_str, data)
                    except Exception as e:
                        self.output.append(f"Runtime Error (Unpacking): {e}")

            # 2. Conditional Statements (if/elif/else)
            elif isinstance(node, ast.If):
                try:
                    # Evaluate the condition
                    condition_result = self._evaluate(node.test)
                    
                    # Execute the appropriate branch
                    if condition_result:
                        for child in node.body:
                            self._process_node(child, structures, index_operations, loop_info, silent=silent)
                    elif node.orelse:
                        for child in node.orelse:
                            self._process_node(child, structures, index_operations, loop_info, silent=silent)
                except Exception as e:
                    self.output.append(f"Runtime Error (Condition): {e}")

            # 3. Loops
            elif isinstance(node, ast.For):
                loop_info["hasLoop"] = True
                if "iterationOutputs" not in loop_info:
                    loop_info["iterationOutputs"] = {}
                
                # 3a. Metadata Gathering (for visualization)
                # Default behavior
                if isinstance(node.target, ast.Name):
                    loop_info["iterator"] = node.target.id
                
                # Check for enumerate(iterable)
                is_enumerate = False
                iterable_obj = []
                if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'enumerate':
                    is_enumerate = True
                    if node.iter.args:
                        # Target structure for visualization is the first arg to enumerate
                        if isinstance(node.iter.args[0], ast.Name):
                            loop_info["target"] = node.iter.args[0].id
                        else:
                            loop_info["target"] = self._get_formula(node.iter.args[0])
                    
                    # Evaluate for execution
                    try:
                        iterable_obj = self._evaluate(node.iter)
                    except Exception as e:
                        self.output.append(f"Runtime Error (enumerate): {e}")
                        iterable_obj = []

                    # If target is tuple (i, num), map num to iterator and i to _index formula
                    if isinstance(node.target, (ast.Tuple, ast.List)) and len(node.target.elts) == 2:
                        if isinstance(node.target.elts[1], ast.Name):
                            loop_info["iterator"] = node.target.elts[1].id
                        if isinstance(node.target.elts[0], ast.Name):
                            index_var = node.target.elts[0].id
                            if not any(d['name'] == index_var for d in loop_info["loopDependencies"]):
                                loop_info["loopDependencies"].append({"name": index_var, "formula": "_index"})

                # Handle range() calls (if not enumerate)
                if not is_enumerate:
                    if isinstance(node.iter, ast.Name):
                        loop_info["target"] = node.iter.id
                        try:
                            iterable_obj = self.context.get(node.iter.id, [])
                        except:
                            iterable_obj = []
                    elif isinstance(node.iter, ast.Call):
                        if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                            try:
                                # Evaluate range arguments
                                args = [self._evaluate(arg) for arg in node.iter.args]
                                range_values = list(range(*args))
                                iterable_obj = range_values
                                
                                # Create a synthetic structure for the range
                                loop_info["target"] = f"range_{loop_info['iterator']}"
                                if not silent:
                                    self._add_or_update(structures, loop_info["target"], 'array', range_values)
                            except Exception as e:
                                self.output.append(f"Runtime Error (range): {e}")
                        else:
                            try:
                                iterable_obj = self._evaluate(node.iter)
                            except:
                                iterable_obj = []
                
                # Check body for dependencies (static analysis for visualization)
                if loop_info["iterator"] and not silent:
                    deps = []
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name):
                                    # Check if value uses the iterator
                                    if self._uses_variable(child.value, loop_info["iterator"]):
                                        formula = self._get_formula(child.value)
                                        deps.append({"name": target.id, "formula": formula})
                                    else:
                                        # Still add it but with evaluated value
                                        try:
                                            evaluated = self._evaluate(child.value)
                                            deps.append({"name": target.id, "formula": str(evaluated)})
                                        except:
                                            formula = self._get_formula(child.value)
                                            deps.append({"name": target.id, "formula": formula})
                    
                    # Merge dependencies, avoid duplicates
                    current_dep_names = {d['name'] for d in loop_info["loopDependencies"]}
                    for dep in deps:
                        if dep['name'] not in current_dep_names:
                            loop_info["loopDependencies"].append(dep)

                # 3b. Silent Interpretation (to capture prints/snapshots per iteration)
                if not silent and iterable_obj:
                    max_iters = min(len(iterable_obj), 100)
                    original_output = list(self.output)
                    if "iterationState" not in loop_info:
                        loop_info["iterationState"] = {}
                    
                    for idx in range(max_iters):
                        val = iterable_obj[idx]
                        
                        # Set loop variables in context
                        if is_enumerate:
                            i_val, num_val = val
                            # Handle tuple target unpacking
                            if isinstance(node.target, (ast.Tuple, ast.List)) and len(node.target.elts) == 2:
                                if isinstance(node.target.elts[0], ast.Name):
                                    self.context[node.target.elts[0].id] = i_val
                                if isinstance(node.target.elts[1], ast.Name):
                                    self.context[node.target.elts[1].id] = num_val
                            elif isinstance(node.target, ast.Name):
                                self.context[node.target.id] = val
                        else:
                            if isinstance(node.target, ast.Name):
                                self.context[node.target.id] = val
                        
                        # Reset output for this iteration
                        self.output = []
                        
                        # Process body silently
                        for child in node.body:
                            self._process_node(child, structures, index_operations, loop_info, silent=True)
                        
                        # Capture iteration output
                        if self.output:
                            loop_info["iterationOutputs"][str(idx)] = list(self.output)
                        
                        # Capture iteration state snapshot (all variables in context)
                        snapshot = {}
                        for name, v in self.context.items():
                            # Format if it's a structure
                            if isinstance(v, list):
                                snapshot[name] = list(v)
                            elif isinstance(v, dict):
                                snapshot[name] = [{"key": str(k), "value": str(v_val)} for k, v_val in v.items()]
                            elif isinstance(v, set):
                                snapshot[name] = list(v)
                            else:
                                snapshot[name] = v
                        loop_info["iterationState"][str(idx)] = snapshot
                    
                    # Restore main output
                    self.output = original_output
            
            elif isinstance(node, ast.While):
                loop_info["hasLoop"] = True
            
            # 4. Subscript Access (e.g., lis[0] or lis[0:2])
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Subscript):
                subscript = node.value
                if isinstance(subscript.value, ast.Name):
                    var_name = subscript.value.id
                    try:
                        indices = self._extract_indices(subscript.slice)
                        if not silent:
                            index_operations.append({
                                "type": "access",
                                "varName": var_name,
                                "indices": indices
                            })
                    except Exception as e:
                        self.output.append(f"Runtime Error (Subscript Access): {e}")
            
            # 5. Method/Function Calls (e.g., arr.append(5) or print(x))
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                
                # Handle print() specifically
                if isinstance(call.func, ast.Name) and call.func.id == 'print':
                    try:
                        # Evaluate all arguments to print()
                        results = [str(self._evaluate(arg)) for arg in call.args]
                        self.output.append(" ".join(results))
                    except Exception as e:
                        self.output.append(f"Print error: {e}")
                    return

                # Handle method mutations (existing logic)
                if isinstance(call.func, ast.Attribute):
                    if isinstance(call.func.value, ast.Name):
                        var_name = call.func.value.id
                        method_name = call.func.attr
                        
                        # Track mutations for list methods
                        if method_name in ['append', 'pop', 'remove', 'insert', 'reverse', 'sort']:
                            try:
                                # Evaluate the method call
                                self._evaluate(call)
                                # Update structures with mutated list
                                if not silent:
                                    if var_name in self.context and isinstance(self.context[var_name], list):
                                        self._add_or_update(structures, var_name, 'array', list(self.context[var_name]))
                            except Exception as e:
                                self.output.append(f"Runtime Error (Method {method_name}): {e}")
        except Exception as top_e:
             self.output.append(f"Unexpected Interpretation Error: {top_e}")


    def _uses_variable(self, node, var_name):
        """Recursively check if a variable is used in the node tree."""
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id == var_name:
                return True
        return False

    def _extract_indices(self, slice_node):
        """Extract indices from a subscript slice node.
        Returns a list of indices (single index returns [idx], slice returns [start, start+1, ..., end-1])
        """
        # Single index: lis[0]
        if isinstance(slice_node, ast.Constant):
            return [slice_node.value]
        elif isinstance(slice_node, ast.Num):  # Python < 3.8
            return [slice_node.n]
        
        # Slice: lis[0:2]
        elif isinstance(slice_node, ast.Slice):
            start = 0
            stop = None
            
            if slice_node.lower:
                start = self._evaluate(slice_node.lower)
            if slice_node.upper:
                stop = self._evaluate(slice_node.upper)
            
            # If stop is None, we can't determine range without knowing array length
            # Return empty for now, frontend will need to handle
            if stop is None:
                return []
            
            return list(range(start, stop))
        
        # Try to evaluate as expression
        try:
            idx = self._evaluate(slice_node)
            return [idx] if isinstance(idx, int) else []
        except:
            return []

    def _get_formula(self, node):
        """Extract source code formula from AST node."""
        if hasattr(ast, 'unparse'):
             return ast.unparse(node)
        return "" # Fallback for older python (shouldn't happen in most envs)

    def _evaluate(self, node):
        """Recursively evaluate AST nodes."""
        # Literals
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num): # Python < 3.8
            return node.n
        elif isinstance(node, ast.Str): # Python < 3.8
            return node.s
        
        # Variables (Look up in context)
        elif isinstance(node, ast.Name):
            if node.id in self.context:
                return self.context[node.id]
            raise NameError(f"Name '{node.id}' is not defined")

        # Containers
        elif isinstance(node, ast.List):
            return [self._evaluate(elt) for elt in node.elts]
        elif isinstance(node, ast.Set):
            return {self._evaluate(elt) for elt in node.elts}
        elif isinstance(node, ast.Dict):
            return {self._evaluate(k): self._evaluate(v) for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.Tuple):
            return tuple(self._evaluate(elt) for elt in node.elts)

        # Operations
        elif isinstance(node, ast.BinOp):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            op = node.op
            
            if isinstance(op, ast.Add): return left + right
            elif isinstance(op, ast.Sub): return left - right
            elif isinstance(op, ast.Mult): return left * right
            elif isinstance(op, ast.Div): return left / right
            elif isinstance(op, ast.FloorDiv): return left // right
            elif isinstance(op, ast.Mod): return left % right
            elif isinstance(op, ast.Pow): return left ** right
            elif isinstance(op, ast.BitXor): return left ^ right # Python uses ^ for XOR
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._evaluate(node.operand)
            op = node.op
            if isinstance(op, ast.USub): return -operand
            elif isinstance(op, ast.UAdd): return +operand
            elif isinstance(op, ast.Not): return not operand
        
        # Comparison Operations (e.g., x < 5, y == 10)
        elif isinstance(node, ast.Compare):
            left = self._evaluate(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._evaluate(comparator)
                if isinstance(op, ast.Lt): result = left < right
                elif isinstance(op, ast.LtE): result = left <= right
                elif isinstance(op, ast.Gt): result = left > right
                elif isinstance(op, ast.GtE): result = left >= right
                elif isinstance(op, ast.Eq): result = left == right
                elif isinstance(op, ast.NotEq): result = left != right
                elif isinstance(op, ast.In): result = left in right
                elif isinstance(op, ast.NotIn): result = left not in right
                else:
                    raise ValueError(f"Unsupported comparison operator: {type(op)}")
                if not result:
                    return False
                left = right  # Chain comparisons (e.g., 1 < x < 10)
            return result
        
        # Boolean Operations (e.g., x and y, a or b)
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._evaluate(val) for val in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._evaluate(val) for val in node.values)
        
        # Function Calls (e.g., len(arr), max(arr))
        elif isinstance(node, ast.Call):
            return self._evaluate_function_call(node)
        
        # Subscript (e.g., lis[0] or lis[0:2])
        elif isinstance(node, ast.Subscript):
            value = self._evaluate(node.value)
            if isinstance(value, (list, tuple, str, dict)):
                # Single index
                if isinstance(node.slice, (ast.Constant, ast.Num)):
                    idx = self._evaluate(node.slice)
                    return value[idx]
                # Slice
                elif isinstance(node.slice, ast.Slice):
                    start = self._evaluate(node.slice.lower) if node.slice.lower else None
                    stop = self._evaluate(node.slice.upper) if node.slice.upper else None
                    step = self._evaluate(node.slice.step) if node.slice.step else None
                    return value[start:stop:step]
                # Expression as index
                else:
                    idx = self._evaluate(node.slice)
                    return value[idx]

        raise ValueError(f"Unsupported node type: {type(node)}")

    def _evaluate_function_call(self, node):
        """Evaluate built-in function calls and method calls."""
        # Built-in functions (e.g., len(arr), max(arr))
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            # Evaluate arguments
            args = [self._evaluate(arg) for arg in node.args]
            
            # Built-in functions
            if func_name == 'len':
                return len(args[0]) if args else 0
            elif func_name == 'max':
                return max(args[0]) if len(args) == 1 and isinstance(args[0], (list, tuple)) else max(args)
            elif func_name == 'min':
                return min(args[0]) if len(args) == 1 and isinstance(args[0], (list, tuple)) else min(args)
            elif func_name == 'sum':
                return sum(args[0]) if args else 0
            elif func_name == 'abs':
                return abs(args[0]) if args else 0
            elif func_name == 'int':
                return int(args[0]) if args else 0
            elif func_name == 'str':
                return str(args[0]) if args else ""
            elif func_name == 'float':
                return float(args[0]) if args else 0.0
            elif func_name == 'range':
                return list(range(*args))
            elif func_name == 'enumerate':
                # enumerate(iterable, start=0)
                iterable = args[0] if args else []
                start = args[1] if len(args) > 1 else 0
                return list(enumerate(iterable, start=start))
            elif func_name == 'sorted':
                return sorted(args[0]) if args else []
            elif func_name == 'reversed':
                return list(reversed(args[0])) if args else []
            else:
                raise ValueError(f"Unsupported function: {func_name}")
        
        # Method calls (e.g., arr.append(5), s.split())
        elif isinstance(node.func, ast.Attribute):
            obj = self._evaluate(node.func.value)
            method_name = node.func.attr
            args = [self._evaluate(arg) for arg in node.args]
            
            # List methods
            if method_name == 'append' and isinstance(obj, list):
                obj.append(args[0] if args else None)
                return obj
            elif method_name == 'pop' and isinstance(obj, list):
                return obj.pop(args[0] if args else -1)
            elif method_name == 'remove' and isinstance(obj, list):
                obj.remove(args[0])
                return obj
            elif method_name == 'insert' and isinstance(obj, list) and len(args) >= 2:
                obj.insert(args[0], args[1])
                return obj
            elif method_name == 'reverse' and isinstance(obj, list):
                obj.reverse()
                return obj
            elif method_name == 'sort' and isinstance(obj, list):
                obj.sort()
                return obj
            
            # String methods
            elif method_name == 'split' and isinstance(obj, str):
                return obj.split(args[0] if args else None)
            elif method_name == 'join' and isinstance(obj, str):
                return obj.join(args[0]) if args else ""
            elif method_name == 'replace' and isinstance(obj, str) and len(args) >= 2:
                return obj.replace(args[0], args[1])
            elif method_name == 'strip' and isinstance(obj, str):
                return obj.strip()
            elif method_name == 'lower' and isinstance(obj, str):
                return obj.lower()
            elif method_name == 'upper' and isinstance(obj, str):
                return obj.upper()
            
            # Dictionary methods
            elif method_name == 'get' and isinstance(obj, dict):
                return obj.get(args[0], args[1] if len(args) > 1 else None)
            elif method_name == 'keys' and isinstance(obj, dict):
                return list(obj.keys())
            elif method_name == 'values' and isinstance(obj, dict):
                return list(obj.values())
            elif method_name == 'items' and isinstance(obj, dict):
                return list(obj.items())
            
            else:
                raise ValueError(f"Unsupported method: {method_name} on {type(obj)}")
        
        raise ValueError(f"Unsupported function call: {ast.unparse(node) if hasattr(ast, 'unparse') else 'unknown'}")

    def _add_or_update(self, structures, name, type_str, data):
        for s in structures:
            if s['name'] == name:
                s['type'] = type_str
                s['data'] = data
                return
        structures.append({"name": name, "type": type_str, "data": data})


def run_tests():
    """
    Comprehensive test suite for the CodeParser.
    Tests all major features including conditionals, built-in functions,
    string operations, and boolean operators.
    """
    parser = CodeParser()
    
    print("=" * 60)
    print("CODEPARSER TEST SUITE")
    print("=" * 60)
    print()
    
    # Test 1: Simple conditional with comparison
    print("=" * 60)
    print("Test 1: Simple Conditional")
    print("=" * 60)
    code1 = """
x = 10
y = 5
if x > y:
    result = "x is greater"
else:
    result = "y is greater"
"""
    result1 = parser.parse(code1)
    print(f"Structures: {result1['structures']}")
    print(f"Expected: x=10, y=5, result='x is greater'")
    
    # Verify
    assert any(s['name'] == 'x' and s['data'] == 10 for s in result1['structures']), "❌ x should be 10"
    assert any(s['name'] == 'y' and s['data'] == 5 for s in result1['structures']), "❌ y should be 5"
    assert any(s['name'] == 'result' and s['data'] == "x is greater" for s in result1['structures']), "❌ result should be 'x is greater'"
    print("✅ PASSED")
    print()
    
    # Test 2: Using len() and max()
    print("=" * 60)
    print("Test 2: Built-in Functions")
    print("=" * 60)
    code2 = """
nums = [1, 5, 3, 9, 2]
length = len(nums)
maximum = max(nums)
total = sum(nums)
"""
    result2 = parser.parse(code2)
    print(f"Structures: {result2['structures']}")
    print(f"Expected: nums=[1,5,3,9,2], length=5, maximum=9, total=20")
    
    # Verify
    assert any(s['name'] == 'nums' and s['data'] == [1, 5, 3, 9, 2] for s in result2['structures']), "❌ nums should be [1,5,3,9,2]"
    assert any(s['name'] == 'length' and s['data'] == 5 for s in result2['structures']), "❌ length should be 5"
    assert any(s['name'] == 'maximum' and s['data'] == 9 for s in result2['structures']), "❌ maximum should be 9"
    assert any(s['name'] == 'total' and s['data'] == 20 for s in result2['structures']), "❌ total should be 20"
    print("✅ PASSED")
    print()
    
    # Test 3: FizzBuzz (conditionals + loops)
    print("=" * 60)
    print("Test 3: FizzBuzz (Loop Detection)")
    print("=" * 60)
    code3 = """
result = []
for i in range(1, 6):
    if i % 3 == 0 and i % 5 == 0:
        result.append("FizzBuzz")
    elif i % 3 == 0:
        result.append("Fizz")
    elif i % 5 == 0:
        result.append("Buzz")
"""
    result3 = parser.parse(code3)
    print(f"Structures: {result3['structures']}")
    print(f"Has Loop: {result3['hasLoop']}")
    print(f"Expected: result=[], hasLoop=True")
    
    # Verify
    assert result3['hasLoop'] == True, "❌ Should detect loop"
    assert any(s['name'] == 'result' for s in result3['structures']), "❌ result should exist"
    print("✅ PASSED")
    print()
    
    # Test 4: String operations
    print("=" * 60)
    print("Test 4: String Operations")
    print("=" * 60)
    code4 = """
s = "hello world"
words = s.split()
upper_s = s.upper()
"""
    result4 = parser.parse(code4)
    print(f"Structures: {result4['structures']}")
    print(f"Expected: s='hello world', words=['hello', 'world'], upper_s='HELLO WORLD'")
    
    # Verify
    assert any(s['name'] == 's' and s['data'] == "hello world" for s in result4['structures']), "❌ s should be 'hello world'"
    assert any(s['name'] == 'words' and s['data'] == ['hello', 'world'] for s in result4['structures']), "❌ words should be ['hello', 'world']"
    assert any(s['name'] == 'upper_s' and s['data'] == 'HELLO WORLD' for s in result4['structures']), "❌ upper_s should be 'HELLO WORLD'"
    print("✅ PASSED")
    print()
    
    # Test 5: Nested conditionals
    print("=" * 60)
    print("Test 5: Nested Conditionals (elif chains)")
    print("=" * 60)
    code5 = """
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"
"""
    result5 = parser.parse(code5)
    print(f"Structures: {result5['structures']}")
    print(f"Expected: score=85, grade='B'")
    
    # Verify
    assert any(s['name'] == 'score' and s['data'] == 85 for s in result5['structures']), "❌ score should be 85"
    assert any(s['name'] == 'grade' and s['data'] == 'B' for s in result5['structures']), "❌ grade should be 'B'"
    print("✅ PASSED")
    print()
    
    # Test 6: Boolean operators
    print("=" * 60)
    print("Test 6: Boolean Operators")
    print("=" * 60)
    code6 = """
x = 5
y = 10
z = 15
result1 = x < y and y < z
result2 = x > y or y < z
result3 = not (x > y)
"""
    result6 = parser.parse(code6)
    print(f"Structures: {result6['structures']}")
    print(f"Expected: x=5, y=10, z=15, result1=True, result2=True, result3=True")
    
    # Verify
    assert any(s['name'] == 'x' and s['data'] == 5 for s in result6['structures']), "❌ x should be 5"
    assert any(s['name'] == 'y' and s['data'] == 10 for s in result6['structures']), "❌ y should be 10"
    assert any(s['name'] == 'z' and s['data'] == 15 for s in result6['structures']), "❌ z should be 15"
    assert any(s['name'] == 'result1' and s['data'] == True for s in result6['structures']), "❌ result1 should be True"
    assert any(s['name'] == 'result2' and s['data'] == True for s in result6['structures']), "❌ result2 should be True"
    assert any(s['name'] == 'result3' and s['data'] == True for s in result6['structures']), "❌ result3 should be True"
    print("✅ PASSED")
    print()
    
    print("=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)
    print()
    print("Summary:")
    print("  ✅ Conditional statements (if/elif/else)")
    print("  ✅ Comparison operators (<, >, ==, etc.)")
    print("  ✅ Boolean operators (and, or, not)")
    print("  ✅ Built-in functions (len, max, sum)")
    print("  ✅ String methods (split, upper)")
    print("  ✅ Loop detection")
    print()


if __name__ == "__main__":
    # Run tests when the module is executed directly
    run_tests()

