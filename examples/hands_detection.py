#!/usr/bin/env python3
from time import sleep
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    Vilib.hands_detect_switch(True)

    # while True:
    #     print(Vilib.detect_obj_parameter['hands_joints']) # Print finger joint coordinates
    #     sleep(0.5)

if __name__ == "__main__":
    main()

