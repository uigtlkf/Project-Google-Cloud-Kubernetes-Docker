from flask import Flask, request, jsonify
import json
import sys

app = Flask(__name__)

@app.route('/alerts', methods=['POST'])
def create_alert():
    """Logs received JSON and returns a mock response."""

    data = request.get_json(silent=True)

    if data is None:
        print("❌ [Alert Service] Error: Invalid JSON received.", flush=True)
        return jsonify({"error": "Invalid JSON received"}), 400

    print(f"✅ [Alert Service] Received Data:\n{json.dumps(data, indent=2)}", flush=True)

    # Simulated response for testing
    response = {"status": "Alert received"}
    print(f"✅ [Alert Service] Response: {json.dumps(response, indent=2)}", flush=True)

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
