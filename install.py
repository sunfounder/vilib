#!/usr/bin/env python3
import os, sys
import time
import threading

# version
# =================================================================
sys.path.append('./vilib')
user_name = os.getlogin()
from version import __version__
print("Start installing vilib %s for user %s"%(__version__ ,user_name))

# define color print
# =================================================================
def warn(msg, end='\n', file=sys.stdout, flush=False):
    print(f'\033[0;33m{msg}\033[0m', end=end, file=file, flush=flush)

def error(msg, end='\n', file=sys.stdout, flush=False):
    print(f'\033[0;31m{msg}\033[0m', end=end, file=file, flush=flush)

# run_command
# =================================================================
def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result

# check if run as root
# =================================================================
if os.geteuid() != 0:
    warn("Script must be run as root. Try \"sudo python3 install.py\".")
    sys.exit(1)

# global variables defined
# =================================================================
errors = []

avaiable_options = ['-h', '--help', '--no-dep']

usage = '''
Usage:
    sudo python3 install.py [option]

Options:
               --no-dep    Do not download dependencies
    -h         --help      Show this help text and exit
'''

# utils
# =================================================================
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
            sys.stdout.write('\033[?25l') # cursor invisible
            sys.stdout.write('%s\033[1D'%char[i])
            sys.stdout.flush()
            time.sleep(0.5)

    sys.stdout.write(' \033[1D')
    sys.stdout.write('\033[?25h') # cursor visible 
    sys.stdout.flush()

def do(msg="", cmd=""):
    print(" - %s ... " % (msg), end='', flush=True)
    # at_work_tip start 
    global at_work_tip_sw
    at_work_tip_sw = True
    _thread = threading.Thread(target=working_tip)
    _thread.daemon = True
    _thread.start()
    # process run
    status, result = run_command(cmd)
    # print(status, result)
    # at_work_tip stop
    at_work_tip_sw = False
    while _thread.is_alive():
        time.sleep(0.01)
    # status
    if status == 0 or status == None or result == "":
        print('Done')
    else:
        print('\033[1;35mError\033[0m')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))

def check_rpi_model():
    _, result = run_command("cat /proc/device-tree/model |awk '{print $3}'")
    result = result.strip()
    if result == '3':
        return 3
    elif result == '4':
        return 4
    else:
        return None

def check_raspbain_version():
    _, result = run_command("cat /etc/debian_version|awk -F. '{print $1}'")
    return result.strip()

def check_python_version():
    import sys
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro
    return major, minor, micro

def reset_echo_and_exit(exit_code):
    sys.stdout.write('\033[?25h') # cursor visible 
    sys.stdout.flush()
    sys.exit(exit_code)

def check_machine_type():
    import platform
    return platform.machine()

def check_os_bits():
    _, result = run_command("getconf LONG_BIT")
    return result.strip()

# check platform
# =================================================================
''' Attention
The new 32-bit raspbian system uses the 64-bit kernel by default on the pi4.
'''
os_bit = int(check_os_bits())
machine_type = check_machine_type()

if machine_type not in ['armv7l', 'aarch64']:
    error(f"Platform [{machine_type}] is not supported.")
    reset_echo_and_exit(1)

if os_bit != 32:
    # picamera not supported on 64-bit systems
    warn(f"The picamera only supports 32-bit systems, please change to Please \"picamera2\" branch.")
    print(f"Please see: https://github.com/sunfounder/vilib/tree/picamera2")
    reset_echo_and_exit(1)

# print system and hardware information
# =================================================================
rpi_model = check_rpi_model()
python_version = check_python_version()
raspbain_version = check_raspbain_version()

print(f"Python version: {python_version[0]}.{python_version[1]}.{python_version[2]}")
print(f"Raspbian version: {raspbain_version} ({os_bit}bit)")
print("")

# Dependencies list installed with apt
# =================================================================
APT_INSTALL_LIST = [ 
    # install python3-picamera: https://picamera.readthedocs.io/en/release-1.13/install.html
    "python3-picamera",
    # install python3-opencv: https://docs.opencv.org/4.x/d2/de6/tutorial_py_setup_in_ubuntu.html
    "python3-opencv",
    "opencv-data",
    # install ffmpeg
    "ffmpeg",
    # install python3-tflite-runtime: https://github.com/tensorflow/tensorflow/blob/v2.5.0/tensorflow/lite/g3doc/guide/python.md#install-tensorflow-lite-for-python
    "python3-tflite-runtime", 
]


