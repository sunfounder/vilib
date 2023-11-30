#!/usr/bin/env python3
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False,hflip=False) # vflip:vertical flip, hflip:horizontal Flip
    # local:local display, web:web display
    # when local=True, the image window will be displayed on the system desktop
    # when web=True, the image window will be displayed on the web browser at http://localhost:9000/mjpg
    Vilib.display(local=True,web=True) 
    print('\npress Ctrl+C to exit')
    
if __name__ == "__main__":
    try:
        main()
        while True:
            pass
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()


