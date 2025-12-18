"""
Comprehensive line-by-line execution test for Two Sum
"""
from code_parser import CodeParser
import json

def test_twosum_detailed():
    print("="*80)
    print("DETAILED TWO SUM EXECUTION TEST")
    print("="*80)
    
    parser = CodeParser()
    code = """pair_idx = {}
nums = [2, 7, 11, 15]
target = 9

for i, num in enumerate(nums):
    if target - num in pair_idx:
        print(i, pair_idx[target - num])
    pair_idx[num] = i
"""
    
    print("\n📝 CODE TO EXECUTE:")
    print(code)
    print("\n" + "="*80)
    
    result = parser.parse(code)
    
    print("\n✅ PARSING COMPLETED")
    print("\n" + "="*80)
    print("📊 STRUCTURES:")
    print(json.dumps(result['structures'], indent=2))
    
    print("\n" + "="*80)
    print("🔄 LOOP INFO:")
    print(f"  hasLoop: {result.get('hasLoop')}")
    print(f"  target: {result.get('target')}")
    print(f"  iterator: {result.get('iterator')}")
    print(f"  loopDependencies: {result.get('loopDependencies')}")
    
    print("\n" + "="*80)
    print("📤 MAIN OUTPUT:")
    print(f"  {result['output']}")
    
    print("\n" + "="*80)
    print("🔁 ITERATION OUTPUTS:")
    iter_outputs = result.get('iterationOutputs', {})
    if iter_outputs:
        for key, value in sorted(iter_outputs.items()):
            print(f"  Iteration {key}: {value}")
    else:
        print("  ❌ NO ITERATION OUTPUTS FOUND")
    
    print("\n" + "="*80)
    print("💾 ITERATION STATE SNAPSHOTS:")
    iter_state = result.get('iterationState', {})
    if iter_state:
        for key in sorted(iter_state.keys()):
            state = iter_state[key]
            print(f"\n  === Iteration {key} ===")
            print(f"    i: {state.get('i')}")
            print(f"    num: {state.get('num')}")
            print(f"    pair_idx: {state.get('pair_idx')}")
            print(f"    target: {state.get('target')}")
    else:
        print("  ❌ NO ITERATION STATES FOUND")
    
    print("\n" + "="*80)
    print("🎯 VERIFICATION:")
    
    # Check iteration 1 specifically
    if "1" in iter_outputs:
        print(f"  ✅ Iteration 1 has output: {iter_outputs['1']}")
    else:
        print(f"  ❌ Iteration 1 has NO output")
        
    if "1" in iter_state:
        print(f"  ✅ Iteration 1 state exists")
        print(f"     pair_idx at iteration 1: {iter_state['1'].get('pair_idx')}")
    else:
        print(f"  ❌ Iteration 1 state missing")
    
    print("\n" + "="*80)
    print("🧪 MANUAL SIMULATION:")
    print("  Let's manually trace iteration 1:")
    print("    i = 1, num = 7")
    print("    target - num = 9 - 7 = 2")
    print("    pair_idx at iter 0 should have: {2: 0}")
    print("    Is 2 in pair_idx? Should be YES")
    print("    So print(1, pair_idx[2]) should execute")
    print("    Expected output: '1 0'")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_twosum_detailed()
