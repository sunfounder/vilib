#!/usr/bin/env python3
from vilib import Vilib
from time import sleep

'''
Vilib.color_detect(color="red")     # red, green, blue, yellow , orange, purple

Vilib.color_obj_parameter['color']  # color name
Vilib.color_obj_parameter['x']      # the largest color block center coordinate 
Vilib.color_obj_parameter['y']      # the largest color block center coordinate 
Vilib.color_obj_parameter['w']      # the largest color block pixel width 
Vilib.color_obj_parameter['h']      # the largest color block pixel height 
Vilib.color_obj_parameter['n']      # Number of color blocks found 
  
Vilib.close_color_detection()
'''

def main():

    Vilib.camera_start(vflip=False, hflip=False) # size=(640,, 480)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    Vilib.color_detect(color="red")  # red, green, blue, yellow , orange, purple
    sleep(1)

    while True:
        n = Vilib.color_obj_parameter['n']
        color = Vilib.color_obj_parameter['color']
        if n != 0:
            x = Vilib.color_obj_parameter['x']
            y = Vilib.color_obj_parameter['y']
            w = Vilib.color_obj_parameter['w']
            h = Vilib.color_obj_parameter['h']
            print(f"{n} {color} blocks found, the largest block coordinate=({x}, {y}), size={w}*{h}")
        else:
            print(f'No {color} block found')
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

    