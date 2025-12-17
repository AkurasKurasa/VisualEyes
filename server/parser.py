import ast
import operator

class CodeParser:
    def __init__(self):
        self.context = {} # Symbol table for variable resolution

    def parse(self, code):
        structures = []
        self.context = {} # Reset context on each parse
        loop_info = {
            "hasLoop": False,
            "target": None,
            "iterator": None,
            "loopDependencies": []
        }

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"structures": [], "error": f"Syntax Error: {e}"}

        # Iterate over top-level nodes in order to respect variable dependencies
        for node in tree.body:
            # 1. Assignments
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
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
                            data = evaluated_value
                        elif isinstance(evaluated_value, set):
                            type_str = 'set'
                            data = list(evaluated_value)
                        elif isinstance(evaluated_value, dict):
                            type_str = 'dictionary'
                            # Format for frontend: [{"key": k, "value": v}]
                            data = [{"key": str(k), "value": str(v)} for k, v in evaluated_value.items()]
                        elif isinstance(evaluated_value, (int, float, str)):
                            type_str = 'variable'
                            data = evaluated_value
                        
                        # Update context for future references
                        if data is not None:
                            # For context, we store raw python objects
                            self.context[var_name] = evaluated_value
                            # For frontend, we add to structures
                            self._add_or_update(structures, var_name, type_str, data)

                    except Exception as e:
                        # If evaluation triggers error (e.g. unknown var), ignore or log
                        print(f"Evaluation error for {var_name}: {e}")
                        pass

            # 2. Loops
            elif isinstance(node, ast.For):
                loop_info["hasLoop"] = True
                if isinstance(node.target, ast.Name):
                    loop_info["iterator"] = node.target.id
                    # Mock iterator in context for loop body analysis? 
                    # For now, we leave it, or set to safely inspect.
                if isinstance(node.iter, ast.Name):
                    loop_info["target"] = node.iter.id
                
                # Check body for assignments dependent on the iterator
                if loop_info["iterator"]:
                    deps = []
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                             # Check if value uses the iterator
                             if self._uses_variable(child.value, loop_info["iterator"]):
                                 formula = self._get_formula(child.value)
                                 for target in child.targets:
                                     if isinstance(target, ast.Name):
                                         deps.append({"name": target.id, "formula": formula})
                    loop_info["loopDependencies"] = deps
            
            elif isinstance(node, ast.While):
                loop_info["hasLoop"] = True

        # Ensure loop iterator exists in structures
        if loop_info["iterator"] and not any(s['name'] == loop_info["iterator"] for s in structures):
             structures.append({"name": loop_info["iterator"], "type": "variable", "data": "?"})

        return {
            "structures": structures,
            **loop_info
        }

    def _uses_variable(self, node, var_name):
        """Recursively check if a variable is used in the node tree."""
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id == var_name:
                return True
        return False

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

        raise ValueError(f"Unsupported node type: {type(node)}")

    def _add_or_update(self, structures, name, type_str, data):
        for s in structures:
            if s['name'] == name:
                s['type'] = type_str
                s['data'] = data
                return
        structures.append({"name": name, "type": type_str, "data": data})
