from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

IMAGE_ANALYSIS_URL = 'http://image-analysis-service:8081/frame'
FACE_RECOGNITION_URL = 'http://face-recognition-service:8082/frame'
SECTION_URL = 'http://section-service:8083/persons'
ALERT_URL = 'http://alert-service:8084/alerts'


@app.route('/frame', methods=['POST'])
def receive_frame():
    frame_data = request.json
    print("Received frame data:", frame_data)  

    # Send frame data to ImageAnalysis service
    try:
        analysis_response = requests.post(IMAGE_ANALYSIS_URL, json=frame_data)
        analysis_response.raise_for_status()
        analysis_data = analysis_response.json()
        print("Image Analysis Service response:", analysis_data)
    except requests.exceptions.RequestException as e:
        print("Error communicating with Image Analysis Service:", e)
        return jsonify({"error": "Image Analysis Service is unavailable", "details": str(e)}), 500

    # Send frame data to FaceRecognition service
    try:
        face_rec_response = requests.post(FACE_RECOGNITION_URL, json=frame_data)
        face_rec_response.raise_for_status()
        face_data = face_rec_response.json()
        print("Face Recognition Service response:", face_data)
    except requests.exceptions.RequestException as e:
        print("Error communicating with Face Recognition Service:", e)
        return jsonify({"error": "Face Recognition Service is unavailable", "details": str(e)}), 500

    # Forward results to Section service for statistics
    try:
        section_data = {
            "timestamp": frame_data["timestamp"],
            "section": frame_data["section"],
            "event": frame_data["event"],
            "persons": analysis_data.get("persons", [])
        }
        section_response = requests.post(SECTION_URL, json=section_data)
        section_response.raise_for_status()
        print("Section Service response:", section_response.json())
    except requests.exceptions.RequestException as e:
        print("Error communicating with Section Service:", e)
        return jsonify({"error": "Section Service is unavailable", "details": str(e)}), 500

    # If persons of interest were detected, forward to Alert service
    if "known-persons" in face_data and face_data["known-persons"]:
        alert_data = {
            "timestamp": frame_data["timestamp"],
            "section": frame_data["section"],
            "event": frame_data["event"],
            "known-persons": face_data["known-persons"]
        }
        try:
            alert_response = requests.post(ALERT_URL, json=alert_data)
            alert_response.raise_for_status()
            print("Alert Service response:", alert_response.json())
        except requests.exceptions.RequestException as e:
            print("Error communicating with Alert Service:", e)
            return jsonify({"error": "Alert Service is unavailable", "details": str(e)}), 500

    return jsonify({"status": "Frame processed"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

