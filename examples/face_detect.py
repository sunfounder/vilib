#!/usr/bin/env python3
from vilib import Vilib
from time import sleep

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    Vilib.face_detect_switch(True)
    sleep(1)

    while True:
        n = Vilib.detect_obj_parameter['human_n'] 
        print("%s faces are found."%n)   
        sleep(1)

if __name__ == "__main__":
    main()

    
