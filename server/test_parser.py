from code_parser import CodeParser
import json

def test_parser():
    parser = CodeParser()
    
    # Test 1: Simple conditional with comparison
    print("=" * 50)
    print("Test 1: Simple Conditional")
    print("=" * 50)
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
    print()
    
    # Test 2: Built-in Functions
    print("=" * 50)
    print("Test 2: Built-in Functions")
    print("=" * 50)
    code2 = """
nums = [1, 5, 3, 9, 2]
length = len(nums)
maximum = max(nums)
total = sum(nums)
"""
    result2 = parser.parse(code2)
    print(f"Structures: {result2['structures']}")
    print(f"Expected: nums=[1,5,3,9,2], length=5, maximum=9, total=20")
    print()
    
    # Test 3: FizzBuzz (conditionals + loops + list methods)
    print("=" * 50)
    print("Test 3: FizzBuzz")
    print("=" * 50)
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
    print(f"Expected: result=[] (loop not executed in parse), hasLoop=True")
    print()
    
    # Test 4: String operations
    print("=" * 50)
    print("Test 4: String Operations")
    print("=" * 50)
    code4 = """
s = "hello world"
words = s.split()
upper_s = s.upper()
"""
    result4 = parser.parse(code4)
    print(f"Structures: {result4['structures']}")
    print(f"Expected: s='hello world', words=['hello', 'world'], upper_s='HELLO WORLD'")
    print()
    
    # Test 5: Nested conditionals
    print("=" * 50)
    print("Test 5: Nested Conditionals")
    print("=" * 50)
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
    print()
    
    # Test 6: Boolean operators
    print("=" * 50)
    print("Test 6: Boolean Operators")
    print("=" * 50)
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
    print()

if __name__ == "__main__":
    test_parser()
