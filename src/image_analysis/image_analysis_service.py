from flask import Flask, request, jsonify
import json
import sys

app = Flask(__name__)

@app.route('/frame', methods=['POST'])
def analyze_image():
    frame_data = request.get_json()
    print(f"✅ Image Analysis Service received data:\n{json.dumps(frame_data, indent=2)}", flush=True)

    # Simulate processing
    response_data = {"persons": [{"age": "25-30", "gender": "male"}]}
    print(f"✅ Processed result: {json.dumps(response_data, indent=2)}", flush=True)

    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
