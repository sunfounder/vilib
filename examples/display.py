#!/usr/bin/env python3
from vilib import Vilib
import time

def main():
    # Vilib.camera_start(vflip=False, hflip=False) # vflip:vertical flip, hflip:horizontal Flip, size=(640, 480)
    Vilib.camera_start(vflip=False, hflip=False, size=(1280, 720))

    Vilib.show_fps()
    '''
    Vilib.show_fps(color=(0, 255, 0), fps_size=0.68, fps_origin=(10, 20))
    
    color: fps font color, (r, g, b)
    fps_size, font size
    fps_origin, origin position, (width, height)

    Vilib.hide_fps() # Hide the FPS
    '''

    Vilib.display(local=True, web=True) 
    '''
    local:local display, web:web display
    when local=True, the image window will be displayed on the system desktop
    when web=True, the image window will be displayed on the web browser at http://localhost:9000/mjpg
    '''

    print('\npress Ctrl+C to exit')


    while True:
        # do something
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()


