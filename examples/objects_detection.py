#!/usr/bin/env python3
from vilib import Vilib
from time import sleep


def main():
    Vilib.camera_start(vflip=False, hflip=False) # size=(640, 480)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    sleep(1)

    # You can use the following two functions to load the model and the corresponding label
    # Vilib.object_detect_set_model(path='/opt/vilib/detect.tflite')
    # Vilib.object_detect_set_labels(path='/opt/vilib/coco_labels.txt')

    Vilib.object_detect_switch(True)

    while True: # Keep the main program running
        print(Vilib.object_detection_list_parameter)
        print() # new line
        sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()

