from vilib import Vilib

def main():
    Vilib.camera_start(inverted_flag=True)
    Vilib.display(imshow=True,web=True)
    Vilib.gesture_detect_switch(True)

if __name__ == "__main__":
    main()