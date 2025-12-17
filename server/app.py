from flask import Flask, request, jsonify
from flask_cors import CORS
from code_parser import CodeParser

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
