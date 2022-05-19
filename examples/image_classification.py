#!/usr/bin/env python3
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    # You can use the following two functions to load the model and the corresponding label
    # Vilib.image_classify_set_model(path='/opt/vilib/mobilenet_v1_0.25_224_quant.tflite')
    # Vilib.image_classify_set_labels(path='/opt/vilib/labels_mobilenet_quant_v1_224.txt')
    Vilib.image_classify_switch(True)

if __name__ == "__main__":
    main()

