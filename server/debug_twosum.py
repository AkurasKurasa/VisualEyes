from code_parser import CodeParser
import json

def test_twosum():
    parser = CodeParser()
    code = """
pair_idx = {}
nums = [2, 7, 11, 15]
target = 9

for i, num in enumerate(nums):
    if target - num in pair_idx:
        print(i, pair_idx[target - num])
    pair_idx[num] = i
"""
    result = parser.parse(code)
    
    print("Structures:", json.dumps(result['structures'], indent=2))
    print("Output:", result['output'])
    print("Iteration Outputs:", json.dumps(result.get('iterationOutputs', {}), indent=2))
    
    # Check if iteration 1 has output
    iter_outputs = result.get('iterationOutputs', {})
    if "1" in iter_outputs:
        print("✅ Found output in iteration 1:", iter_outputs["1"])
    else:
        print("❌ Output missing in iteration 1")

    # Check if pair_idx is growing
    iter_state = result.get('iterationState', {})
    if "0" in iter_state:
        print("Iteration 0 pair_idx:", iter_state["0"].get("pair_idx"))
    if "1" in iter_state:
        print("Iteration 1 pair_idx:", iter_state["1"].get("pair_idx"))

if __name__ == "__main__":
    test_twosum()
