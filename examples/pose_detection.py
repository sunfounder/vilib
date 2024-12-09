#!/usr/bin/env python3
from vilib import Vilib
from time import sleep

def main():
    
    Vilib.camera_start(vflip=False, hflip=False) # size=(640, 480)
    Vilib.show_fps()
    Vilib.display(local=True,web=True)
    Vilib.pose_detect_switch(True)
    sleep(1)

    while True: # Keep the main program running
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


