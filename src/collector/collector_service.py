from flask import Flask, request, jsonify
import requests
import json
import sys

app = Flask(__name__)

IMAGE_ANALYSIS_URL = 'http://image-analysis-service.default.svc.cluster.local/frame'
FACE_RECOGNITION_URL = 'http://face-recognition-service.default.svc.cluster.local/frame'
SECTION_URL = 'http://section-service.default.svc.cluster.local/persons'
ALERT_URL = 'http://alert-service.default.svc.cluster.local/alerts'
CAMERA_SERVICE_URL = 'http://camera-service.default.svc.cluster.local/stream'


@app.route('/')
def home():
    return jsonify({"message": "Collector Service Running"}), 200


@app.route('/collector', methods=['GET'])
def collector_health():
    return jsonify({"message": "Collector Service Running"}), 200


@app.route('/start-camera', methods=['POST'])
def start_camera_stream():
    """Request the Camera Service to start streaming frames to the Collector."""
    try:
        data = {
            "destination": "http://collector-service.default.svc.cluster.local/frame",
            "max-frames": 1,
            "delay": 0.5
        }
        print(f"📤 [Collector] Sending request to start camera stream:\n{json.dumps(data, indent=2)}", flush=True)

        # Explicitly setting the toggle=on
        response = requests.post(CAMERA_SERVICE_URL + "?toggle=on", json=data)
        response.raise_for_status()

        print(f"✅ [Collector] Camera streaming started: {response.json()}", flush=True)
        return jsonify({"status": "Camera stream requested"}), 200

    except requests.exceptions.RequestException as e:
        print(f"❌ [Collector] Failed to start camera stream: {e}", flush=True)
        return jsonify({"error": "Failed to start camera stream", "details": str(e)}), 500


@app.route('/frame', methods=['POST'])
def receive_frame():
    frame_data = request.get_json(force=True)
    print(f"✅ Received Frame Data: {json.dumps(frame_data, indent=2)}")
    sys.stdout.flush()

    # Validate required fields
    required_fields = ["timestamp", "image", "section", "event", "frame_uuid"]
    missing_fields = [field for field in required_fields if field not in frame_data]

    if missing_fields:
        print(f"❌ [Collector] Missing required fields: {missing_fields}", flush=True)
        return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
    # Send frame data to Image Analysis Service
    try:
        print("📤 Sending to Image Analysis...")
        sys.stdout.flush()
        analysis_response = requests.post(IMAGE_ANALYSIS_URL, json=frame_data)
        analysis_response.raise_for_status()
        analysis_data = analysis_response.json()
        print(f"✅ Image Analysis Response: {json.dumps(analysis_data, indent=2)}")
        sys.stdout.flush()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending to Image Analysis: {e}")
        sys.stdout.flush()
        return jsonify({"error": "Image Analysis Service is unavailable", "details": str(e)}), 500

    # Send frame data to Face Recognition Service
    try:
        print("📤 Sending to Face Recognition...")
        sys.stdout.flush()
        face_rec_response = requests.post(FACE_RECOGNITION_URL, json=frame_data)
        face_rec_response.raise_for_status()
        face_data = face_rec_response.json()
        print(f"✅ Face Recognition Response: {json.dumps(face_data, indent=2)}")
        sys.stdout.flush()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending to Face Recognition: {e}")
        sys.stdout.flush()
        return jsonify({"error": "Face Recognition Service is unavailable", "details": str(e)}), 500

    # Forward results to Section Service for statistics
    section_data = {
        "timestamp": frame_data["timestamp"],
        "section": frame_data["section"],
        "event": frame_data["event"],
        "persons": analysis_data.get("persons", [])
    }
    try:
        print("📤 Sending to Section Service...")
        sys.stdout.flush()
        section_response = requests.post(SECTION_URL, json=section_data)
        section_response.raise_for_status()
        print(f"✅ Section Service Response: {json.dumps(section_response.json(), indent=2)}")
        sys.stdout.flush()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending to Section Service: {e}")
        sys.stdout.flush()
        return jsonify({"error": "Section Service is unavailable", "details": str(e)}), 500

    # If persons of interest were detected, forward to Alert Service
    if "known-persons" in face_data and face_data["known-persons"]:
        alert_data = {
            "timestamp": frame_data["timestamp"],
            "section": frame_data["section"],
            "event": frame_data["event"],
            "known-persons": face_data["known-persons"]
        }
        try:
            print("📤 Sending to Alert Service...")
            sys.stdout.flush()
            alert_response = requests.post(ALERT_URL, json=alert_data)
            alert_response.raise_for_status()
            print(f"✅ Alert Service Response: {json.dumps(alert_response.json(), indent=2)}")
            sys.stdout.flush()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending to Alert Service: {e}")
            sys.stdout.flush()
            return jsonify({"error": "Alert Service is unavailable", "details": str(e)}), 500

    return jsonify({"status": "Frame processed"}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

