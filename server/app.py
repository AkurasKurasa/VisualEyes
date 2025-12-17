from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import CodeParser

app = Flask(__name__)
CORS(app) # Enable CORS for frontend communication

parser = CodeParser()

@app.route('/parse', methods=['POST'])
def parse_code():
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({"structures": [], "hasLoop": False})

    result = parser.parse(code)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