# if raspbain_version == "10":
#     APT_INSTALL_LIST.append("libopenexr23")
# elif raspbain_version == "11":
#     APT_INSTALL_LIST.append("libopenexr25")
    
# Dependencies list installed with pip3
# =================================================================
PIP_INSTALL_LIST = [
    "Flask",
    "imutils",
    "pyzbar", # pyzbar:one-dimensional barcodes and QR codes
    "pyzbar[scripts]",
    'protobuf>=3.20.0', # mediapipe need 
    "readchar", # will update setuptools to the latest version
    "\'setuptools>59.0,<60.0\'", # The default installation location will change after setuptools version 60.0
]

# ---- select mediapipe version ----
# =================================================================
'''
mediapipe-rpi4 / mediapipe-rpi3 -> 32bit python37
mediapipe -> 64bit python38, 39, 310, 311
picamera -> 32bit
picamera2 ->  32bit / 64bit
'''
is_compatible_mediapipe = False

# if python37 & 32bit OS
if python_version[0] == 3 and python_version[1] == 7 and os_bit == 32:
    is_compatible_mediapipe = True
    if rpi_model == 4:
        PIP_INSTALL_LIST.append("mediapipe-rpi4")
    else:
        PIP_INSTALL_LIST.append("mediapipe-rpi3")

# install mediapipe dependencies
APT_Mediapipe_Dependencies = [
    "python3-matplotlib",
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
    "libzbar0",
]

if raspbain_version == "10":
    APT_Mediapipe_Dependencies.append("libopenexr23")
elif raspbain_version == "11":
    APT_Mediapipe_Dependencies.append("libopenexr25")

# main function
# =================================================================
def install():
    options = []
    if len(sys.argv) > 1:
        options = sys.argv[1:]
        for opt in options:
            if opt not in avaiable_options:
                print("Option {} is not found.".format(opt))
                print(usage)
                return
        if "-h" in options or "--help" in options:
            print(usage)
            return

    if "--no-dep" not in options:
        # ----- install dependencies with apt -----
        print("apt install dependencies:")
        # add repo list and key for tflite-runtime
        do(msg="add repo list and key for tflite-runtime",
            cmd='echo \"deb https://packages.cloud.google.com/apt coral-edgetpu-stable main\" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list'
            + ' && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -'
        )
        do(msg="dpkg configure",
            cmd='dpkg --configure -a')  
        do(msg="update apt-get",
            cmd='apt-get update -y')
        for dep in APT_INSTALL_LIST:
            do(msg=f"install {dep}",
                cmd=f'apt-get install {dep} -y')
                # print
        if is_compatible_mediapipe:
            print('apt install mediapipe dependencies:')
            for dep in APT_Mediapipe_Dependencies:
                do(msg=f"install {dep}",
                    cmd=f'apt-get install {dep} -y')

        # ----- install dependencies with pip -----
        print("pip3 install dependencies:")
        for dep in PIP_INSTALL_LIST:
            do(msg=f"install {dep}",
                cmd=f'pip3 install {dep}')

    print("Create workspace")
    if not os.path.exists('/opt'):
        os.mkdir('/opt')
        run_command('sudo chmod 774 /opt')
        run_command('sudo chown -R %s:%s /opt'%(user_name, user_name))
    do(msg="create dir",
        cmd='sudo mkdir -p /opt/vilib'
        + ' && sudo chmod 774 /opt/vilib'
        + ' && sudo chown -R %s:%s /opt/vilib'%(user_name, user_name)
        )
    do(msg="copy workspace",
        cmd='sudo cp -r ./workspace/* /opt/vilib/'
        + ' && sudo chmod 774 /opt/vilib/*'
        + ' && sudo chown -R %s:%s /opt/vilib/*'%(user_name, user_name)
        )
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


if __name__ == "__main__":
    try:
        install()
    except KeyboardInterrupt:
        print("Canceled.")
    finally:
        sys.stdout.write('\033[?25h') # cursor visible 
        sys.stdout.flush()
