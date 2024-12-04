from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/frame', methods=['POST'])
def recognize_face():
    data = request.json
    print("Received data in Face Recognition:", data)
    # Simulate response data for testing
    return jsonify({"known-persons": [{"name": "John Doe"}]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
