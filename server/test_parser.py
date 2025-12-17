from parser import CodeParser
import json

code = """
x = 10
y = x * 2 + 5
z = (y / 5) + 1
arr = [1, 1+1, 3*3]
"""

parser = CodeParser()
result = parser.parse(code)
print(json.dumps(result, indent=2))
