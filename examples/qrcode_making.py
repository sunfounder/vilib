#!/usr/bin/env python3
from time import sleep
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    sleep(1)

    Vilib.display_qrcode()

    while True:
        # https://github.com/lincolnloop/python-qrcode
        Vilib.make_qrcode("Hello world !", # data
                path='qrcode_out.png', # save path
                version=1,
                box_size=10,
                border=4,
                fill_color=(132, 112, 255),
                back_color=(255, 255, 255)
                )
        sleep(3)
        Vilib.make_qrcode("Peace to the world.", 
                path='qrcode_out2.png',
                version=1,
                box_size=10,
                border=4,
                fill_color=(132, 112, 255),
                back_color=(225, 255, 255)
                )
        sleep(3)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()
