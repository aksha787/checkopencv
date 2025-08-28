import cv2
import time
from flask import Flask, Response

app = Flask(__name__)
camera = cv2.VideoCapture(0)
# camera = cv2.VideoCapture(0, cv2.CAP_V4L2) # Try this if default fails, or GStreamer pipeline

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

# It's crucial to set a lower resolution for Pi Zero performance
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            print("Failed to read frame from camera.")
            break
        else:
            # You can add your OpenCV processing/detection here
            # Example: Convert to grayscale for a quick visual check
            # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # ret, buffer = cv2.imencode('.jpg', gray_frame) # Encode grayscale

            ret, buffer = cv2.imencode('.jpg', frame) # Encode original frame
            if not ret:
                print("Failed to encode frame.")
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Pi Zero Camera Stream</title>
        </head>
        <body>
            <h1>Live Camera Stream</h1>
            <img src="/video_feed" width="640" height="480" />
        </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting Flask web server on port 5000...")
    print("Access the stream from your desktop browser at http://<your_pi_ip_address>:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
    # Release camera when Flask app stops (e.g., with Ctrl+C)
    camera.release()
