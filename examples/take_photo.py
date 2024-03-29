#!/usr/bin/env python3
import time
from vilib import Vilib
import os
user = os.getlogin()
user_home = os.path.expanduser(f'~{user}')

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)

    path =f"{user_home}/Pictures/vilib/photos"
  
    while True:
        if input() == 'q': 
            _time = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())
            Vilib.take_photo(str(_time),path)
            print("The photo save as:%s/%s.jpg"%(path, _time))
            time.sleep(0.1)


if __name__ == "__main__":
    main()


    