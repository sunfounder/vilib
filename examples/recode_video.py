from time import sleep,strftime,localtime
from vilib import Vilib

# region  read keyboard 
import sys
import tty
import termios

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

manual = '''
Press keys on keyboard to record value!
    Q: record/pause/continue
    E: stop
    G: Quit
'''
# endregion


Vilib.rec_video_set["path"] = "/home/pi/video/"
vname = strftime("%Y-%m-%d-%H.%M.%S", localtime())
Vilib.rec_video_set["name"] = vname
rec_flag = 'stop' # start,pause,stop
# endregion init

# rec control
def rec_control(key):
    global rec_flag
    
    if key == 'q' and rec_flag == 'stop':
        key = None
        rec_flag = 'start'
        Vilib.rec_video_run()
        print('rec start ...')
    if key == 'q' and rec_flag == 'start':
        key = None
        rec_flag = 'pause'
        Vilib.rec_video_pause()
        print('pause')
    if key == 'q' and rec_flag == 'pause':
        key = None
        rec_flag = 'start'
        Vilib.rec_video_start()
        print('continue')    

    if key == 'e' and rec_flag != 'stop':
        Vilib.rec_video_stop()
        print('stop')
        print("The video saved as %s%s.avi"%(Vilib.rec_video_set["path"],vname))  



def main():

    Vilib.camera_start(vflip=False,hflip=False) 
    Vilib.display(local=True,web=True)

    print(manual)
    while True:
        key = readchar()
        # rec control
        rec_control(key)
        # esc
        if key == 'g':
            Vilib.camera_close()
            break 

        sleep(0.1)

if __name__ == "__main__":
    main()