from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

print("Current Directory:", os.getcwd())
print("Files in Dir:", os.listdir(os.getcwd()))
print("Sys Path:", sys.path)

try:
    from code_parser import CodeParser
except ImportError as e:
    print(f"Import Error: {e}")
    # Fallback to prevent crash so /api/health still works
    class CodeParser:
        def parse(self, code):
            return {"structures": [], "error": "Parser module failed to load"}

app = Flask(__name__)
CORS(app) # Enable CORS for frontend communication

parser = CodeParser()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/api/parse', methods=['POST'])
def parse_code():
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({"structures": [], "hasLoop": False})

    try:
        result = parser.parse(code)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
