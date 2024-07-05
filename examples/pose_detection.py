#!/usr/bin/env python3
from vilib import Vilib


def main():
    
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    Vilib.pose_detect_switch(True)

if __name__ == "__main__":
    main()


