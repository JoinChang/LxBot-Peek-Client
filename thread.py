import io
import subprocess

from PyQt5.QtCore import QThread

from PIL import ImageGrab, ImageFilter, ImageEnhance
from flask import Flask, send_file, abort

from config import Config

config = Config()

app = Flask(__name__)

@app.route('/peek')
def peek():
    if int(config.get("client", "status", 0)) == 0:
        return abort(403)
    pic = ImageGrab.grab().convert("RGB")
    pic = pic.filter(ImageFilter.GaussianBlur(int(config.get("screenshot", "vague", 6))))
    enhance_brightness = ImageEnhance.Brightness(pic)
    pic = enhance_brightness.enhance(int(config.get("screenshot", "brightness", 10)) / 10)

    pic_bytes = io.BytesIO()
    pic.save(pic_bytes, format='JPEG')
    pic_bytes.seek(0, 0)
    return send_file(pic_bytes, mimetype='image/jpg')

class WorkThreadFlask(QThread):
    def __int__(self):
        super(WorkThreadFlask, self).__init__()

    def run(self):
        app.run(host=config.get("client", "host", "0.0.0.0"), port=int(config.get("client", "port", 12345)), debug=True, use_reloader=False)

class WorkThreadFrp(QThread):
    def __int__(self):
        super(WorkThreadFrp, self).__init__()

    def run(self):
        subprocess.call("frpc.exe", creationflags=subprocess.CREATE_NO_WINDOW)