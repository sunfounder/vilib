#!/usr/bin/env python3
from vilib import Vilib
from time import sleep

'''
Vilib.qrcode_detect_switch(flag=True)     # True / False

Vilib.qrcode_obj_parameter['x']       # the largest block center x-axis coordinate
Vilib.qrcode_obj_parameter['y']       # the largest block center y-axis coordinate
Vilib.qrcode_obj_parameter['w']       # the largest block pixel width
Vilib.qrcode_obj_parameter['h']       # the largest block pixel height
Vilib.qrcode_obj_parameter['data']    # recognition result
  
'''

def main():
    Vilib.camera_start(vflip=False, hflip=False) # size=(640, 480)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    Vilib.qrcode_detect_switch(True)
    sleep(1)

    while True:
        texts = [x['text'] for x in Vilib.detect_obj_parameter['qr_list']]
        if len(texts)>0:
            print(", ".join(texts))
        else:
            print("None")
        sleep(0.5)  


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()

