from flask import Flask, render_template, Response
import os
import logging
from cv2 import imencode
import time

os.environ['FLASK_DEBUG'] = 'development'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class WebDisplay():

    app = Flask(__name__)
    vilib = None

    def __init__(self, vilib):
        WebDisplay.vilib = vilib

    @app.route('/')
    def index():
        """Video streaming home page."""
        return render_template('index.html')

    def get_frame():
        return imencode('.jpg', WebDisplay.vilib.img)[1].tobytes()

    def get_qrcode_pictrue():
        return imencode('.jpg', WebDisplay.vilib.img)[1].tobytes()

    def get_png_frame():
        return imencode('.png', WebDisplay.vilib.img)[1].tobytes()

    def get_qrcode():
        while WebDisplay.vilib.qrcode_img_encode is None:
            time.sleep(0.2)

        return WebDisplay.vilib.qrcode_img_encode

    def gen():
        """Video streaming generator function."""
        while True:  
            # start_time = time.time()
            frame = WebDisplay.get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.03)
            # end_time = time.time() - start_time
            # print('flask fps:%s'%int(1/end_time))

    @app.route('/mjpg') ## video
    def video_feed():
        # from camera import Camera
        """Video streaming route. Put this in the src attribute of an img tag."""
        if WebDisplay.vilib.web_display_flag:
            response = Response(WebDisplay.gen(),
                            mimetype='multipart/x-mixed-replace; boundary=frame') 
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        else:
            tip = '''
        Please enable web display first:
            Vilib.display(web=True)
    '''
            html = f"<html><style>p{{white-space: pre-wrap;}}</style><body><p>{tip}</p></body></html>"
            return Response(html, mimetype='text/html')

    @app.route('/mjpg.jpg')  # jpg
    def video_feed_jpg():
        # from camera import Camera
        """Video streaming route. Put this in the src attribute of an img tag."""
        response = Response(WebDisplay.get_frame(), mimetype="image/jpeg")
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    @app.route('/mjpg.png')  # png
    def video_feed_png():
        # from camera import Camera
        """Video streaming route. Put this in the src attribute of an img tag."""
        response = Response(WebDisplay.get_png_frame(), mimetype="image/png")
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    @app.route("/qrcode")
    def qrcode_feed():
        qrcode_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>QRcode</title>
        <script>
            function refreshQRCode() {
                var imgElement = document.getElementById('qrcode-img');
                imgElement.src = '/qrcode.png?' + new Date().getTime();  // Add timestamp to avoid caching
            }
            var refreshInterval = 500;  // 2s

            window.onload = function() {
                refreshQRCode(); 
                setInterval(refreshQRCode, refreshInterval);
            };
        </script>
    </head>
    <body>
        <img id="qrcode-img" src="/qrcode.png" alt="QR Code" />
    </body>
    </html>
    '''
        return Response(qrcode_html, mimetype='text/html')

    @classmethod
    @app.route("/qrcode.png")
    def qrcode_feed_png():
        """Video streaming route. Put this in the src attribute of an img tag."""
        if WebDisplay.vilib.web_qrcode_flag:
            # response = Response(get_qrcode(),
            #                 mimetype='multipart/x-mixed-replace; boundary=frame')
            response = Response(WebDisplay.get_qrcode(), mimetype="image/png")
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        else:
            tip = '''
        Please enable web display first:
            Vilib.display_qrcode(web=True)
    '''
            html = f"<html><style>p{{white-space: pre-wrap;}}</style><body><p>{tip}</p></body></html>"
            return Response(html, mimetype='text/html')

    def web_camera_start(self):
        try:
            WebDisplay.app.run(host='0.0.0.0', port=9000, threaded=True, debug=False)
        except Exception as e:
            print(e)
