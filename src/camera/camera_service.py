from flask import Flask, request, jsonify
import requests
import time
import threading
import base64
import json
import sys
import uuid

app = Flask(__name__)

streaming = False  # Global variable to control streaming

@app.route('/')
def home():
    return jsonify({"message": "Camera Service Running"}), 200

def generate_fake_frame():
    """Generates a placeholder frame (simulating camera data)."""
    return base64.b64encode(b"fake_image_data").decode()

def capture_and_send(destination, max_frames, delay):
    """Simulates capturing frames and sends them to the Collector Service."""
    global streaming

    frame_count = 0
    while streaming and frame_count < max_frames:
        frame_data = {
            "image": generate_fake_frame(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "section": 1,
            "event": "entry",
            "frame_uuid": str(uuid.uuid4())
        }

        try:
            print(
                f"📤 [Camera Service] Sending frame {frame_count + 1} to {destination}:\n{json.dumps(frame_data, indent=2)}",
                flush=True)
            response = requests.post(destination, json=frame_data, headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            print(f"✅ [Camera Service] Frame {frame_count + 1} Sent: {response.status_code}", flush=True)
        except requests.exceptions.RequestException as e:
            print(f"❌ [Camera Service] Error sending frame: {e}", flush=True)

        frame_count += 1
        time.sleep(delay)

    streaming = False  # Ensure streaming stops after max-frames is reached

@app.route('/stream', methods=['POST'])
def start_stream():
    """API to start or stop the camera stream based on toggle value."""
    global streaming

    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid or empty JSON payload"}), 400

        print(f"✅ [Camera Service] Received JSON Data:\n{json.dumps(data, indent=2)}", flush=True)

        destination = data.get("destination")
        max_frames = data.get("max-frames", 1)
        delay = data.get("delay", 0.5)

        if not destination:
            return jsonify({"error": "Missing 'destination' field"}), 400

        try:
            max_frames = int(max_frames)
            delay = float(delay)
        except ValueError:
            return jsonify({"error": "Invalid data types for 'max-frames' or 'delay'"}), 400

        toggle = request.args.get("toggle", "off").lower()

        if toggle == "on":
            if not streaming:  # Prevent duplicate streams
                streaming = True
                threading.Thread(target=capture_and_send, args=(destination, max_frames, delay), daemon=True).start()
                return jsonify({"message": "Camera streaming started"}), 200
            return jsonify({"message": "Camera already streaming"}), 200

        else:
            streaming = False
            return jsonify({"message": "Camera streaming stopped"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process JSON: {str(e)}"}), 400

@app.route('/status', methods=['GET'])
def status():
    """Check if the camera service is running."""
    return jsonify({"camera_streaming": streaming}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
