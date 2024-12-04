from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/alerts', methods=['POST'])
def create_alert():
    data = request.json
    print("Received alert in Alert Service:", data)
    # Simulated response for testing
    return jsonify({"status": "Alert received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084)
