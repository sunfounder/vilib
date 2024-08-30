#!/usr/bin/env python3

# whther print welcome message
import os

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

import sys

new_path = '/usr/local/lib/aarch64-linux-gnu/python3.12/site-packages/'
new_path2 = '/usr/local/lib/aarch64-linux-gnu/'
sys.path.append(new_path)
sys.path.append(new_path2)
print(sys.path)
import libcamera

from picamera2 import Picamera2

import cv2
import numpy as np

import time
import threading
from multiprocessing import Process, Pool, Manager, Value, cpu_count

from .utils import *

# user and user home directory
# =================================================================
user = os.popen("echo ${SUDO_USER:-$(who -m | awk '{ print $1 }')}").readline().strip()
user_home = os.popen(f'getent passwd {user} | cut -d: -f 6').readline().strip()
# print(f"user: {user}")
# print(f"user_home: {user_home}")

# Default path for pictures and videos
DEFAULLT_PICTURES_PATH = '%s/Pictures/vilib/'%user_home
DEFAULLT_VIDEOS_PATH = '%s/Videos/vilib/'%user_home

# Vilib
# =================================================================
class Vilib(object):

    camera_vflip = False
    camera_hflip = False

    camera_run = False
    camera_has_start = False

    processes = 1 # number of processes
    camera_fps = 60

    camera_thread = None
    flask_thread = None

    img = Manager().list(range(1))

    Windows_Name = "picamera"
    imshow_flag = False
    web_display_flag = False

    qrcode_win_name = 'qrcode'
    imshow_qrcode_flag = False
    web_qrcode_flag = False

    draw_fps_sw = False
    fps_origin = (640-105, 20)
    fps_size = 0.6
    fps_color = (255, 255, 255)

    detect_obj_parameter = {}
    color_obj_parameter = {}
    color_detect_color = Manager().Value(str, None)
    face_detect_sw = Value('b', False)
    hands_detect_sw = Value('b', False)
    pose_detect_sw = Value('b', False)
    image_classify_sw = Value('b', False)
    image_classification_model = Manager().Value(str, None)
    image_classification_labels = Manager().Value(str, None)
    objects_detect_sw = Value('b', False)
    objects_detection_model = Manager().Value(str, None)
    objects_detection_labels = Manager().Value(str, None)
    qrcode_detect_sw = Value('b', False)
    traffic_detect_sw = Value('b', False)

    qrcode_display_thread = None
    qrcode_making_completed = False
    qrcode_img = Manager().list(range(1))
    qrcode_img_encode = None

    web_display = None

    @staticmethod
    def camera():
        # --- init picamera2 ---
        try:
            picam2 = Picamera2()

            preview_config = picam2.preview_configuration
            # preview_config.size = (800, 600)
            preview_config.size = (640, 480)
            preview_config.format = 'RGB888'  # 'XRGB8888', 'XBGR8888', 'RGB888', 'BGR888', 'YUV420'
            preview_config.transform = libcamera.Transform(
                                            hflip=Vilib.camera_hflip ,
                                            vflip=Vilib.camera_vflip
                                        )
            preview_config.colour_space = libcamera.ColorSpace.Sycc()
            preview_config.buffer_count = 4
            preview_config.queue = True
            # preview_config.raw = {'size': (2304, 1296)}
            preview_config.controls = {'FrameRate': Vilib.camera_fps} # change picam2.capture_array() takes time

            picam2.start()
        except Exception as e:
            print(f"\033[38;5;1mError:\033[0m\n{e}")
            print("\nPlease check whether the camera is connected well" +\
                "You can use the \"libcamea-hello\" command to test the camera"
                )
            exit(1)
        
        fps = 0
        start_time = 0
        framecount = 0

        try:
            start_time = time.time()

            print(f'Image processing process number: {Vilib.processes}')

            if Vilib.processes > 1:
                # ------- start pool ----
                def pool_init_worker():
                    import signal
                    signal.signal(signal.SIGINT, signal.SIG_IGN)

                pool = Pool(processes=Vilib.processes, initializer=pool_init_worker)
                process_list = []
                pindex = 0
                
                # --- First fill of all processes ---
                frame = picam2.capture_array()

                for _ in range(Vilib.processes):
                    _p = pool.apply_async(Vilib.img_process, [frame])
                    process_list.append(_p) 

            Vilib.camera_has_start = True

            while True:
                # ----------- extract image data ----------------
                frame = picam2.capture_array()

                # ----------- image gains and effects ----------------

                # ----------- apply new img_process, and draw fps on completed frame ----------------
                # multi-process
                # ==================
                if Vilib.processes > 1: 
                    process_list[pindex] = pool.apply_async(Vilib.img_process, [frame])
                    
                    pindex += 1
                    if pindex > Vilib.processes - 1:
                        pindex = 0 
                    output_img, result = process_list[pindex].get()

                # no multi-process
                # ==================
                else: 
                    output_img, result =Vilib.img_process(frame)

                # ----------- process result -----------
                Vilib.img_process_result_copy(result)

                # ----------- draw_fps & the final frame -----------
                # this completed frame
                Vilib.img = Vilib.draw_fps(output_img, fps)

                # ----------- calculate fps ----------------
                # calculate fps
                framecount += 1
                elapsed_time = float(time.time() - start_time)
                if (elapsed_time > 1):
                    fps = round(framecount/elapsed_time, 1)
                    framecount = 0
                    start_time = time.time()
                # ----------- display on desktop ----------------
                if Vilib.imshow_flag == True:
                    try:
                        cv2.imshow(Vilib.Windows_Name, Vilib.img)

                        if Vilib.imshow_qrcode_flag and Vilib.qrcode_making_completed:
                                Vilib.qrcode_making_completed = False
                                cv2.imshow(Vilib.qrcode_win_name, Vilib.qrcode_img)

                        cv2.waitKey(1)
                        if cv2.getWindowProperty(Vilib.Windows_Name, cv2.WND_PROP_VISIBLE) == 0:
                            cv2.destroyWindow(Vilib.Windows_Name)

                    except Exception as e:
                        Vilib.imshow_flag = False
                        print(f"imshow failed:\n  {e}")
                        break

                # ----------- exit ----------------
                if Vilib.camera_run == False:
                    break

        except KeyboardInterrupt as e:
            print(e)
        finally:
            print('camera close')
            if Vilib.processes > 1:
                pool.terminate()
            picam2.close()
            cv2.destroyAllWindows()

    @staticmethod
    def camera_start(vflip=False, hflip=False, processes=1, camera_fps=60):
        Vilib.camera_hflip = hflip
        Vilib.camera_vflip = vflip

        if processes > cpu_count():
            Vilib.processes = cpu_count()
        elif processes < 0:
            Vilib.processes = 1
        else:
            Vilib.processes = processes

        if camera_fps < 10:
            Vilib.camera_fps = 10
        elif camera_fps > 90:
            Vilib.camera_fps = 90

        Vilib.camera_run = True
        Vilib.camera_thread = threading.Thread(target=Vilib.camera, name="vilib")
        Vilib.camera_thread.daemon = False
        Vilib.camera_thread.start()
        while not Vilib.camera_has_start:
            pass

    @staticmethod
    def camera_close():
        if Vilib.camera_thread != None:
            Vilib.camera_run = False
            time.sleep(0.1)

    @staticmethod
    def img_process_result_copy(result):
        if result['color'] != None:
            Vilib.color_obj_parameter = result['color']
            Vilib.detect_obj_parameter['color'] = Vilib.color_obj_parameter['color']
            Vilib.detect_obj_parameter['color_x'] = Vilib.color_obj_parameter['x']
            Vilib.detect_obj_parameter['color_y'] = Vilib.color_obj_parameter['y']
            Vilib.detect_obj_parameter['color_w'] = Vilib.color_obj_parameter['w']
            Vilib.detect_obj_parameter['color_h'] = Vilib.color_obj_parameter['h']
            Vilib.detect_obj_parameter['color_n'] = Vilib.color_obj_parameter['n']
            
        if result['face'] != None:
            Vilib.face_obj_parameter = result['face']
            Vilib.detect_obj_parameter['human_x'] = Vilib.face_obj_parameter['x']
            Vilib.detect_obj_parameter['human_y'] = Vilib.face_obj_parameter['y']
            Vilib.detect_obj_parameter['human_w'] = Vilib.face_obj_parameter['w']
            Vilib.detect_obj_parameter['human_h'] = Vilib.face_obj_parameter['h']
            Vilib.detect_obj_parameter['human_n'] = Vilib.face_obj_parameter['n']

        if result['traffic_sign'] != None:
            Vilib.traffic_sign_obj_parameter = result['traffic_sign']
            Vilib.detect_obj_parameter['traffic_sign_x'] = Vilib.traffic_sign_obj_parameter['x']
            Vilib.detect_obj_parameter['traffic_sign_y'] = Vilib.traffic_sign_obj_parameter['y']
            Vilib.detect_obj_parameter['traffic_sign_w'] = Vilib.traffic_sign_obj_parameter['w']
            Vilib.detect_obj_parameter['traffic_sign_h'] = Vilib.traffic_sign_obj_parameter['h']
            Vilib.detect_obj_parameter['traffic_sign_t'] = Vilib.traffic_sign_obj_parameter['t']
            Vilib.detect_obj_parameter['traffic_sign_acc'] = Vilib.traffic_sign_obj_parameter['acc']

        if result['qrcode'] != None:
            Vilib.detect_obj_parameter['qr_x'] = Vilib.qrcode_obj_parameter['x']
            Vilib.detect_obj_parameter['qr_y'] = Vilib.qrcode_obj_parameter['y']
            Vilib.detect_obj_parameter['qr_w'] = Vilib.qrcode_obj_parameter['w']
            Vilib.detect_obj_parameter['qr_h'] = Vilib.qrcode_obj_parameter['h']
            Vilib.detect_obj_parameter['qr_data'] = Vilib.qrcode_obj_parameter['data']

    @staticmethod
    def img_process(img):
        result = {}

        img, color_obj_parameter = Vilib.color_detect_func(img)
        img, face_obj_parameter = Vilib.face_detect_func(img)
        img, traffic_sign_obj_parameter = Vilib.traffic_detect_fuc(img)
        img, qrcode_obj_parameter = Vilib.qrcode_detect_func(img)
        img, image_classification_obj_parameter = Vilib.image_classify_fuc(img)
        img = Vilib.object_detect_fuc(img)
        img, hands_obj_parametr = Vilib.hands_detect_fuc(img)
        img = Vilib.pose_detect_fuc(img)

        result['color'] = color_obj_parameter
        result['face'] = face_obj_parameter
        result['traffic_sign'] = traffic_sign_obj_parameter
        result['qrcode'] = qrcode_obj_parameter
        result['img_classification'] = image_classification_obj_parameter
        result['hands'] = hands_obj_parametr

        # print(result)
        return img, result

    @staticmethod
    def draw_fps(img, fps):
        if Vilib.draw_fps_sw:
            cv2.putText(
                    # img, # image
                    img,
                    f"FPS: {fps}", # text
                    Vilib.fps_origin, # origin
                    cv2.FONT_HERSHEY_SIMPLEX, # font
                    Vilib.fps_size, # font_scale
                    Vilib.fps_color, # font_color
                    1, # thickness
                    cv2.LINE_AA, # line_type: LINE_8 (default), LINE_4, LINE_AA
                )
        return img

    # @staticmethod
    # def draw_fps(img, fps):
    #     if Vilib.draw_fps_sw:
    #         blk = np.zeros(img.shape, np.uint8)  
    #         cv2.rectangle(blk, (640-110, 2), (640-10, 24), (128, 128, 128), -1)
    #         img = cv2.addWeighted(img, 1.0, blk, 0.5, 1)
    #         cv2.putText(
    #                 # img, # image
    #                 img,
    #                 f"FPS: {fps}", # text
    #                 Vilib.fps_origin, # origin
    #                 cv2.FONT_HERSHEY_SIMPLEX, # font
    #                 Vilib.fps_size, # font_scale
    #                 Vilib.fps_color, # font_color
    #                 1, # thickness
    #                 cv2.LINE_AA, # line_type: LINE_8 (default), LINE_4, LINE_AA
    #             )
    #     return img

    @staticmethod
    def display(local=True, web=True):
        # cheack camera thread is_alive
        if Vilib.camera_thread != None and Vilib.camera_thread.is_alive():
            # check gui
            if local == True:
                if 'DISPLAY' in os.environ.keys():
                    Vilib.imshow_flag = True  
                    print("Imgshow start ...")
                else:
                    Vilib.imshow_flag = False 
                    print("Local display failed, because there is no gui.") 
            # web video
            if web == True:
                Vilib.web_display_flag = True
                wlan0,eth0 = getIP()
                if wlan0 != None:
                    ip = wlan0     
                else:
                    ip = eth0
                print(f'\nWeb display on: http://{ip}:9000/mjpg\n')

                # ----------- flask_thread ----------------
                if Vilib.flask_thread == None or Vilib.flask_thread.is_alive() == False:
                    print('Starting web streaming ...')
                    from .web_display import WebDisplay
                    web_display = WebDisplay(Vilib)
                    Vilib.flask_thread = threading.Thread(name='flask_thread',target=web_display.web_camera_start)
                    Vilib.flask_thread.daemon = True
                    Vilib.flask_thread.start()
                    time.sleep(0.05) # wait for flask thread to start
        else:
            print('Error: Please execute < camera_start() > first.')

    @staticmethod
    def show_fps(color=None, fps_size=None, fps_origin=None):
        if color is not None:
            Vilib.fps_color = color
        if fps_size is not None:
            Vilib.fps_size = fps_size
        if fps_origin is not None:
            Vilib.fps_origin = fps_origin

        Vilib.draw_fps_sw = True

    @staticmethod
    def hide_fps():
        Vilib.draw_fps_sw = False

    # take photo
    # =================================================================
    @staticmethod
    def take_photo(photo_name, path=DEFAULLT_PICTURES_PATH):
        # ----- check path -----
        if not os.path.exists(path):
            # print('Path does not exist. Creating path now ... ')
            os.makedirs(name=path, mode=0o751, exist_ok=True)
            time.sleep(0.01) 
        # ----- save photo -----
        status = False
        for _ in range(5):
            if  Vilib.img is not None:
                status = cv2.imwrite(path + '/' + photo_name +'.jpg', Vilib.img)
                break
            else:
                time.sleep(0.01)
        else:
            status = False

        # if status:
        #     print('The photo is saved as '+path+'/'+photo_name+'.jpg')
        # else:
        #     print('Photo save failed .. ')

        return status


    # record video
    # =================================================================
    rec_video_set = {}

    rec_video_set["fourcc"] = cv2.VideoWriter_fourcc(*'XVID') 
    #rec_video_set["fourcc"] = cv2.cv.CV_FOURCC("D", "I", "B", " ") 

    rec_video_set["fps"] = 30.0
    rec_video_set["framesize"] = (640, 480)
    rec_video_set["isColor"] = True

    rec_video_set["name"] = "default"
    rec_video_set["path"] = DEFAULLT_VIDEOS_PATH

    rec_video_set["start_flag"] = False
    rec_video_set["stop_flag"] =  False

    rec_thread = None

    @staticmethod
    def rec_video_work():
        if not os.path.exists(Vilib.rec_video_set["path"]):
            # print('Path does not exist. Creating path now ... ')
            os.makedirs(name=Vilib.rec_video_set["path"],
                        mode=0o751,
                        exist_ok=True
            )
            time.sleep(0.01)
        video_out = cv2.VideoWriter(Vilib.rec_video_set["path"]+'/'+Vilib.rec_video_set["name"]+'.avi',
                                    Vilib.rec_video_set["fourcc"], Vilib.rec_video_set["fps"], 
                                    Vilib.rec_video_set["framesize"], Vilib.rec_video_set["isColor"])
    
        while True:
            if Vilib.rec_video_set["start_flag"] == True:
                # video_out.write(Vilib.img_array[0])
                video_out.write(Vilib.img)
            if Vilib.rec_video_set["stop_flag"] == True:
                video_out.release() # note need to release the video writer
                Vilib.rec_video_set["start_flag"] == False
                break

    @staticmethod
    def rec_video_run():
        if Vilib.rec_thread != None:
            Vilib.rec_video_stop()
        Vilib.rec_video_set["stop_flag"] = False
        Vilib.rec_thread = threading.Thread(name='rec_video', target=Vilib.rec_video_work)
        Vilib.rec_thread.daemon = True
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

   # color detection
    # =================================================================
    @staticmethod 
    def color_detect(color="red"):
        '''
        :param color: could be red, green, blue, yellow , orange, purple
        '''
        from .color_detection import color_obj_parameter
        Vilib.color_detect_color.value = color
        Vilib.color_obj_parameter = color_obj_parameter
        Vilib.color_obj_parameter['color'] = color
        Vilib.detect_obj_parameter['color'] = color

    @staticmethod
    def color_detect_func(img):
        if Vilib.color_detect_color.value is not None and Vilib.color_detect_color.value != 'close':
            from .color_detection import color_detect_work
            img, color_obj_parameter = color_detect_work(img, 640, 480, Vilib.color_detect_color.value)
            return img, color_obj_parameter
        else:
            return img, None

    @staticmethod
    def close_color_detection():
        Vilib.color_detect_color.value = None
        Vilib.color_obj_parameter['color'] = None
        Vilib.detect_obj_parameter['color'] = None

  # face detection
    # =================================================================
    @staticmethod   
    def face_detect_switch(flag=False):
        Vilib.face_detect_sw.value = flag
        if Vilib.face_detect_sw.value:
            from .face_detection import face_detect, set_face_detection_model, face_obj_parameter
            Vilib.set_face_detection_model = set_face_detection_model
            Vilib.face_obj_parameter = face_obj_parameter
            Vilib.detect_obj_parameter['human_x'] = Vilib.face_obj_parameter['x']
            Vilib.detect_obj_parameter['human_y'] = Vilib.face_obj_parameter['y']
            Vilib.detect_obj_parameter['human_w'] = Vilib.face_obj_parameter['w']
            Vilib.detect_obj_parameter['human_h'] = Vilib.face_obj_parameter['h']
            Vilib.detect_obj_parameter['human_n'] = Vilib.face_obj_parameter['n']

    @staticmethod
    def face_detect_func(img):
        if Vilib.face_detect_sw.value:
            from .face_detection import face_detect
            img, face_obj_parameter = face_detect(img, 640, 480)
            return img, face_obj_parameter
        else:
            return img, None

   # traffic sign detection
    # =================================================================
    @staticmethod
    def traffic_detect_switch(flag=False):
        Vilib.traffic_detect_sw.value  = flag
        if Vilib.traffic_detect_sw.value:
            from .traffic_sign_detection import traffic_sign_detect, traffic_sign_obj_parameter
            Vilib.traffic_sign_obj_parameter = traffic_sign_obj_parameter
            Vilib.detect_obj_parameter['traffic_sign_x'] = Vilib.traffic_sign_obj_parameter['x']
            Vilib.detect_obj_parameter['traffic_sign_y'] = Vilib.traffic_sign_obj_parameter['y']
            Vilib.detect_obj_parameter['traffic_sign_w'] = Vilib.traffic_sign_obj_parameter['w']
            Vilib.detect_obj_parameter['traffic_sign_h'] = Vilib.traffic_sign_obj_parameter['h']
            Vilib.detect_obj_parameter['traffic_sign_t'] = Vilib.traffic_sign_obj_parameter['t']
            Vilib.detect_obj_parameter['traffic_sign_acc'] = Vilib.traffic_sign_obj_parameter['acc']

    @staticmethod
    def traffic_detect_fuc(img):
        if Vilib.traffic_detect_sw.value:
            from .traffic_sign_detection import traffic_sign_detect
            img, traffic_sign_obj_parameter = traffic_sign_detect(img, border_rgb=(255, 0, 0))
            return img, traffic_sign_obj_parameter
        else:
            return img, None

    # qrcode recognition
    # =================================================================
    @staticmethod
    def qrcode_detect_switch(flag=False):
        Vilib.qrcode_detect_sw.value = flag
        if Vilib.qrcode_detect_sw.value:
            from .qrcode_recognition import qrcode_obj_parameter
            Vilib.qrcode_obj_parameter = qrcode_obj_parameter
            Vilib.detect_obj_parameter['qr_x'] = Vilib.qrcode_obj_parameter['x']
            Vilib.detect_obj_parameter['qr_y'] = Vilib.qrcode_obj_parameter['y']
            Vilib.detect_obj_parameter['qr_w'] = Vilib.qrcode_obj_parameter['w']
            Vilib.detect_obj_parameter['qr_h'] = Vilib.qrcode_obj_parameter['h']
            Vilib.detect_obj_parameter['qr_data'] = Vilib.qrcode_obj_parameter['data']

    @staticmethod
    def qrcode_detect_func(img):
        if Vilib.qrcode_detect_sw.value:
            from .qrcode_recognition import qrcode_recognize
            img, qrcode_obj_parameter = qrcode_recognize(img, border_rgb=(255, 0, 0))
            return img, qrcode_obj_parameter
        else:
            return img, None

    # qrcode making
    # =================================================================
    @staticmethod
    def make_qrcode(data, 
                    path=None,
                    version=1,
                    box_size=10,
                    border=4,
                    fill_color=(132,  112, 255),
                    back_color=(255, 255, 255)
                    ):
        import qrcode # https://github.com/lincolnloop/python-qrcode

        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_pil = qr.make_image(fill_color=fill_color,
                            back_color=back_color)
        if path != None:
            qr_pil.save(path)

        Vilib.qrcode_img = cv2.cvtColor(np.array(qr_pil), cv2.COLOR_RGB2BGR)
        Vilib.qrcode_making_completed = True

        if Vilib.web_qrcode_flag:
            Vilib.qrcode_img_encode = cv2.imencode('.jpg', Vilib.qrcode_img)[1].tobytes()



    @staticmethod
    def display_qrcode_work():
        while True:
            if Vilib.imshow_flag:
                time.sleep(0.1)
                continue

            # ----------- display qrcode on desktop ----------------
            if Vilib.imshow_qrcode_flag and Vilib.qrcode_making_completed :
                    Vilib.qrcode_making_completed = False
                    try:
                        if len(Vilib.qrcode_img) > 10:
                            cv2.imshow(Vilib.qrcode_win_name, Vilib.qrcode_img)
                            cv2.waitKey(1)
                            if cv2.getWindowProperty(Vilib.qrcode_win_name, cv2.WND_PROP_VISIBLE) == 0:
                                cv2.destroyWindow(Vilib.qrcode_win_name)
                    except Exception as e:
                        Vilib.imshow_qrcode_flag = False
                        print(f"imshow qrcode failed:\n  {e}")
                        break
            time.sleep(0.1)

    @staticmethod
    def display_qrcode(local=True, web=True):
        # check gui
        if local == True:
            if 'DISPLAY' in os.environ.keys():
                Vilib.imshow_qrcode_flag = True  
                print("Imgshow qrcode start ...")
            else:
                Vilib.imshow_qrcode_flag = False 
                print("Local display failed, because there is no gui.") 
        # web video
        if web == True:
            Vilib.web_qrcode_flag = True 
            wlan0,eth0 = getIP()
            if wlan0 != None:
                ip = wlan0
            else:
                ip = eth0
            print(f'QRcode display on: http://{ip}:9000/qrcode\n')

            # ----------- flask_thread ----------------
            if Vilib.flask_thread == None or Vilib.flask_thread.is_alive() == False:
                print('Starting web streaming ...')
                Vilib.flask_thread = threading.Thread(name='flask_thread',target=web_camera_start)
                Vilib.flask_thread.daemon = True
                Vilib.flask_thread.start()

        if Vilib.qrcode_display_thread == None or Vilib.qrcode_display_thread.is_alive() == False:
            Vilib.qrcode_display_thread = threading.Thread(name='qrcode_display',target=Vilib.display_qrcode_work)
            Vilib.qrcode_display_thread.daemon = True
            Vilib.qrcode_display_thread.start()


    # image classification
    # =================================================================
    @staticmethod
    def image_classify_switch(flag=False):
        from .image_classification import image_classification_obj_parameter
        Vilib.image_classify_sw = flag
        Vilib.image_classification_obj_parameter = image_classification_obj_parameter

    @staticmethod
    def image_classify_set_model(path):
        if not os.path.exists(path):
            raise ValueError('incorrect model path ')          
        Vilib.image_classification_model = path

    @staticmethod
    def image_classify_set_labels(path):
        if not os.path.exists(path):
            raise ValueError('incorrect labels path ')  
        Vilib.image_classification_labels = path

    @staticmethod
    def image_classify_fuc(img):
        if Vilib.image_classify_sw == True:
            # print('classify_image starting')
            from .image_classification import classify_image
            img, image_classification_obj_parameter = classify_image(image=img,
                                model=Vilib.image_classification_model,
                                labels=Vilib.image_classification_labels)   
            return img, image_classification_obj_parameter
        else:
            return img, None

    # objects detection
    # =================================================================
    @staticmethod
    def object_detect_switch(flag=False):
        Vilib.objects_detect_sw.value = flag

    @staticmethod
    def object_detect_set_model(path):
        if not os.path.exists(path):
            raise ValueError('incorrect model path ')    
        Vilib.objects_detection_model = path

    @staticmethod
    def object_detect_set_labels(path):
        if not os.path.exists(path):
            raise ValueError('incorrect labels path ')    
        Vilib.objects_detection_labels = path

    @staticmethod
    def object_detect_fuc(img):
        if Vilib.objects_detect_sw.value == True:
            from .objects_detection import detect_objects
            img = detect_objects(image=img,
                                model=Vilib.objects_detection_model,
                                labels=Vilib.objects_detection_labels)
        return img

    # hands detection
    # =================================================================
    @staticmethod
    def hands_detect_switch(flag=False):
        from .hands_detection import DetectHands
        Vilib.detect_hands = DetectHands()
        Vilib.hands_detect_sw = flag

    @staticmethod
    def hands_detect_fuc(img):
        if Vilib.hands_detect_sw.value == True:
            from .hands_detection import DetectHands
            img, hands_obj_parametr = DetectHands(max_num_hands=2).work(img)   
            return img, hands_obj_parametr
        else:
            return img, None

    # pose detection
    # =================================================================
    @staticmethod
    def pose_detect_switch(flag=False):
        from .pose_detection import DetectPose
        Vilib.pose_detect = DetectPose()
        Vilib.pose_detect_sw = flag

    @staticmethod
    def pose_detect_fuc(img):
        if Vilib.pose_detect_sw.value == True:
            from .pose_detection import DetectPose
            img, Vilib.detect_obj_parameter['body_joints'] = DetectPose().work(image=img)   
        return img