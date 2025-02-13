from vilib import Vilib
from libcamera import controls
import time

'''
More to see Picamera2 Manual "Chapter 5. Camera controls and properties"
and "Appendix C: Camera controls"

https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf


## get picam2 instance
   picam2 = Vilib.get_instance()
or
   picam2 = Vilib.picam2

'''
def main():
    Vilib.camera_start(vflip=False, hflip=False, size=(1280, 720))
    Vilib.show_fps()
    Vilib.display(local=True, web=True) 

    time.sleep(3)
    Vilib.set_controls({"AwbMode": controls.AwbModeEnum.Cloudy})
    time.sleep(3)
    Vilib.set_controls({"AwbMode": controls.AwbModeEnum.Fluorescent})
    time.sleep(3)
    Vilib.set_controls({"AwbMode": controls.AwbModeEnum.Auto})

    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()
