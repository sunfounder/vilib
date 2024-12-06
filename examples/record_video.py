#!/usr/bin/env python3
from time import sleep,strftime,localtime
from vilib import Vilib
import readchar 
import os

user_name = os.getlogin()

manual = '''
Press keys on keyboard to control recording:
    Q: record/pause/continue
    E: stop
    ESC: Quit
'''

def print_overwrite(msg,  end='', flush=True):
    print('\r\033[2K', end='',flush=True)
    print(msg, end=end, flush=True)

def main():
    rec_flag = 'stop' # start,pause,stop
    vname = None
    Vilib.rec_video_set["path"] = f"/home/{user_name}/Videos/" # set path

    Vilib.camera_start(vflip=False, hflip=False, size=(1280, 720)) # default size = (640, 480)
    Vilib.display(local=True,web=True)
    sleep(0.8)  # wait for startup
    Vilib.rec_video_set["framesize"] = (1280, 720)

    print(manual)
    while True:
        # read keyboard
        key = readchar.readkey().lower()
        # start,pause
        if key == 'q':
            key = None
            if rec_flag == 'stop':            
                rec_flag = 'start'
                # set name
                vname = strftime("%Y-%m-%d-%H.%M.%S", localtime())
                Vilib.rec_video_set["name"] = vname
                # start record
                Vilib.rec_video_run()
                Vilib.rec_video_start()
                print_overwrite('rec start ...')
            elif rec_flag == 'start':
                rec_flag = 'pause'
                Vilib.rec_video_pause()
                print_overwrite('pause')
            elif rec_flag == 'pause':
                rec_flag = 'start'
                Vilib.rec_video_start()
                print_overwrite('continue')
        # stop       
        elif key == 'e' and rec_flag != 'stop':
            key = None
            rec_flag = 'stop'
            Vilib.rec_video_stop()
            print_overwrite("The video saved as %s%s.avi"%(Vilib.rec_video_set["path"],vname),end='\n')  
        # quit
        elif key == readchar.key.CTRL_C or key in readchar.key.ESCAPE_SEQUENCES:
            Vilib.camera_close()
            print('\nquit')
            break 

        sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()


