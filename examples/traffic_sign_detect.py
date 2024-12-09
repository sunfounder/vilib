#!/usr/bin/env python3
from vilib import Vilib
from time import sleep

'''
Vilib.traffic_detect_switch(flag=True)     # True / False

Vilib.traffic_sign_obj_parameter['x']       # the largest traffic sign block center x-axis coordinate
Vilib.traffic_sign_obj_parameter['y']       # the largest traffic sign block center y-axis coordinate
Vilib.traffic_sign_obj_parameter['w']       # the largest traffic sign block pixel width
Vilib.traffic_sign_obj_parameter['h']       # the largest traffic sign block pixel height
Vilib.traffic_sign_obj_parameter['t']       # traffic sign text, could be: 'none', 'stop','right','left','forward'
Vilib.traffic_sign_obj_parameter['acc']     # accuracy
  
'''

def main():

    Vilib.camera_start(vflip=False, hflip=False) # , size=(640, 480)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    Vilib.traffic_detect_switch(True)
    sleep(1)

    while True:
        t = Vilib.traffic_sign_obj_parameter['t']
        if t != 'none':
            x = Vilib.traffic_sign_obj_parameter['x']
            y = Vilib.traffic_sign_obj_parameter['y']
            w = Vilib.traffic_sign_obj_parameter['w']
            h = Vilib.traffic_sign_obj_parameter['h']
            acc = Vilib.traffic_sign_obj_parameter['acc']

            print(f"{t} ({acc}%), coordinate=({x}, {y}), size={w}*{h}")
        else:
            print(f'No traffic sign found')
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

    