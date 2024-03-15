#!/usr/bin/env python3

# whther print welcome message
import os
import logging

from .version import __version__
if 'VILIB_WELCOME' not in os.environ or os.environ['VILIB_WELCOME'] not in [
        'False', '0'
]:
    from pkg_resources import require
    picamera2_version = require('picamera2')[0].version
    print(f'vilib {__version__} launching ...')
    print(f'picamera2 {picamera2_version}')

# set libcamera2 log level
os.environ['LIBCAMERA_LOG_LEVELS'] = '*:ERROR'

import time
import datetime

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2
import libcamera

import tflite_runtime.interpreter as tflite
from pyzbar import pyzbar

import threading
from multiprocessing import Process, Manager

from flask import Flask, render_template, Response

# user and user home directory
user = os.popen(
    "echo ${SUDO_USER:-$(who -m | awk '{ print $1 }')}").readline().strip()
user_home = os.popen('getent passwd %s | cut -d: -f 6' %
                     user).readline().strip()
# print(user)  # pi
# print(user_home) # /home/pi

# Default path for pictures and videos
Default_Pictures_Path = '%s/Pictures/vilib/' % user_home
Default_Videos_Path = '%s/Videos/vilib/' % user_home


# utils
def run_command(cmd):
    import subprocess
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result


def findContours(img):
    _tuple = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # compatible with opencv3.x and openc4.x
    if len(_tuple) == 3:
        _, contours, hierarchy = _tuple
    else:
        contours, hierarchy = _tuple
    return contours, hierarchy


def getIP():
    wlan0 = os.popen("ifconfig wlan0 |awk '/inet/'|awk 'NR==1 {print $2}'"
                     ).readline().strip('\n')
    eth0 = os.popen("ifconfig eth0 |awk '/inet/'|awk 'NR==1 {print $2}'"
                    ).readline().strip('\n')

    if wlan0 == '':
        wlan0 = None
    if eth0 == '':
        eth0 = None

    return wlan0, eth0


# region Main : parameter definition
traffic_num_list = [i for i in range(4)]
ges_num_list = [i for i in range(3)]

traffic_list = ['stop', 'right', 'left', 'forward']
gesture_list = ["paper", "scissor", "rock"]
# rock, scissor, paper

traffic_dict = dict(zip(traffic_num_list, traffic_list))  # 构建模型返回数字对应的类型的字典
ges_dict = dict(zip(ges_num_list, gesture_list))

traffic_sign_model_path = "/opt/vilib/tf_150_dr0.2.tflite"  # 模型路径
gesture_model_path = "/opt/vilib/3bak_ges_200_dr0.2.tflite"

interpreter_1 = tflite.Interpreter(
    model_path=traffic_sign_model_path)  # tflite读取模型
interpreter_1.allocate_tensors()

interpreter_2 = tflite.Interpreter(model_path=gesture_model_path)
interpreter_2.allocate_tensors()

# Get input and output tensors.
input_details_1 = interpreter_1.get_input_details()
# print(str(input_details_1))
output_details_1 = interpreter_1.get_output_details()
# print(str(output_details_1))

# Get input and output tensors.
input_details_2 = interpreter_2.get_input_details()
# print(str(input_details_2))
output_details_2 = interpreter_2.get_output_details()
# print(str(output_details_2))

image_classification_model = '/opt/vilib/mobilenet_v1_0.25_224_quant.tflite'
image_classification_labels = '/opt/vilib/labels_mobilenet_quant_v1_224.txt'

objects_detection_model = '/opt/vilib/detect.tflite'
objects_detection_labels = '/opt/vilib/coco_labels.txt'

# endregion : parameter definition

# region Main : flask
# os.environ['FLASK_ENV'] =  'development'
os.environ['FLASK_DEBUG'] = 'development'
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def get_frame():
    return cv2.imencode('.jpg', Vilib.img_array[0])[1].tobytes()


def get_qrcode_pictrue():
    return cv2.imencode('.jpg', Vilib.img_array[1])[1].tobytes()


def get_png_frame():
    return cv2.imencode('.png', Vilib.img_array[0])[1].tobytes()


def gen():
    """Video streaming generator function."""
    while True:
        # start_time = time.time()
        frame = get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03)
        # end_time = time.time() - start_time
        # print('flask fps:%s'%int(1/end_time))


@app.route('/mjpg')  ## video
def video_feed():
    # from camera import Camera
    """Video streaming route. Put this in the src attribute of an img tag."""
    response = Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/mjpg.jpg')  # jpg
def video_feed_jpg():
    # from camera import Camera
    """Video streaming route. Put this in the src attribute of an img tag."""
    response = Response(get_frame(), mimetype="image/jpeg")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/mjpg.png')  # png
def video_feed_png():
    # from camera import Camera
    """Video streaming route. Put this in the src attribute of an img tag."""
    response = Response(get_png_frame(), mimetype="image/png")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def web_camera_start():
    try:
        app.run(host='0.0.0.0', port=9000, threaded=True, debug=False)
    except Exception as e:
        print(e)


# endregion : flask

# 滤镜
EFFECTS = [
    "none",
    "negative",
    "solarize",
    "emboss",
    "posterise",
    "cartoon",
]

Camera_SETTING = [
    "resolution",  #max(4056,3040)
    #"framerate
    "rotation",  #(0 90 180 270)
    # "shutter_speed",
    "brightness",  # 0~100  default 50
    "sharpness",  # -100~100  default 0
    "contrast",  # -100~100  default 0
    "saturation",  # -100~100  default 0
    "iso",  #Vaild value:0(auto) 100,200,320,400,500,640,800
    "exposure_compensation",  # -25~25  default 0
    "exposure_mode",  #Valid values are: 'off', 'auto' (default),'night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach','verylong', 'fixedfps', 'antishake', or 'fireworks'
    "meter_mode",  #Valid values are: 'average' (default),'spot', 'backlit', 'matrix'.
    "awb_mode",  #'off', 'auto' (default), ‘sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent','incandescent', 'flash', or 'horizon'.
    "hflip",  # Default:False ,True
    "vflip",  # Default:False ,True
    # "crop",           #Retrieves or sets the zoom applied to the camera’s input, as a tuple (x, y, w, h) of floating point
    #values ranging from 0.0 to 1.0, indicating the proportion of the image to include in the output
    #(the ‘region of interest’). The default value is (0.0, 0.0, 1.0, 1.0), which indicates that everything
    #should be included.
]

# 相片水印
time_font = lambda x: ImageFont.truetype('/opt/vilib/Roboto-Light-2.ttf',
                                         int(x / 320.0 * 6))
text_font = lambda x: ImageFont.truetype('/opt/vilib/Roboto-Light-2.ttf',
                                         int(x / 320.0 * 10))
company_font = lambda x: ImageFont.truetype('/opt/vilib/Roboto-Light-2.ttf',
                                            int(x / 320.0 * 8))


# 添加水印接口
def add_text_to_image(name, text_1):

    image_target = Image.open(name)

    image_draw = ImageDraw.Draw(image_target)

    time_text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_size_x, time_size_y = image_draw.textsize(time_text,
                                                   font=time_font(
                                                       image_target.size[0]))
    text_size_x, text_size_y = image_draw.textsize(text_1,
                                                   font=text_font(
                                                       image_target.size[0]))

    # 设置文本文字位置
    # print(rgba_image)
    time_xy = (image_target.size[0] - time_size_x - time_size_y,
               image_target.size[1] - int(1.5 * time_size_y))
    text_xy = (text_size_y, image_target.size[1] - int(1.5 * text_size_y))
    company_xy = (text_size_y,
                  image_target.size[1] - int(1.5 * text_size_y) - text_size_y)

    # 设置文本颜色和透明度
    image_draw.text(time_xy,
                    time_text,
                    font=time_font(image_target.size[0]),
                    fill=(255, 255, 255))
    image_draw.text(company_xy,
                    text_1,
                    font=text_font(image_target.size[0]),
                    fill=(255, 255, 255))
    image_target.save(name, quality=95, subsampling=0)  #


