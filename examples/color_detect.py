from vilib import Vilib

def main():
    Vilib.camera_start()
    Vilib.display()
    Vilib.color_detect("red")

if __name__ == "__main__":
    main()