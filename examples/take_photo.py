from time import sleep
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display()

    i = 0
    path = "/home/pi/picture/test/"
  
    while True:
        if input() == 'q': 
            i += 1 
            Vilib.take_photo('photo'+str(i),path)
            print("take_photo",i)
            sleep(0.1)


if __name__ == "__main__":
    main()