class Vilib(object):

    flask_process = None
    camera_thread = None

    # set parameters

    # 读取人脸识别模型
    face_cascade = cv2.CascadeClassifier(
        '/opt/vilib/haarcascade_frontalface_default.xml')
    kernel_5 = np.ones((5, 5), np.uint8)  #4x4的卷积核

    video_source = 0

    # 用于寻找手势识别的肤色的区域的模板图片，可以通过手势识别的校准功能更改图片
    try:
        roi = cv2.imread("/opt/vilib/cali.jpg")
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    except Exception as e:
        print(e)

    # 创建共享字典，提供外部接口动态修改，以及返回字典内容
    # detect_obj_parameter = Manager().dict()
    detect_obj_parameter = {}
    img_array = Manager().list(range(2))

    # 默认的颜色识别颜色为红色
    detect_obj_parameter['color_default'] = 'red'

    # 颜色的HSV空间中的 H 的范围
    color_dict = {
        'red': [0, 4],
        'orange': [5, 18],
        'yellow': [22, 37],
        'green': [42, 85],
        'blue': [92, 110],
        'purple': [115, 165],
        'red_2': [165, 180]
    }

    # detect_obj_parameter
    # color_obj_parameter
    detect_obj_parameter['color_x'] = 320  # 最大色块中心坐标 x
    detect_obj_parameter['color_y'] = 240  # 最大色块中心坐标 x
    detect_obj_parameter['color_w'] = 0  # 最大色块 宽
    detect_obj_parameter['color_h'] = 0  # 最大色块 高
    detect_obj_parameter['color_n'] = 0  # 识别到的色块个数
    detect_obj_parameter['lower_color'] = np.array(
        [min(color_dict[detect_obj_parameter['color_default']]), 60, 60])
    detect_obj_parameter['upper_color'] = np.array(
        [max(color_dict[detect_obj_parameter['color_default']]), 255, 255])

    # Human_obj_parameter
    detect_obj_parameter['human_x'] = 320  # 最大人脸中心坐标 x
    detect_obj_parameter['human_y'] = 240  # 最大人脸中心坐标 x
    detect_obj_parameter['human_w'] = 0  # 最大人脸 宽
    detect_obj_parameter['human_h'] = 0  # 最大人脸 高
    detect_obj_parameter['human_n'] = 0  # 识别到的人脸个数

    # traffic_sign_obj_parameter
    detect_obj_parameter['traffic_sign_x'] = 320  # 中心坐标 x
    detect_obj_parameter['traffic_sign_y'] = 240  # 中心坐标 x
    detect_obj_parameter['traffic_sign_w'] = 0  # 宽
    detect_obj_parameter['traffic_sign_h'] = 0  # 高
    detect_obj_parameter[
        'traffic_sign_t'] = 'None'  # 标志文本 traffic_list = ['stop','right','left','forward'] 或 'none'
    detect_obj_parameter['traffic_sign_acc'] = 0

    # gesture_obj_parameter
    detect_obj_parameter['gesture_x'] = 320
    detect_obj_parameter['gesture_y'] = 240
    detect_obj_parameter['gesture_w'] = 0
    detect_obj_parameter['gesture_h'] = 0
    detect_obj_parameter[
        'gesture_t'] = 'None'  # 手势文本  gesture_list = ["paper","scissor","rock"]
    detect_obj_parameter['gesture_acc'] = 0

    # object_detection_parameter
    detect_obj_parameter['object_x'] = 320
    detect_obj_parameter['object_y'] = 240
    detect_obj_parameter['object_w'] = 0
    detect_obj_parameter['object_h'] = 0
    detect_obj_parameter['object_t'] = 'None'  # object label
    detect_obj_parameter['object_n'] = 0

    # detect_switch
    detect_obj_parameter['hdf_flag'] = False
    detect_obj_parameter['cdf_flag'] = False
    detect_obj_parameter['ts_flag'] = False
    detect_obj_parameter['gs_flag'] = False
    detect_obj_parameter['calibrate_flag'] = False
    detect_obj_parameter['object_follow_flag'] = False
    detect_obj_parameter['qr_flag'] = False

    detect_obj_parameter['camera_start_flag'] = False
    detect_obj_parameter['imshow_flag'] = False
    detect_obj_parameter['web_display_flag'] = False

    detect_obj_parameter['odf_flag'] = False
    detect_obj_parameter['icf_flag'] = False
    detect_obj_parameter['gdf_flag'] = False
    detect_obj_parameter['pdf_flag'] = False

    # QR_code
    detect_obj_parameter['qr_data'] = "None"
    detect_obj_parameter['qr_x'] = 320
    detect_obj_parameter['qr_y'] = 240
    detect_obj_parameter['qr_w'] = 0
    detect_obj_parameter['qr_h'] = 0

    # hands
    detect_obj_parameter['hands_joints'] = None
    # pose
    detect_obj_parameter['body_joints'] = None

    # picture
    detect_obj_parameter['picture_flag'] = False
    detect_obj_parameter['process_picture'] = True
    detect_obj_parameter[
        'picture_path'] = Default_Pictures_Path + datetime.datetime.now(
        ).strftime('%Y-%m-%d %H:%M:%S') + '.jpg'

    detect_obj_parameter['video_flag'] = None

    detect_obj_parameter['ensure_flag'] = False
    detect_obj_parameter['clarity_val'] = 0

    # picture
    detect_obj_parameter['eff'] = 0
    detect_obj_parameter['setting'] = 0
    detect_obj_parameter['setting_flag'] = False
    detect_obj_parameter['setting_val'] = 0
    # detect_obj_parameter['current_setting_val'] = None
    detect_obj_parameter['setting_resolution'] = (3840, 2880)
    detect_obj_parameter['change_setting_flag'] = False
    detect_obj_parameter['change_setting_type'] = 'None'
    detect_obj_parameter['change_setting_val'] = 0

    detect_obj_parameter['photo_button_flag'] = False
    detect_obj_parameter['content_length'] = 0
    detect_obj_parameter['content_num'] = 0
    detect_obj_parameter['process_content_1'] = []
    detect_obj_parameter['process_si'] = []
    # detect_obj_parameter['process_dict'] = {}

    detect_obj_parameter['watermark_flag'] = True
    detect_obj_parameter['camera_flip'] = False
    detect_obj_parameter['watermark'] = "Shot by Picar-x"

    rt_img = np.ones((320, 240), np.uint8)
    front_view_img = np.zeros((240, 320, 3), np.uint8)
    # 使用白色填充图片区域,默认为黑色
    # front_view_img.fill(255)
    img_array[0] = rt_img
    img_array[1] = rt_img
    vi_img = np.ones((320, 240), np.uint8)

    # 通过两个参数Shift_left，Shift_right修改
    @staticmethod
    def photo_effect(shirt_way='Shift_left'):
        print(shirt_way)
        shirt_way = str(shirt_way)
        if shirt_way == 'Shift_left':
            Vilib.detect_obj_parameter['eff'] += 1
            if Vilib.detect_obj_parameter['eff'] >= len(EFFECTS):
                Vilib.detect_obj_parameter['eff'] = 0
        elif shirt_way == 'Shift_right':
            Vilib.detect_obj_parameter['eff'] -= 1
            if Vilib.detect_obj_parameter['eff'] < 0:
                Vilib.detect_obj_parameter['eff'] = len(EFFECTS) - 1
        else:
            raise Exception("parameter error!")

    @staticmethod
    def video_flag(flag):
        # global button_motion
        Vilib.detect_obj_parameter['video_flag'] = flag

    # @staticmethod
    # def watermark(watermark = "Shot by Picar-x"):
    #     # global button_motion
    #     watermark = str(watermark)
    #     Vilib.detect_obj_parameter['watermark_flag'] = True
    #     Vilib.detect_obj_parameter['watermark'] = watermark

    @staticmethod
    def show_setting(flag):
        # global button_motion

        Vilib.detect_obj_parameter['setting_flag'] = flag
        # button_motion = 'free'

    @staticmethod
    def change_setting_type_val(setting_type, setting_val):
        # global button_motion
        if setting_type == 'resolution':
            Vilib.detect_obj_parameter['setting_resolution'] = setting_val
        else:
            Vilib.detect_obj_parameter['change_setting_type'] = setting_type
            Vilib.detect_obj_parameter['change_setting_val'] = setting_val
            Vilib.detect_obj_parameter['change_setting_flag'] = True

    @staticmethod
    def shuttle_button():
        Vilib.detect_obj_parameter['photo_button_flag'] = True

    @staticmethod
    def make_qrcode_picture(data):
        Vilib.img_array = qrcode.make(data=data)

