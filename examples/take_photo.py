import time
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display()

    i = 0
    path = "/home/pi/picture/vilib/photos"
  
    while True:
        if input() == 'q': 
            _time = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())
            Vilib.take_photo(str(_time),path)
            print("take_photo:%s.jpg"%_time)
            time.sleep(0.1)


if __name__ == "__main__":
    main()