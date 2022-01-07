#!/usr/bin/env python3
import os, sys

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
    # pyzbar:one-dimensional barcodes and QR codes 
    "libzbar0",
]

PIP_INSTALL_LIST = [
    "Flask",
    "imutils",
    "mediapipe-rpi3",
    # install tflite_runtime
    # "https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl"
    "./tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl",
    # "face-recognition",
    # pyzbar:one-dimensional barcodes and QR codes 
    "pyzbar",
    "pyzbar[scripts]",
]


def install():
    options = []
    if len(sys.argv) > 1:
        options = sys.argv[1:]
        for o in options:
            if o not in avaiable_options:
                print("Option {} is not found.".format(o))
                print(usage)
                quit()
        if "-h" in options or "--help" in options:
            print(usage)
            quit()

    print("vilib install process starts")
    if "--no-dep" not in options:    
        do(msg="update apt",
            cmd='sudo apt update -y')
        # do(msg="upgrade apt",
        #     cmd='sudo apt upgrade -y')

        print("Install dependency")
        for dep in APT_INSTALL_LIST:
            do(msg="install %s"%dep,
                cmd='sudo apt install %s -y'%dep)
        for dep in PIP_INSTALL_LIST:
            do(msg="install %s"%dep,
                cmd='sudo pip3 install %s'%dep)

    print("Create workspace")
    _, result = run_command("ls /opt")
    if "vilib" not in result:
        do(msg="create dir",
            cmd='sudo mkdir /opt/vilib')
        do(msg="copy workspace",
            cmd='sudo cp -r ./workspace/* /opt/vilib/')
        do(msg="add write permission to log file",
            cmd='sudo chmod 666 /opt/vilib/log')

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


def do(msg="", cmd=""):
    print(" - %s... " % (msg), end='', flush=True)
    status, result = run_command(cmd)
    # print(status, result)
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