# 返回检测到的颜色的坐标，大小，数量

    @staticmethod
    def color_detect_object(obj_parameter):
        if obj_parameter == 'x':
            return int(Vilib.detect_obj_parameter['color_x'] / 214.0) - 1
        elif obj_parameter == 'y':
            return -1 * (int(Vilib.detect_obj_parameter['color_y'] / 160.2) - 1
                         )  #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter['color_w']  #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter['color_h']  #objects_max_height
        elif obj_parameter == 'number':
            return Vilib.detect_obj_parameter['color_n']  #objects_count
        return None

# 返回检测到的人脸的坐标，大小，数量

    @staticmethod
    def human_detect_object(obj_parameter):
        if obj_parameter == 'x':
            return int(Vilib.detect_obj_parameter['human_x'] / 214.0) - 1
        elif obj_parameter == 'y':
            return -1 * (int(Vilib.detect_obj_parameter['human_y'] / 160.2) - 1
                         )  #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter['human_w']  #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter['human_h']  #objects_max_height
        elif obj_parameter == 'number':
            return Vilib.detect_obj_parameter['human_n']  #objects_count
        return None

# 返回检测到的交通标志的坐标，大小，类型，准确度

    @staticmethod
    def traffic_sign_detect_object(obj_parameter):
        if obj_parameter == 'x':
            return int(
                Vilib.detect_obj_parameter['traffic_sign_x'] / 214.0) - 1
        elif obj_parameter == 'y':
            return -1 * (
                int(Vilib.detect_obj_parameter['traffic_sign_y'] / 160.2) - 1
            )  #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter[
                'traffic_sign_w']  #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter[
                'traffic_sign_h']  #objects_max_height
        elif obj_parameter == 'number':
            return Vilib.detect_obj_parameter['traffic_sign_n']  #objects_count
        elif obj_parameter == 'type':
            return Vilib.detect_obj_parameter['traffic_sign_t']  #objects_type
        elif obj_parameter == 'accuracy':
            return Vilib.detect_obj_parameter[
                'traffic_sign_acc']  #objects_type
        return 'none'

# 返回检测到的手势的坐标，大小，类型，准确度

    @staticmethod
    def gesture_detect_object(obj_parameter):
        if obj_parameter == 'x':
            return int(Vilib.detect_obj_parameter['gesture_x'] / 214.0) - 1
        elif obj_parameter == 'y':
            return -1 * (int(Vilib.detect_obj_parameter['gesture_y'] / 160.2) -
                         1)  #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter['gesture_w']  #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter['gesture_h']  #objects_max_height
        elif obj_parameter == 'type':
            return Vilib.detect_obj_parameter['gesture_t']  #objects_type
        elif obj_parameter == 'accuracy':
            return Vilib.detect_obj_parameter['gesture_acc']  #objects_type
        return 'none'

# 返回检测到的二维码的坐标，大小，类型，准确度

    @staticmethod
    def qrcode_detect_object(obj_parameter='data'):
        if obj_parameter == 'x':
            return int(Vilib.detect_obj_parameter['qr_x'] / 214.0) - 1
        elif obj_parameter == 'y':
            return -1 * (int(Vilib.detect_obj_parameter['qr_y'] / 160.2) - 1
                         )  #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter['qr_w']  #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter['qr_h']  #objects_max_height
        elif obj_parameter == 'data':
            return Vilib.detect_obj_parameter['qr_data']  #objects_count
        return 'none'

# 设置要检测的颜色

    @staticmethod
    def detect_color_name(color_name):
        if color_name == 'close':
            Vilib.detect_obj_parameter['cdf_flag'] = False
        else:
            Vilib.detect_obj_parameter['color_default'] = color_name
            Vilib.detect_obj_parameter['lower_color'] = np.array([
                min(Vilib.color_dict[
                    Vilib.detect_obj_parameter['color_default']]), 60, 60
            ])
            Vilib.detect_obj_parameter['upper_color'] = np.array([
                max(Vilib.color_dict[
                    Vilib.detect_obj_parameter['color_default']]), 255, 255
            ])
            Vilib.detect_obj_parameter['cdf_flag'] = True

# function switch
# 人脸检测开关

    @staticmethod
    def human_detect_switch(flag=False):
        Vilib.detect_obj_parameter['hdf_flag'] = flag

    # 颜色检测开关
    @staticmethod
    def color_detect_switch(flag=False):
        Vilib.detect_obj_parameter['cdf_flag'] = flag

    # 手势检测开关
    @staticmethod
    def gesture_detect_switch(flag=False):
        Vilib.detect_obj_parameter['gs_flag'] = flag

    # 交通标志检测开关
    @staticmethod
    def traffic_sign_detect_switch(flag=False):
        Vilib.detect_obj_parameter['ts_flag'] = flag

    # 手势检测开关
    @staticmethod
    def gesture_calibrate_switch(flag=False):
        Vilib.detect_obj_parameter['calibrate_flag'] = flag

    # 目标检测开关
    @staticmethod
    def object_follow_switch(flag=False):
        Vilib.detect_obj_parameter['object_follow_flag'] = flag

    # 二维码检测开关
    @staticmethod
    def qrcode_detect_switch(flag=False):
        Vilib.detect_obj_parameter['qr_flag'] = flag

