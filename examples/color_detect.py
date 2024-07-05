#!/usr/bin/env python3
from vilib import Vilib
from time import sleep


def main():

    Vilib.camera_start(vflip=False,hflip=False) #
    Vilib.display(local=True,web=True)
    Vilib.color_detect(color="red")  # red, green, blue, yellow , orange, purple
    sleep(1)
    # Vilib.detect_obj_parameter['color_x']    # Maximum color block center coordinate x
    # Vilib.detect_obj_parameter['color_y']    # Maximum color block center coordinate x
    # Vilib.detect_obj_parameter['color_w']    # Maximum color block pixel width
    # Vilib.detect_obj_parameter['color_h']    # Maximum color block pixel height
    # Vilib.detect_obj_parameter['color_n']    # Number of color blocks found

    while True:
        n = Vilib.detect_obj_parameter['color_n'] 
        print("%s color blocks are found"%n, end=',', flush=True)
        if n != 0:   
            w = Vilib.detect_obj_parameter['color_w']
            h = Vilib.detect_obj_parameter['color_h']
            print("the maximum color block pixel size is %s*%s"%(w,h))
        else:
            print('') # new line
        sleep(0.5)



if __name__ == "__main__":
    main()


    