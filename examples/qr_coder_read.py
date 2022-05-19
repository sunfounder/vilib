#!/usr/bin/env python3
from vilib import Vilib
from time import sleep


def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    Vilib.qrcode_detect_switch(True)
    
    while True:
        text = Vilib.detect_obj_parameter['qr_data'] 
        print(text)
        sleep(0.5)  
            
if __name__ == "__main__":
    main()
    
    
    
 