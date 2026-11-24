#!/usr/bin/env python3
import os, sys
import time
import threading

# version
# =================================================================
sys.path.append('./vilib')

import pwd
owner_uid = os.stat(__file__).st_uid
user_name = pwd.getpwuid(owner_uid).pw_name

from version import __version__
print("Start installing vilib %s for user %s"%(__version__ ,user_name))

# define color print
# =================================================================
def warn(msg, end='\n', file=sys.stdout, flush=False):
    print(f'\033[0;33m{msg}\033[0m', end=end, file=file, flush=flush)

def error(msg, end='\n', file=sys.stdout, flush=False):
    print(f'\033[0;31m{msg}\033[0m', end=end, file=file, flush=flush)

# check if run as root
# =================================================================
if os.geteuid() != 0:
    warn("Script must be run as root. Try \"sudo python3 install.py\".")
    sys.exit(1)

# global variables defined
# =================================================================
errors = []

avaiable_options = ['-h', '--help', '--no-dep', '--all']

usage = '''
Usage:
    sudo python3 install.py [option]

Options:
               --all       Install everything, including the optional AI
                           dependencies (mediapipe, tflite-runtime). Only
                           products that use hands / pose / object detection
                           or image classification need this.
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
        return int(3)
    elif result == '4':
        return int(4)
    else:
        return None

def check_raspbain_version():
    _, result = run_command("cat /etc/debian_version|awk -F. '{print $1}'")
    result = result.strip()
    if result.isdigit():
        return int(result.strip())

    # Ubuntu compatibility
    codename = result.split("/")[0]

    _, result = run_command(
        f"curl -fsSL https://deb.debian.org/debian/dists/{codename}/Release "
        "| awk -F': ' '$1 == \"Version\" {print $2; exit}'"
    )

    version = result.strip().split('.')[0]
    
    if version.isdigit():
        return int(version)

    raise RuntimeError(
        f"Unable to determine Debian version from https://deb.debian.org/debian/dists/{codename}/Release: {result.strip()}'"
    )

def check_python_version():
    import sys
    major = int(sys.version_info.major)
    minor = int(sys.version_info.minor)
    micro = int(sys.version_info.micro)
    return major, minor, micro

def check_os_bit():
    '''
    # import platform
    # machine_type = platform.machine() 
    latest bullseye uses a 64-bit kernel
    This method is no longer applicable, the latest raspbian will uses 64-bit kernel 
    (kernel 6.1.x) by default, "uname -m" shows "aarch64", 
    but the system is still 32-bit.
    '''
    _ , os_bit = run_command("getconf LONG_BIT")
    return int(os_bit)

# print system and hardware information
# =================================================================
rpi_model = check_rpi_model()
python_version = check_python_version()
raspbain_version = check_raspbain_version()
os_bit = check_os_bit()

print(f"Python version: {python_version[0]}.{python_version[1]}.{python_version[2]}")
print(f"Raspbian version: {raspbain_version} ({os_bit}bit)")
print("")

# check system
# =================================================================
if raspbain_version <= 10:
    warn('System not be supported.Requires system in bullseye(11) or newer.')
    print('Please use newer system or use "legacy" branch.')
    sys.exit(1)

# Dependencies list installed with apt
# =================================================================
# Base dependencies: needed by every product.
APT_INSTALL_LIST = [ 
    "python3-libcamera",
    # install python3-picamera2: https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
    "python3-picamera2",
    "rpicam-apps",
    "python3-pyqt5",
    "python3-opengl",
    # install python3-opencv: # https://qengineering.eu/install-opencv-4.5-on-raspberry-64-os.html
    "python3-opencv",
    "opencv-data",
    # install ffmpeg
    "ffmpeg", 
    # pyzbar (QR code / barcode recognition) needs the zbar shared library
    # (Debian 13 provides it through libzbar0t64, the old name still resolves)
    "libzbar0",
]

# Optional dependencies: only needed by the AI packages (mediapipe / tflite-runtime).
# They are installed only when install.py is run with "--all", and only for the
# package that this system can actually run, see prepare_optional_deps().
MEDIAPIPE_APT_INSTALL_LIST = [
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
    "libopenblas-dev",
]

TFLITE_APT_INSTALL_LIST = [
    # ATLAS was dropped in Debian 13; the tflite-runtime wheel does not need it
    *(["libatlas-base-dev"] if raspbain_version < 13 else []),
    "libhdf5-dev",
]

# Filled by prepare_optional_deps() when "--all" is used
OPTIONAL_APT_INSTALL_LIST = []

# Dependencies list installed with pip3
# =================================================================
PIP_INSTALL_LIST = [
    "Flask",
    "imutils",
    "qrcode",
    "pyzbar", # pyzbar:one-dimensional barcodes and QR codes
    "pyzbar[scripts]",
    "readchar", # will update setuptools to the latest version
]

# Optional pip dependencies: only needed by the AI features (mediapipe / tflite-runtime).
# Filled by prepare_optional_deps(), installed only with "--all".
OPTIONAL_PIP_INSTALL_LIST = []

if raspbain_version >= 13:
    # Debian 13 (trixie) and later ship NumPy 2.x, which matches the simplejpeg
    # apt package built against the system NumPy.
    PIP_INSTALL_LIST.append("numpy")
else:
    # Debian <= 12 (bullseye / bookworm) still ships NumPy 1.x (bookworm: 1.24.2),
    # and the apt simplejpeg used by picamera2 is built against it. A pip-installed
    # NumPy 2.x in /usr/local shadows the system NumPy and breaks "import picamera2"
    # (ValueError: numpy.dtype size changed). mediapipe itself also requires numpy<2.
    PIP_INSTALL_LIST.append("numpy==1.26.4")

def prepare_optional_deps():
    """Fill the optional dependency lists for this system.

    Called only when install.py runs with "--all", so an ordinary installation
    of a product that does not use the AI features stays free of warnings.
    """
    # check whether mediapipe is supported
    if os_bit == 64 and raspbain_version >= 11 and python_version[0] == 3 and python_version[1] < 13:
        OPTIONAL_PIP_INSTALL_LIST.append('protobuf>=3.20.0') # mediapipe need
        OPTIONAL_PIP_INSTALL_LIST.append("mediapipe")
        OPTIONAL_APT_INSTALL_LIST.extend(MEDIAPIPE_APT_INSTALL_LIST)
    else:
        warn("mediapipe is only supported on 64bit system with python 3.12 or older... Skip")

    # check whether tflite-runtime is supported
    if python_version[0] == 3 and python_version[1] < 13:
        OPTIONAL_PIP_INSTALL_LIST.append("tflite-runtime")
        OPTIONAL_APT_INSTALL_LIST.extend(TFLITE_APT_INSTALL_LIST)
    else:
        warn("tflite-runtime is only supported on python 3.12 or older... Skip")

def pip_dep_name(dep):
    if dep.endswith('.whl'):
        return dep.split("/")[-1]
    return dep

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
                sys.exit(0)
        if "-h" in options or "--help" in options:
            print(usage)
            sys.exit(0)

    # check whether pip has the option "--break-system-packages"
    _is_bsps = ''
    status, _ = run_command("pip3 help install|grep break-system-packages")
    if status == 0:
        _is_bsps = "--break-system-packages"

    print("Install vilib python package")
    # do(msg="run setup file",
    #     cmd='python3 setup.py install')
    do(msg="pip3 install ./",
        cmd=f'pip3 install ./ {_is_bsps}')
    do(msg="cleanup",
        cmd='rm -rf vilib.egg-info')

    if "--no-dep" not in options:
        # install dependencies with apt
        # ===================================
        print("apt install dependency:")
        do(msg="dpkg configure",
            cmd='DEBIAN_FRONTEND=noninteractive dpkg --configure -a')  
        do(msg="update apt-get",
            cmd='DEBIAN_FRONTEND=noninteractive apt-get update -y')
        for dep in APT_INSTALL_LIST:
            do(msg=f"install {dep}",
                cmd=f'DEBIAN_FRONTEND=noninteractive apt-get install {dep} -y')

        # install dependencies with pip
        # ===================================
        print("pip3 install dependency:")

        if _is_bsps != '': # if true
            print("\033[38;5;8m pip3 install with --break-system-packages\033[0m")
        # update pip
        do(msg="update pip3", cmd="DEBIAN_FRONTEND=noninteractive apt-get install --only-upgrade -y python3-pip")
        for dep in PIP_INSTALL_LIST:
            dep_name = pip_dep_name(dep)
            do(msg=f"install {dep_name}",
                cmd=f'pip3 install {dep} {_is_bsps}')

        # install optional AI dependencies
        # ===================================
        # mediapipe / tflite-runtime are only installed on request, so products
        # that do not use them never see a "not supported" warning.
        if "--all" in options:
            prepare_optional_deps()
            if len(OPTIONAL_APT_INSTALL_LIST) > 0:
                print("apt install optional AI dependency (--all):")
                for dep in OPTIONAL_APT_INSTALL_LIST:
                    do(msg=f"install {dep}",
                        cmd=f'DEBIAN_FRONTEND=noninteractive apt-get install {dep} -y')
            if len(OPTIONAL_PIP_INSTALL_LIST) > 0:
                print("pip3 install optional AI dependency (--all):")
                for dep in OPTIONAL_PIP_INSTALL_LIST:
                    dep_name = pip_dep_name(dep)
                    do(msg=f"install {dep_name}",
                        cmd=f'pip3 install {dep} {_is_bsps}')
        else:
            print('\033[38;5;8m  Optional AI features (mediapipe / tflite-runtime) are not installed.'
                  ' Re-run with "--all" if your product needs them. \033[0m')

    print("Create workspace")
    # ===================================
    if not os.path.exists('/opt'):
        os.mkdir('/opt')
        run_command('chmod 774 /opt')
        run_command(f'chown -R {user_name}:{user_name} /opt')
    do(msg="create dir",
        cmd='mkdir -p /opt/vilib'
        + ' && chmod 774 /opt/vilib'
        + f' && chown -R {user_name}:{user_name} /opt/vilib'
        )
    do(msg="copy workspace",
        cmd='cp -r ./workspace/* /opt/vilib/'
        + ' && chmod 774 /opt/vilib/*'
        + f' && chown -R {user_name}:{user_name} /opt/vilib/*'
        )

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
        print("\n\nCanceled.")
    finally:
        sys.stdout.write(' \033[1D')
        sys.stdout.write('\033[?25h') # cursor visible 
        sys.stdout.flush()
