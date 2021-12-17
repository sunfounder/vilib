from time import sleep
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    Vilib.hands_detect_switch(True)

    while True:
        print(Vilib.detect_obj_parameter['hands_joints'])
        sleep(1)

if __name__ == "__main__":
    main()