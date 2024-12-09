#!/usr/bin/env python3
from vilib import Vilib
from time import sleep


def main():
    Vilib.camera_start(vflip=False, hflip=False) # size=(640, 480)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)

    # You can use the following two functions to load the model and the corresponding label
    # Vilib.image_classify_set_model(path='/opt/vilib/mobilenet_v1_0.25_224_quant.tflite')
    # Vilib.image_classify_set_labels(path='/opt/vilib/labels_mobilenet_quant_v1_224.txt')

    Vilib.image_classify_switch(True)
    sleep(1)

    while True:
        name = Vilib.image_classification_obj_parameter['name']
        acc = Vilib.image_classification_obj_parameter['acc']
        print(f'{name} {acc:.3f}')
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