# camera()

    @staticmethod
    def camera_clone():
        Vilib.camera()

    @staticmethod
    def camera():
        global effect
        flask_thread = None

        picam2 = Picamera2()
        preview_config = picam2.preview_configuration
        # preview_config.size = (800, 600)
        preview_config.size = (640, 480)
        preview_config.format = 'RGB888'  # 'XRGB8888', 'XBGR8888', 'RGB888', 'BGR888', 'YUV420'
        hflip = Vilib.detect_obj_parameter['camera_hflip']
        vflip = Vilib.detect_obj_parameter['camera_vflip']
        preview_config.transform = libcamera.Transform(hflip=hflip,
                                                       vflip=vflip)
        preview_config.colour_space = libcamera.ColorSpace.Sycc()
        preview_config.buffer_count = 4
        preview_config.queue = True

        try:
            picam2.start()
        except Exception as e:
            print(f"\033[38;5;1mError:\033[0m\n{e}")
            print("\nPlease check whether the camera is connected well,  \
and disable the \"legacy camera driver\" on raspi-config")
            import sys
            sys.exit(1)

        last_e = 'none'
        camera_val = 0
        last_show_content_list = []
        show_content_list = []
        change_type_val = []
        change_type_dict = {"shutter_speed":0,"resolution":[2592,1944], "brightness":50, "contrast":0, "sharpness":0, "saturation":0, "iso":0, "exposure_compensation":0, "exposure_mode":'auto', \
            "meter_mode":'average' ,"rotation":0 ,"awb_mode":'auto',"drc_strength":'off',"hflip":False,"vflip":True}
        start_time = 0
        end_time = 0
        # camera.framerate = 10
        #
        try:
            while True:
                start_time = time.time()
                img = picam2.capture_array()

                img = Vilib.gesture_calibrate(img)
                img = Vilib.traffic_detect(img)
                img = Vilib.color_detect_func(img)
                img = Vilib.human_detect_func(img)
                img = Vilib.gesture_recognition(img)
                img = Vilib.qrcode_detect_func(img)
                # img = Vilib.face_detect_func(img)
                # img = Vilib.face_recognition_func(img)
                img = Vilib.object_detect_fuc(img)
                img = Vilib.image_classify_fuc(img)
                img = Vilib.hands_detect_fuc(img)
                img = Vilib.pose_detect_fuc(img)

                # change_camera_setting
                if Vilib.detect_obj_parameter['change_setting_flag'] == True:
                    Vilib.detect_obj_parameter['change_setting_flag'] = False
                    change_setting_cmd = "camera." + Vilib.detect_obj_parameter[
                        'change_setting_type'] + '=' + str(
                            Vilib.detect_obj_parameter['change_setting_val'])
                    print(change_setting_cmd)
                    exec(change_setting_cmd)
                    change_type_dict[Vilib.detect_obj_parameter[
                        'change_setting_type']] = Vilib.detect_obj_parameter[
                            'change_setting_val']
                if Vilib.detect_obj_parameter['content_num'] != 0:
                    for i in range(Vilib.detect_obj_parameter['content_num']):
                        exec(
                            "Vilib.detect_obj_parameter['process_si'] = Vilib.detect_obj_parameter['process_content_"
                            + str(i + 1) + "'" + "]")
                        cv2.putText(
                            img,
                            str(Vilib.detect_obj_parameter['process_si'][0]),
                            Vilib.detect_obj_parameter['process_si'][1],
                            cv2.FONT_HERSHEY_SIMPLEX,
                            Vilib.detect_obj_parameter['process_si'][3],
                            Vilib.detect_obj_parameter['process_si'][2], 2)
                if Vilib.detect_obj_parameter['setting_flag'] == True:
                    setting_type = Camera_SETTING[
                        Vilib.detect_obj_parameter['setting']]
                    if setting_type == "resolution":
                        Vilib.detect_obj_parameter[
                            'setting_val'] = Vilib.detect_obj_parameter[
                                'setting_resolution']
                        change_type_dict["resolution"] = list(
                            Vilib.detect_obj_parameter['setting_resolution'])
                        cv2.putText(
                            img, 'resolution:' +
                            str(Vilib.
                                detect_obj_parameter['setting_resolution']),
                            (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 2)
                    elif setting_type == "shutter_speed":
                        change_type_dict[
                            "shutter_speed"] = Vilib.detect_obj_parameter[
                                'change_setting_val']
                        cv2.putText(
                            img, 'shutter_speed:' +
                            str(Vilib.
                                detect_obj_parameter['change_setting_val']),
                            (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 2)
                    else:
                        cmd_text = "Vilib.detect_obj_parameter['setting_val'] = camera." + Camera_SETTING[
                            Vilib.detect_obj_parameter['setting']]
                        # print('mennu:',Ras_Cam.detect_obj_parameter['setting_val'])
                        exec(cmd_text)
                        cv2.putText(
                            img, setting_type + ': ' +
                            str(Vilib.detect_obj_parameter['setting_val']),
                            (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 2)

                e = EFFECTS[Vilib.detect_obj_parameter['eff']]
                if last_e != e:
                    last_e = e
                last_e = e
                if last_e != 'none':
                    cv2.putText(img, str(last_e), (0, 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (204, 209, 72),
                                2)

                if Vilib.detect_obj_parameter['photo_button_flag'] == True:
                    picam2.close()
                    break

                if Vilib.detect_obj_parameter['imshow_flag'] == True:
                    try:
                        cv2.imshow("Picamera", img)
                        cv2.waitKey(1)  # 1 ms
                        if cv2.getWindowProperty('Picamera',
                                                 cv2.WND_PROP_VISIBLE) == 0:
                            # cv2.destroyAllWindows()
                            cv2.destroyWindow('Picamera')
                            Vilib.detect_obj_parameter['imshow_flag'] = False
                            Vilib.detect_obj_parameter[
                                'camera_start_flag'] = False
                    except Exception as e:
                        print(e)
                        print(
                            'imshow faileed, maybe this environment does not have "display" '
                        )

                if Vilib.detect_obj_parameter['camera_start_flag'] == False:
                    break

                # web_display
                if Vilib.detect_obj_parameter['web_display_flag'] == True:
                    if flask_thread == None or flask_thread.is_alive(
                    ) == False:
                        print('Starting network video streaming ...')
                        wlan0, eth0 = getIP()
                        if wlan0 != None:
                            ip = wlan0
                        else:
                            ip = eth0
                        print('\nRunning on: http://%s:9000/mjpg\n' % ip)
                        flask_thread = threading.Thread(
                            name='flask_thread', target=web_camera_start)
                        flask_thread.setDaemon(True)
                        flask_thread.start()
                elif Vilib.detect_obj_parameter['web_display_flag'] == False:
                    if flask_thread != None and flask_thread.is_alive():
                        flask_thread.join(timeout=0.2)

                Vilib.img_array[0] = img
                end_time = time.time()
                end_time = end_time - start_time

                if Vilib.detect_obj_parameter['camera_start_flag'] == False:
                    break

        except KeyboardInterrupt:
            pass
        finally:
            print('camera close')
            picam2.close()
            cv2.destroyAllWindows()

# 手势校准接口

    @staticmethod
    def gesture_calibrate(img):
        if Vilib.detect_obj_parameter['calibrate_flag'] == True:
            cv2.imwrite('/opt/vilib/cali.jpg', img[190:290, 270:370])
            cv2.rectangle(img, (270, 190), (370, 290), (255, 255, 255), 2)

        return img

# 添加水印的控制开关

    @staticmethod
    def get_picture(process_picture):
        Vilib.detect_obj_parameter['picture_flag'] = True
        Vilib.detect_obj_parameter['process_picture'] = process_picture
        Vilib.detect_obj_parameter[
            'picture_path'] = Default_Pictures_Path + datetime.datetime.now(
            ).strftime('%Y-%m-%d %H:%M:%S') + '.jpg'

# # 拍照控制接口
#     @staticmethod
#     def take_photo(img):
#         if img is not None:
#             cv2.imwrite(Vilib.detect_obj_parameter['picture_path'], img)
#             Vilib.detect_obj_parameter['picture_flag'] = False

    @staticmethod
    def cnt_area(cnt):
        x, y, w, h = cv2.boundingRect(cnt)
        return w * h

# 交通标志检测函数，传入值依此是摄像头读取到图像，交通标志的坐标，长宽

    @staticmethod
    def traffic_predict(input_img, x, y, w, h):

        x1 = int(x)
        x2 = int(x + w)
        y1 = int(y)
        y2 = int(y + h)

        new_img = input_img[y1:y2, x1:x2]
        new_img = (new_img / 255.0)
        new_img = (new_img - 0.5) * 2.0

        resize_img = cv2.resize(
            new_img, (96, 96),
            interpolation=cv2.INTER_LINEAR)  #调整为识别模型的要求的96x96的图像大小
        flatten_img = np.reshape(resize_img, (96, 96, 3))
        im5 = np.expand_dims(flatten_img, axis=0)

        # Perform the actual detection by running the model with the image as input
        image_np_expanded = im5.astype('float32')  # 类型也要满足要求

        interpreter_1.set_tensor(input_details_2[0]['index'],
                                 image_np_expanded)  #放入图像到模型中
        interpreter_1.invoke()  #检测
        output_data_2 = interpreter_1.get_tensor(
            output_details_2[0]['index'])  #获取模型返回的数据

        #     # 出来的结果去掉没用的维度   np.where(result==np.max(result)))[0][0]
        result = np.squeeze(output_data_2)
        result_accuracy = round(np.max(result), 2)  #获取准确度
        ges_class = np.where(result == np.max(result))[0][0]  #获取类型

        return result_accuracy, ges_class

### 手势识别的流程和上面交通标志一致

    @staticmethod
    def gesture_predict(input_img, x, y, w, h):

        x1 = int(x)
        x2 = int(x + w)
        y1 = int(y)
        y2 = int(y + h)

        if x1 <= 0:
            x1 = 0
        elif x2 >= 640:
            x2 = 640
        if y1 <= 0:
            y1 = 0
        elif y2 >= 640:
            y2 = 640

        new_img = input_img[y1:y2, x1:x2]
        new_img = (new_img / 255.0)
        new_img = (new_img - 0.5) * 2.0

        resize_img = cv2.resize(new_img, (96, 96),
                                interpolation=cv2.INTER_LINEAR)
        flatten_img = np.reshape(resize_img, (96, 96, 3))
        im5 = np.expand_dims(flatten_img, axis=0)

        # Perform the actual detection by running the model with the image as input
        image_np_expanded = im5.astype('float32')  # 类型也要满足要求

        interpreter_2.set_tensor(input_details_2[0]['index'],
                                 image_np_expanded)
        interpreter_2.invoke()
        output_data_2 = interpreter_2.get_tensor(output_details_2[0]['index'])

        #     # 出来的结果去掉没用的维度   np.where(result==np.max(result)))[0][0]
        result = np.squeeze(output_data_2)
        result_accuracy = round(np.max(result), 2)
        ges_class = np.where(result == np.max(result))[0][0]

        return result_accuracy, ges_class

# 交通标志可能存在区域的检测

    @staticmethod
    def traffic_detect(img):

        if Vilib.detect_obj_parameter['ts_flag'] == True:

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 2.从BGR转换到HSV
            cv2.circle(img, (160, 120), 1, (255, 255, 255), -1)

            ### red
            mask_red_1 = cv2.inRange(hsv, (157, 20, 20), (180, 255, 255))
            mask_red_2 = cv2.inRange(hsv, (0, 20, 20), (10, 255, 255))

            ### blue
            mask_blue = cv2.inRange(hsv, (92, 10, 10), (125, 255, 255))

            ### all
            mask_all = cv2.bitwise_or(mask_red_1, mask_blue)
            mask_all = cv2.bitwise_or(mask_red_2, mask_all)

            open_img = cv2.morphologyEx(mask_all,
                                        cv2.MORPH_OPEN,
                                        Vilib.kernel_5,
                                        iterations=1)  #开运算
            contours, hierarchy = findContours(open_img)
            contours = sorted(contours, key=Vilib.cnt_area, reverse=False)
            traffic_n = len(contours)
            max_area = 0
            traffic_sign_num = 0

            if traffic_n > 0:
                for i in contours:  # 遍历所有的轮廓
                    x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高

                    # 在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                    if w > 32 and h > 32:
                        acc_val, traffic_type = Vilib.traffic_predict(
                            img, x, y, w, h)
                        # print(traffic_type,acc_val)
                        acc_val = round(acc_val * 100)
                        if acc_val >= 75:
                            if traffic_type == 1 or traffic_type == 2 or traffic_type == 3:
                                simple_gray = cv2.cvtColor(
                                    img[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY)
                                # new_mask_blue = cv2.inRange(hsv[y:y+h,x:x+w],(92,70,50), (118,255,255))
                                circles = cv2.HoughCircles(simple_gray,cv2.HOUGH_GRADIENT,1,32,\
                                param1=140,param2=70,minRadius=int(w/4.0),maxRadius=max(w,h))

                                if circles is not None:
                                    for i in circles[0, :]:
                                        # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                                        traffic_sign_coor = (int(x + i[0]),
                                                             int(y + i[1]))
                                        cv2.circle(img, traffic_sign_coor,
                                                   i[2], (255, 0, 255), 2)
                                        cv2.putText(
                                            img,
                                            str(traffic_dict[traffic_type]) +
                                            ': ' + str(round(acc_val)),
                                            (int(x + i[0] - i[2]),
                                             int(y + i[1] - i[2])),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                                            (255, 0, 255), 2)  #加减10是调整字符位置
                                        if w * h > max_area:
                                            max_area = w * h
                                            max_obj_x = x
                                            max_obj_y = y
                                            max_obj_w = w
                                            max_obj_h = h
                                            max_obj_t = traffic_type
                                            max_obj_acc = acc_val
                                            traffic_sign_num += 1

                            elif traffic_type == 0:
                                # small_hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)
                                red_mask_1 = cv2.inRange(
                                    hsv[y:y + h, x:x + w], (0, 50, 20),
                                    (4, 255, 255
                                     ))  # 3.inRange()：介于lower/upper之间的为白色，其余黑色
                                red_mask_2 = cv2.inRange(
                                    hsv[y:y + h, x:x + w], (163, 50, 20),
                                    (180, 255, 255))
                                red_mask_all = cv2.bitwise_or(
                                    red_mask_1, red_mask_2)

                                # circles = np.uint16(np.around(circles))

                                # ret, new_binary = cv2.threshold(simple_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
                                new_binary = cv2.GaussianBlur(
                                    red_mask_all, (5, 5), 0)

                                open_img = cv2.morphologyEx(red_mask_all,
                                                            cv2.MORPH_OPEN,
                                                            Vilib.kernel_5,
                                                            iterations=1)  #开运算
                                open_img = cv2.dilate(open_img,
                                                      Vilib.kernel_5,
                                                      iterations=5)
                                blue_contours, hierarchy = findContours(
                                    open_img)
                                contours_count = len(blue_contours)
                                if contours_count >= 1:
                                    # print("contours:",contours_count)
                                    blue_contours = sorted(blue_contours,
                                                           key=Vilib.cnt_area,
                                                           reverse=True)

                                    epsilon = 0.025 * cv2.arcLength(
                                        blue_contours[0], True)
                                    approx = cv2.approxPolyDP(
                                        blue_contours[0], epsilon, True)

                                    #     # 分析几何形状
                                    corners = len(approx)

                                    if corners >= 0:
                                        traffic_sign_coor = (int(x + w / 2),
                                                             int(y + h / 2))
                                        cv2.rectangle(img, (x, y),
                                                      (x + w, y + h),
                                                      (255, 0, 255), 2)
                                        cv2.putText(
                                            img,
                                            str(traffic_dict[traffic_type]) +
                                            ': ' + str(round(acc_val)), (x, y),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                                            (255, 0, 255), 2)  #加减10是调整字符位置
                                        if w * h > max_area:
                                            max_area = w * h
                                            max_obj_x = x
                                            max_obj_y = y
                                            max_obj_w = w
                                            max_obj_h = h
                                            max_obj_t = traffic_type
                                            max_obj_acc = acc_val
                                            traffic_sign_num += 1

                # print("traffic_sign_num:",traffic_sign_num)
                if traffic_sign_num > 0:

                    Vilib.detect_obj_parameter['traffic_sign_x'] = int(
                        max_obj_x + max_obj_w / 2)
                    Vilib.detect_obj_parameter['traffic_sign_y'] = int(
                        max_obj_y + max_obj_h / 2)
                    Vilib.detect_obj_parameter['traffic_sign_w'] = max_obj_w
                    Vilib.detect_obj_parameter['traffic_sign_h'] = max_obj_h
                    # print("traffic_sign_type:",)
                    Vilib.detect_obj_parameter[
                        'traffic_sign_t'] = traffic_dict[max_obj_t]
                    Vilib.detect_obj_parameter[
                        'traffic_sign_acc'] = max_obj_acc
                else:
                    Vilib.detect_obj_parameter['traffic_sign_x'] = 320
                    Vilib.detect_obj_parameter['traffic_sign_y'] = 240
                    Vilib.detect_obj_parameter['traffic_sign_w'] = 0
                    Vilib.detect_obj_parameter['traffic_sign_h'] = 0
                    Vilib.detect_obj_parameter['traffic_sign_t'] = 'none'
                    Vilib.detect_obj_parameter['traffic_sign_acc'] = 0

        else:
            Vilib.detect_obj_parameter['traffic_sign_x'] = 320
            Vilib.detect_obj_parameter['traffic_sign_y'] = 240
            Vilib.detect_obj_parameter['traffic_sign_w'] = 0
            Vilib.detect_obj_parameter['traffic_sign_h'] = 0
            Vilib.detect_obj_parameter['traffic_sign_t'] = 'none'
            Vilib.detect_obj_parameter['traffic_sign_acc'] = 0

        return img

# 手掌肤色的区域检测，把图像的区域给手势识别接口做手势识别

    @staticmethod
    def gesture_recognition(img):
        if Vilib.detect_obj_parameter['gs_flag'] == True:

            ###肤色部分

            target_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # 首先对样本图像计算2D直方图
            roi_hsv_hist = cv2.calcHist([Vilib.roi_hsv], [0, 1], None,
                                        [180, 256], [0, 180, 0, 255])
            # 对得到的样本2D直方图进行归一化
            # 这样可以方便显示，归一化后的直方图就变成0-255之间的数了
            # cv2.NORM_MINMAX表示对数组所有值进行转换，线性映射到最大最小值之间
            cv2.normalize(roi_hsv_hist, roi_hsv_hist, 0, 255, cv2.NORM_MINMAX)
            # 对待检测图像进行反向投影
            # 最后一个参数为尺度参数
            dst = cv2.calcBackProject([target_hsv], [0, 1], roi_hsv_hist,
                                      [0, 180, 0, 256], 1)
            # 构建一个圆形卷积核，用于对图像进行平滑，连接分散的像素
            disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dst = cv2.filter2D(dst, -1, disc, dst)
            ret, thresh = cv2.threshold(dst, 1, 255, 0)
            dilate = cv2.dilate(thresh, Vilib.kernel_5, iterations=3)
            # 注意由于原图是三通道BGR图像，因此在进行位运算之前，先要把thresh转成三通道
            # thresh = cv2.merge((dilate, dilate, dilate))
            # 对原图与二值化后的阈值图像进行位运算，得到结果
            # res = cv2.bitwise_and(img, thresh)
            # ycrcb=cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)
            # cr_skin = cv2.inRange(ycrcb, (85,124,121), (111,131,128))
            # open_img = cv2.morphologyEx(cr_skin, cv2.MORPH_OPEN,Vilib.kernel_5,iterations=1)

            contours, hierarchy = findContours(dilate)
            ges_num = len(contours)
            is_ges = False
            if ges_num > 0:
                contours = sorted(contours, key=Vilib.cnt_area, reverse=True)
                # for i in range(0,len(contours)):    #遍历所有的轮廓
                x, y, w, h = cv2.boundingRect(
                    contours[0])  #将轮廓分解为识别对象的左上角坐标和宽、高
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = Vilib.face_cascade.detectMultiScale(
                    gray[y:y + h, x:x + w], 1.3, 2)
                # print(len(faces))
                face_len = len(faces)

                # 在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                if w >= 60 and h >= 60 and face_len == 0:
                    # acc_val,ges_type = Vilib.gesture_predict(img,x-2.2*w,y-2.8*h,4.4*w,5.6*h)
                    acc_val, ges_type = Vilib.gesture_predict(
                        img, x - 0.1 * w, y - 0.2 * h, 1.1 * w, 1.2 * h)

                    acc_val = round(acc_val * 100, 3)
                    if acc_val >= 75:
                        # print(x,y,w,h)
                        cv2.rectangle(img,
                                      (int(x - 0.1 * w), int(y - 0.2 * h)),
                                      (int(x + 1.1 * w), int(y + 1.2 * h)),
                                      (0, 125, 0), 2, cv2.LINE_AA)
                        cv2.rectangle(img, (0, 0), (125, 27), (204, 209, 72),
                                      -1, cv2.LINE_AA)
                        cv2.putText(img, ges_dict[ges_type] + ': ' +
                                    str(acc_val) + '%', (0, 17),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                    (255, 255, 255), 2)  ##(0,97,240)

                        Vilib.detect_obj_parameter['gesture_x'] = int(x +
                                                                      w / 2)
                        Vilib.detect_obj_parameter['gesture_y'] = int(y +
                                                                      h / 2)
                        Vilib.detect_obj_parameter['gesture_w'] = w
                        Vilib.detect_obj_parameter['gesture_h'] = h
                        Vilib.detect_obj_parameter['gesture_t'] = ges_dict[
                            ges_type]
                        Vilib.detect_obj_parameter['gesture_acc'] = acc_val
                        is_ges = True

            if is_ges == False:
                Vilib.detect_obj_parameter['gesture_x'] = 320
                Vilib.detect_obj_parameter['gesture_y'] = 240
                Vilib.detect_obj_parameter['gesture_w'] = 0
                Vilib.detect_obj_parameter['gesture_h'] = 0
                Vilib.detect_obj_parameter['gesture_t'] = 'none'
                Vilib.detect_obj_parameter['gesture_acc'] = 0

        return img

# 人脸检测

    @staticmethod
    def human_detect_func(img):
        if Vilib.detect_obj_parameter['hdf_flag'] == True:
            resize_img = cv2.resize(
                img, (320, 240),
                interpolation=cv2.INTER_LINEAR)  # 2.从BGR转换到RAY
            gray = cv2.cvtColor(resize_img, cv2.COLOR_BGR2GRAY)
            faces = Vilib.face_cascade.detectMultiScale(gray, 1.3, 2)
            # print(len(faces))
            Vilib.detect_obj_parameter['human_n'] = len(faces)
            max_area = 0
            if Vilib.detect_obj_parameter['human_n'] > 0:
                for (x, y, w, h) in faces:
                    x = x * 2
                    y = y * 2
                    w = w * 2
                    h = h * 2
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    object_area = w * h
                    if object_area > max_area:
                        object_area = max_area
                        Vilib.detect_obj_parameter['human_x'] = int(x + w / 2)
                        Vilib.detect_obj_parameter['human_y'] = int(y + h / 2)
                        Vilib.detect_obj_parameter['human_w'] = w
                        Vilib.detect_obj_parameter['human_h'] = h
            else:
                Vilib.detect_obj_parameter['human_x'] = 320
                Vilib.detect_obj_parameter['human_y'] = 240
                Vilib.detect_obj_parameter['human_w'] = 0
                Vilib.detect_obj_parameter['human_h'] = 0
                Vilib.detect_obj_parameter['human_n'] = 0
            return img
        else:
            return img

# 颜色识别

    @staticmethod
    def color_detect_func(img):

        # 蓝色的范围，不同光照条件下不一样，可灵活调整   H：色度，S：饱和度 v:明度
        if Vilib.detect_obj_parameter['cdf_flag'] == True:
            resize_img = cv2.resize(img, (160, 120),
                                    interpolation=cv2.INTER_LINEAR)
            hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)  # 2.从BGR转换到HSV
            color_type = Vilib.detect_obj_parameter['color_default']
            mask = cv2.inRange(
                hsv, np.array([min(Vilib.color_dict[color_type]), 60, 60]),
                np.array([max(Vilib.color_dict[color_type]), 255,
                          255]))  # 3.inRange()：介于lower/upper之间的为白色，其余黑色
            if color_type == 'red':
                mask_2 = cv2.inRange(hsv, (167, 0, 0), (180, 255, 255))
                mask = cv2.bitwise_or(mask, mask_2)

            open_img = cv2.morphologyEx(mask,
                                        cv2.MORPH_OPEN,
                                        Vilib.kernel_5,
                                        iterations=1)  #开运算
            ####在binary中发现轮廓，轮廓按照面积从小到大排列
            contours, hierarchy = findContours(open_img)
            Vilib.detect_obj_parameter['color_n'] = len(contours)
            max_area = 0
            if Vilib.detect_obj_parameter['color_n'] > 0:
                for i in contours:  #遍历所有的轮廓
                    x, y, w, h = cv2.boundingRect(i)  #将轮廓分解为识别对象的左上角坐标和宽、高
                    # 在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                    if w >= 8 and h >= 8:
                        x = x * 4
                        y = y * 4
                        w = w * 4
                        h = h * 4
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0),
                                      2)
                        # 给识别对象写上标号
                        cv2.putText(img, color_type, (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                    2)  #加减10是调整字符位置

                        object_area = w * h
                        if object_area > max_area:
                            max_area = object_area
                            Vilib.detect_obj_parameter['color_x'] = int(x +
                                                                        w / 2)
                            Vilib.detect_obj_parameter['color_y'] = int(y +
                                                                        h / 2)
                            Vilib.detect_obj_parameter['color_w'] = w
                            Vilib.detect_obj_parameter['color_h'] = h
                            # print()
            else:
                Vilib.detect_obj_parameter['color_x'] = 320
                Vilib.detect_obj_parameter['color_y'] = 240
                Vilib.detect_obj_parameter['color_w'] = 0
                Vilib.detect_obj_parameter['color_h'] = 0
                Vilib.detect_obj_parameter['color_n'] = 0
            return img
        else:
            return img

# 二维码识别

    @staticmethod
    def qrcode_detect_func(img):
        if Vilib.detect_obj_parameter['qr_flag'] == True:
            barcodes = pyzbar.decode(img)
            # 循环检测到的条形码
            if len(barcodes) > 0:
                for barcode in barcodes:
                    # 提取条形码的边界框的位置
                    # 画出图像中条形码的边界框
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

                    # 条形码数据为字节对象，所以如果我们想在输出图像上
                    # 画出来，就需要先将它转换成字符串
                    barcodeData = barcode.data.decode("utf-8")
                    # barcodeType = barcode.type

                    # 绘出图像上条形码的数据和条形码类型
                    # text = "{} ({})".format(barcodeData, barcodeType)
                    text = "{}".format(barcodeData)
                    if len(text) > 0:
                        Vilib.detect_obj_parameter['qr_data'] = text
                        Vilib.detect_obj_parameter['qr_h'] = h
                        Vilib.detect_obj_parameter['qr_w'] = w
                        Vilib.detect_obj_parameter['qr_x'] = x
                        Vilib.detect_obj_parameter['qr_y'] = y
                    # print("Vilib.qr_date:%s"%Vilib.qr_date)
                    cv2.putText(img, text, (x - 20, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                Vilib.detect_obj_parameter['qr_data'] = "None"
                Vilib.detect_obj_parameter['qr_x'] = 320
                Vilib.detect_obj_parameter['qr_y'] = 240
                Vilib.detect_obj_parameter['qr_w'] = 0
                Vilib.detect_obj_parameter['qr_h'] = 0
            return img
        else:
            return img

# 颜色识别 2

    @staticmethod
    def new_color_detect_func(img, color):
        Vilib.detect_color_name(color)

        # 蓝色的范围，不同光照条件下不一样，可灵活调整   H：色度，S：饱和度 v:明度
        if Vilib.detect_obj_parameter['cdf_flag'] == True:
            resize_img = cv2.resize(img, (160, 120),
                                    interpolation=cv2.INTER_LINEAR)
            hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)  # 2.从BGR转换到HSV
            # print(Vilib.lower_color)
            color_type = Vilib.detect_obj_parameter['color_default']

            mask = cv2.inRange(
                hsv, np.array([min(Vilib.color_dict[color_type]), 60, 60]),
                np.array([max(Vilib.color_dict[color_type]), 255,
                          255]))  # 3.inRange()：介于lower/upper之间的为白色，其余黑色
            if color_type == 'red':
                mask_2 = cv2.inRange(hsv, (167, 0, 0), (180, 255, 255))
                mask = cv2.bitwise_or(mask, mask_2)

            open_img = cv2.morphologyEx(mask,
                                        cv2.MORPH_OPEN,
                                        Vilib.kernel_5,
                                        iterations=1)  #开运算

            ####在binary中发现轮廓，轮廓按照面积从小到大排列
            contours, hierarchy = cv2.findContours(open_img)

            Vilib.detect_obj_parameter['color_n'] = len(contours)
            max_area = 0

            if Vilib.detect_obj_parameter['color_n'] > 0:
                for i in contours:  #遍历所有的轮廓
                    x, y, w, h = cv2.boundingRect(i)  #将轮廓分解为识别对象的左上角坐标和宽、高

                    #在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                    if w >= 8 and h >= 8:
                        x = x * 2
                        y = y * 2
                        w = w * 2
                        h = h * 2
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0),
                                      2)
                        #给识别对象写上标号
                        cv2.putText(img, color_type, (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                    2)  #加减10是调整字符位置

                        object_area = w * h
                        if object_area > max_area:
                            max_area = object_area
                            Vilib.detect_obj_parameter['color_x'] = int(x +
                                                                        w / 2)
                            Vilib.detect_obj_parameter['color_y'] = int(y +
                                                                        h / 2)
                            Vilib.detect_obj_parameter['color_w'] = w
                            Vilib.detect_obj_parameter['color_h'] = h
                            # print()
            else:
                Vilib.detect_obj_parameter['color_x'] = 320
                Vilib.detect_obj_parameter['color_y'] = 240
                Vilib.detect_obj_parameter['color_w'] = 0
                Vilib.detect_obj_parameter['color_h'] = 0
                Vilib.detect_obj_parameter['color_n'] = 0
            return img
        else:
            return img

# 开启摄像头

    @staticmethod
    def camera_start(vflip=False, hflip=False):
        Vilib.detect_obj_parameter['camera_vflip'] = vflip
        Vilib.detect_obj_parameter['camera_hflip'] = hflip
        Vilib.detect_obj_parameter['camera_start_flag'] = True
        Vilib.camera_thread = threading.Thread(target=Vilib.camera_clone,
                                               name="camera_satrt")
        Vilib.camera_thread.daemon = False
        Vilib.camera_thread.start()

# 关闭摄像头

    @staticmethod
    def camera_close():
        if Vilib.camera_thread != None:
            Vilib.detect_obj_parameter['camera_start_flag'] = False
            time.sleep(0.1)

# 开启摄像头网络传输

    @staticmethod
    def camera_flask():
        Vilib.detect_obj_parameter['web_display_flag'] = True

# close flask

    @staticmethod
    def web_display_close():
        Vilib.detect_obj_parameter['web_display_flag'] = False

# 1. 显示在树莓派桌面，在浏览器输入蜘蛛的IP地址可以看到画面

    @staticmethod
    def display(local=True, web=True):
        # cheack camera thread is_alive
        if Vilib.camera_thread != None and Vilib.camera_thread.is_alive():
            # check gui
            if local == True:
                # if os.path.exists('/usr/share/xsessions/'):
                #     os.environ['XAUTHORITY'] = '%s/.Xauthority'%user_home
                #     os.environ['DISPLAY'] = ':0.0'
                #     Vilib.detect_obj_parameter['imshow_flag'] = True
                #     print("imshow start ...")
                if 'DISPLAY' in os.environ.keys():
                    Vilib.detect_obj_parameter['imshow_flag'] = True
                    print("imshow start ...")
                else:
                    Vilib.detect_obj_parameter['imshow_flag'] = False
                    print("local display failed, because there is no gui.")

            # web video
            if web == True:
                Vilib.detect_obj_parameter['web_display_flag'] = True
        else:
            print('Error: Please execute < camera_start() > first.')

# 2. 拍照保存

    @staticmethod
    def take_photo(photo_name, path=Default_Pictures_Path):
        # check path
        while not os.path.exists(path):
            # print('Path does not exist. Creating path now ... ')
            os.makedirs(name=path, mode=0o777, exist_ok=True)
            time.sleep(0.01)
        # save photo
        img = Vilib.img_array[0]
        for _ in range(5):
            if img is not None:
                cv2.imwrite(path + '/' + photo_name + '.jpg', img)
                Vilib.detect_obj_parameter['picture_flag'] = False
                # print('The photo is saved as '+path+'/'+photo_name+'.jpg')
                break
            else:
                time.sleep(0.01)
        else:
            print('Photo save failed .. ')

# 3.录像

    rec_video_set = {}

    rec_video_set["fourcc"] = cv2.VideoWriter_fourcc(*'XVID')
    #rec_video_set["fourcc"] = cv2.cv.CV_FOURCC("D", "I", "B", " ")

    rec_video_set["fps"] = 20.0
    rec_video_set["framesize"] = (640, 480)
    rec_video_set["isColor"] = True

    rec_video_set["name"] = "default"
    rec_video_set["path"] = Default_Videos_Path

    rec_video_set["start_flag"] = False
    rec_video_set["stop_flag"] = False

    @staticmethod
    def rec_video_work():
        while not os.path.exists(Vilib.rec_video_set["path"]):
            # print('Path does not exist. Creating path now ... ')
            os.makedirs(name=Vilib.rec_video_set["path"],
                        mode=0o777,
                        exist_ok=True)
            time.sleep(0.01)
        video_out = cv2.VideoWriter(
            Vilib.rec_video_set["path"] + '/' + Vilib.rec_video_set["name"] +
            '.avi', Vilib.rec_video_set["fourcc"], Vilib.rec_video_set["fps"],
            Vilib.rec_video_set["framesize"], Vilib.rec_video_set["isColor"])

        while True:
            if Vilib.rec_video_set["start_flag"] == True:
                video_out.write(Vilib.img_array[0])
            if Vilib.rec_video_set["stop_flag"] == True:
                video_out.release()  # note need to release the video writer
                Vilib.rec_video_set["start_flag"] == False
                break

    rec_thread = None

    @staticmethod
    def rec_video_run():
        if Vilib.rec_thread != None:
            Vilib.rec_video_stop()
        Vilib.rec_video_set["stop_flag"] = False
        Vilib.rec_thread = threading.Thread(name='rec_video',
                                            target=Vilib.rec_video_work)
        Vilib.rec_thread.setDaemon(True)
        Vilib.rec_thread.start()

    @staticmethod
    def rec_video_start():
        Vilib.rec_video_set["start_flag"] = True
        Vilib.rec_video_set["stop_flag"] = False

    @staticmethod
    def rec_video_pause():
        Vilib.rec_video_set["start_flag"] = False

    @staticmethod
    def rec_video_stop():
        Vilib.rec_video_set["start_flag"] == False
        Vilib.rec_video_set["stop_flag"] = True
        if Vilib.rec_thread != None:
            Vilib.rec_thread.join(3)
            Vilib.rec_thread = None

# 4.颜色识别

    @staticmethod
    def color_detect(color="red"):
        Vilib.detect_color_name(color)
        #Vilib.color_detect_switch(True)

# 5.人脸检测

    @staticmethod
    def face_detect_switch(flag=False):
        Vilib.human_detect_switch(flag)

# 二维码  #

    @staticmethod
    def qr_coder_reader():
        #Vilib.qrcode_detect_switch(True)
        text = Vilib.detect_obj_parameter['qr_data']
        return text

# objects detection

    @staticmethod
    def object_detect_switch(flag=False):
        Vilib.detect_obj_parameter['odf_flag'] = flag

    @staticmethod
    def object_detect_set_model(path):
        global objects_detection_model
        if not os.path.exists(path):
            raise ValueError('incorrect model path ')
        objects_detection_model = path

    @staticmethod
    def object_detect_set_labels(path):
        global objects_detection_labels
        if not os.path.exists(path):
            raise ValueError('incorrect labels path ')
        objects_detection_labels = path

    @staticmethod
    def object_detect_fuc(img):
        if Vilib.detect_obj_parameter['odf_flag'] == True:
            # print('detect_objects starting')
            from .objects_detection import detect_objects
            img = detect_objects(image=img,
                                 model=objects_detection_model,
                                 labels=objects_detection_labels)
        return img

# image classification

    @staticmethod
    def image_classify_switch(flag=False):
        Vilib.detect_obj_parameter['icf_flag'] = flag

    @staticmethod
    def image_classify_set_model(path):
        global image_classification_model
        if not os.path.exists(path):
            raise ValueError('incorrect model path ')
        image_classification_model = path

    @staticmethod
    def image_classify_set_labels(path):
        global image_classification_labels
        if not os.path.exists(path):
            raise ValueError('incorrect labels path ')
        image_classification_labels = path

    @staticmethod
    def image_classify_fuc(img):
        if Vilib.detect_obj_parameter['icf_flag'] == True:
            # print('classify_image starting')
            from .image_classification import classify_image
            img = classify_image(image=img,
                                 model=image_classification_model,
                                 labels=image_classification_labels)
        return img

# gesture detection

    @staticmethod
    def hands_detect_switch(flag=False):
        from .hands_detection import DetectHands
        Vilib.detect_hands = DetectHands()
        Vilib.detect_obj_parameter['gdf_flag'] = flag

    @staticmethod
    def hands_detect_fuc(img):
        if Vilib.detect_obj_parameter['gdf_flag'] == True:
            img, Vilib.detect_obj_parameter[
                'hands_joints'] = Vilib.detect_hands.work(image=img)
        return img


# pose detection

    @staticmethod
    def pose_detect_switch(flag=False):
        from .pose_detection import DetectPose
        Vilib.pose_detect = DetectPose()
        Vilib.detect_obj_parameter['pdf_flag'] = flag

    @staticmethod
    def pose_detect_fuc(img):
        if Vilib.detect_obj_parameter['pdf_flag'] == True:
            img, Vilib.detect_obj_parameter[
                'body_joints'] = Vilib.pose_detect.work(image=img)
        return img

if __name__ == '__main__':
    Vilib().camera_start()
    Vilib.display()