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
    question = data.get('question', '')
    response = query(question)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)