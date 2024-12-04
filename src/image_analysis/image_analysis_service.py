from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/frame', methods=['POST'])
def analyze_image():
    data = request.json
    print("Received data in Image Analysis:", data)
    # Mock response for testing
    return jsonify({"persons": [{"age": "25-30", "gender": "male"}]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
