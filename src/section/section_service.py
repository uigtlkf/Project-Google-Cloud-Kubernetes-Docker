from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/persons', methods=['POST'])
def log_persons():
    data = request.json
    print("Received data in Section Service:", data)
    # Simulated response for testing
    return jsonify({"status": "Logged"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)
