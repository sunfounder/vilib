#!/usr/bin/env python3
from time import sleep
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False, hflip=False) # size=(640, 480)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    Vilib.hands_detect_switch(True)
    sleep(1)

    while True: 
        # print(Vilib.detect_obj_parameter['hands_joints']) # Print finger joint coordinates
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

