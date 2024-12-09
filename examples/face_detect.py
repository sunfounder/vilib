#!/usr/bin/env python3
from vilib import Vilib
from time import sleep

'''
Vilib.face_detect_switch(True)     # True / False

Vilib.face_obj_parameter['x']      # the largest face block center coordinate 
Vilib.face_obj_parameter['y']      # the largest face block center coordinate 
Vilib.face_obj_parameter['w']      # the largest face block pixel width 
Vilib.face_obj_parameter['h']      # the largest face block pixel height 
Vilib.face_obj_parameter['n']      # Number of face blocks found 
  
'''

def main():
    Vilib.camera_start(vflip=False, hflip=False) # size=(640, 480)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    Vilib.face_detect_switch(True)
    sleep(1)

    while True:
        n = Vilib.face_obj_parameter['n']
        if n != 0:
            x = Vilib.face_obj_parameter['x']
            y = Vilib.face_obj_parameter['y']
            w = Vilib.face_obj_parameter['w']
            h = Vilib.face_obj_parameter['h']
            print(f"{n} faces found, the largest block coordinate=({x}, {y}), size={w}*{h}")
        else:
            print(f'No face found')
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


    
