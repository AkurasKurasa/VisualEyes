from code_parser import CodeParser

parser = CodeParser()
code = """pair_idx = {}
nums = [2, 7, 11, 15]
target = 9

for i, num in enumerate(nums):
    if target - num in pair_idx:
        print(i, pair_idx[target - num])
    pair_idx[num] = i
"""

result = parser.parse(code)

print("ITERATION OUTPUTS:")
print(result.get('iterationOutputs'))

print("\nITERATION 1 OUTPUT:")
outputs = result.get('iterationOutputs', {})
if '1' in outputs:
    print(f"Found: {outputs['1']}")
else:
    print("NOT FOUND")

print("\nITERATION 1 STATE:")
states = result.get('iterationState', {})
if '1' in states:
    state = states['1']
    print(f"pair_idx: {state.get('pair_idx')}")
    print(f"i: {state.get('i')}")
    print(f"num: {state.get('num')}")
else:
    print("NOT FOUND")
