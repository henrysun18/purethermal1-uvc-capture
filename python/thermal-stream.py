#!/usr/bin/env python

"""
CV2 video capture example from Pure Thermal 1
"""

try:
    import cv2
    from flask import Flask, render_template, Response
except ImportError:
    print("ERROR python-opencv must be installed")
    exit(1)


app = Flask(__name__)
@app.route('/')
def index():
    """GordonBot Thermal Video Feed"""
    return render_template('thermal-video-stream.html')
@app.route('/video_feed')
def video_feed():
    """put this in the src attribute of an img tag in the html"""
    return Response(OpenCvCapture().show_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

name = "GordonBot Thermal Video Feed"
class OpenCvCapture(object):
    """
    Encapsulate state for capture from Pure Thermal 1 with OpenCV
    """

    def __init__(self):
        # capture from the LAST camera in the system
        # presumably, if the system has a built-in webcam it will be the first
        cv2_cap = cv2.VideoCapture(0)

        if not cv2_cap.isOpened():
            print("Camera not found!")
            exit(1)

        self.cv2_cap = cv2_cap

    def get_frame(self, img):
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def show_video(self):
        """
        Run loop for cv2 capture from lepton
        """
        print("Running, ESC or Ctrl-c to exit...")
        while True:
            ret, img = self.cv2_cap.read()
#            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img)
            frame = self.get_frame(img)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run(host='192.168.43.76', port=9000, debug=True, threaded=True)
