#!/usr/bin/env python3
import os, sys
import time
import threading

errors = []

avaiable_options = ['-h', '--help', '--no-dep']

usage = '''
Usage:
    sudo python3 install.py [option]

Options:
               --no-dep    Do not download dependencies
    -h         --help      Show this help text and exit
'''


APT_INSTALL_LIST = [ 
    # Python3 package management tool
    # "python3-pip",        # 
    # "python3-setuptools",

    # install compilation tools
    "cmake",
    "gcc",
    "g++",
    # install numpy
    "python3-numpy",
    # GTK support for GUI features, Camera support (v4l), Media Support (ffmpeg, gstreamer) etc
    # https://docs.opencv.org/4.x/d2/de6/tutorial_py_setup_in_ubuntu.html   
    "libavcodec-dev", 
    "libavformat-dev ",
    "libswscale-dev",
    "libgstreamer-plugins-base1.0-dev", 
    "libgstreamer1.0-dev",
    "libgtk2.0-dev",
    "libgtk-3-dev",
    # update image format support library
    "libpng-dev",
    "libjpeg-dev",
    "libopenexr-dev",
    "libtiff-dev",
    "libwebp-dev",
    # install python3-opencv
    "python3-opencv", 
    # install additional dependencies for opencv
    "libjasper-dev",
    "libqtgui4", # --------
    "libqt4-test",
    # install python3-picamera
    "python3-picamera",
    # install mediapipe-rpi3 dependency
    "ffmpeg", 
    "libgtk-3-0",
    "libxcb-shm0",
    "libcdio-paranoia-dev", 
    "libsdl2-2.0-0", 
    "libxv1",  
    "libtheora0", 
    "libva-drm2", 
    "libva-x11-2", 
    "libvdpau1", 
    "libharfbuzz0b", 
    "libbluray2", 
    "libatlas-base-dev",
    "libhdf5-103", 
    "libdc1394-22", 
    "libopenexr23", 
    "libzbar0",
]

PIP_INSTALL_LIST = [
    "Flask",
    "imutils",
    "mediapipe-rpi3",
    # install tflite_runtime
    # https://github.com/google-coral/pycoral/releases/
    # "https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl"
    "./tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl",
    # "./tflite_runtime-2.5.0.post1-cp39-cp39-linux_armv7l.whl",
    "pyzbar", # pyzbar:one-dimensional barcodes and QR codes
    "pyzbar[scripts]",
]


def install():
    options = []
    if len(sys.argv) > 1:
        options = sys.argv[1:]
        for opt in options:
            if opt not in avaiable_options:
                print("Option {} is not found.".format(opt))
                print(usage)
                quit()
        if "-h" in options or "--help" in options:
            print(usage)
            quit()

    print("vilib install process starts")
    if "--no-dep" not in options:  
        do(msg="dpkg configure",
            cmd='sudo dpkg --configure -a')  
        do(msg="update apt-get",
            cmd='sudo apt-get update -y')

        print("Install dependency")
        for dep in APT_INSTALL_LIST:
            do(msg="install %s"%dep,
                cmd='sudo apt-get install %s -y'%dep)
        for dep in PIP_INSTALL_LIST:
            do(msg="install %s"%dep,
                cmd='sudo pip3 install %s'%dep)

    print("Create workspace")
    if not os.path.exists('/opt'):
        os.mkdir('/opt')
        os.popen('sudo chmod 774 /opt')
    do(msg="create dir",
        cmd='sudo mkdir -p /opt/vilib')
    do(msg="copy workspace",
        cmd='sudo cp -r ./workspace/* /opt/vilib/')
    do(msg="add write permission to log file",
        cmd='sudo touch /opt/vilib/log && sudo chmod 774 /opt/vilib/log')

    print("Install vilib python package")
    do(msg="run setup file",
        cmd='sudo python3 setup.py install')
    do(msg="cleanup",
        cmd='sudo rm -rf vilib.egg-info')

    # check errors
    if len(errors) == 0:
        print("Finished")
    else:
        print("\n\nError happened in install process:")
        for error in errors:
            print(error)
        print("Try to fix it yourself, or contact service@sunfounder.com with this message")
        sys.exit(1)


def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result


at_work_tip_sw = False
def working_tip():
    char = ['/', '-', '\\', '|']
    i = 0
    global at_work_tip_sw
    while at_work_tip_sw:  
            i = (i+1)%4 
            sys.stdout.write('%s\033[1D'%char[i])
            sys.stdout.flush()
            time.sleep(0.5)

    sys.stdout.write(' \033[1D')
    sys.stdout.flush()    
        

def do(msg="", cmd=""):
    print(" - %s... " % (msg), end='', flush=True)
    # at_work_tip start 
    global at_work_tip_sw
    at_work_tip_sw = True
    _thread = threading.Thread(target=working_tip)
    _thread.setDaemon(True)
    _thread.start()
    # process run
    status, result = run_command(cmd)
    # print(status, result)
    # at_work_tip stop
    at_work_tip_sw = False
    while _thread.isAlive():
        time.sleep(0.1)
    # status
    if status == 0 or status == None or result == "":
        print('Done')
    else:
        print('Error')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))


if __name__ == "__main__":
    try:
        install()
    except KeyboardInterrupt:
        print("Canceled.")
