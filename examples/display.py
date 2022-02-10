#!/usr/bin/env python3
from vilib import Vilib

def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    print('\npress Ctrl+C to exit')
    
if __name__ == "__main__":
    main()