#!/usr/bin/env python3
import time
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)

    path = "/home/pi/Pictures/vilib/photos"
  
    while True:
        if input() == 'q': 
            _time = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())
            status = Vilib.take_photo(str(_time),path)
            if status:
                print("The photo save as:%s/%s.jpg"%(path, _time))
            else:
                print("Photo save failed")
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()

    