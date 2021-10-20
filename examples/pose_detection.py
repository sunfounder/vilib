import os
from vilib import Vilib


def main():
    
    Vilib.camera_start(inverted_flag=True)
    Vilib.display(local=True,web=True)
    Vilib.pose_detect_switch(True)

if __name__ == "__main__":
    main()
