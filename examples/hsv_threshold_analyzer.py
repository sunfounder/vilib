import os
if 'DISPLAY' not in os.environ.keys():
    print('No display found. Please run on desktop environment.')
    exit(0)
import sys
import cv2
import time

model = "img" # "img" or "video"
if len(sys.argv) > 1:
    model = "img"
    img_path = sys.argv[1]
else:
    model = "video"
    from vilib import Vilib

h_low = 127
h_high = 255
s_low = 0
s_high = 255
v_low = 0
v_high = 255

window_name = 'HSV Threshold Analyzer'

def on_h_low_change(value):
    global h_low
    h_low = value

def on_h_high_change(value):
    global h_high
    h_high = value

def on_s_low_change(value):
    global s_low
    s_low = value

def on_s_high_change(value):
    global s_high
    s_high = value

def on_v_low_change(value):
    global v_low
    v_low = value

def on_v_high_change(value):
    global v_high
    v_high = value

def main():
    img = None

    if model == "img":
        img = cv2.imread(img_path)
        cv2.imshow("Original", img)
    else:
        from vilib import Vilib

        Vilib.camera_start(vflip=False, hflip=False, size=(640, 480))
        Vilib.display(local=False, web=False)

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.createTrackbar('H_Low', window_name, h_low, 255, on_h_low_change)
    cv2.createTrackbar('H_High', window_name, h_high, 255, on_h_high_change)
    cv2.createTrackbar('S_Low', window_name, s_low, 255, on_s_low_change)
    cv2.createTrackbar('S_High', window_name, s_high, 255, on_s_high_change)
    cv2.createTrackbar('V_Low', window_name, v_low, 255, on_v_low_change)
    cv2.createTrackbar('V_High', window_name, v_high, 255, on_v_high_change)
    cv2.resizeWindow(window_name, 480, 600)
    cv2.moveWindow(window_name, 20, 80)

    while True:
        if model == "video":
            img  = Vilib.img
            if len(img) < 2:
                time.sleep(0.1)
                continue
            cv2.imshow("Original", img)
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, (h_low, s_low, v_low), (h_high, s_high, v_high))
        cv2.imshow(window_name, mask)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()


