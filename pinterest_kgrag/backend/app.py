#
# app.py
#   Bill Xia
#   April 19, 2025
#
# Purpose: Runs the Flask server that powers the program's backend.
#

# Imports.
from flask import Flask, request, jsonify
from flask_cors import CORS
from query import query

app = Flask(__name__)
CORS(app)

@app.route('/api/query', methods=['POST'])
def handle_query():
    data     = request.get_json()
    print(f"Received query: {data}")
    result, db_data = query(data)
    print("response & db_response1: ", result)
    print("response & db_response2: ", db_data)
    return jsonify({'response': result, 'db_data': db_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')