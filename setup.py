# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import sys 
from os import path,system

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='vilib',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="0.0.1",

    description='Camera Library for Raspberry Pi',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/sunfounder/SunFounder_camera',

    # Author details
    author='SunFounder',
    author_email='service@sunfounder.com',

    # Choose your license
    license='GNU',
    zip_safe=False,
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='python raspberry pi GPIO sunfounder',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=[ 'doc', 'tests*' ,'examples']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['picamera','imutils'],
 
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'face_train = vilib.face:main',
        ],
    },
)


errors = []

def do(msg="", cmd=""):
    print(" - %s..." % (msg), end='\r')
    print(" - %s... " % (msg), end='')
    status, result = eval(cmd)
    # print(status, result)
    if status == 0 or status == None or result == "":
        print('Done')
    else:
        print('Error')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))

def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    # print(result)
    # print(status)
    return status, result

if sys.argv[-1] == 'install':

    system('sudo apt update')
    # install cmake
    system('sudo apt install cmake -y')
    # install opencv
    # system('sudo pip3 install pillow')
    # system('sudo pip3 install numpy')  
    system('sudo apt install libjpeg-dev -y')
    system('sudo apt install libatlas-base-dev -y')
    system('sudo apt install libjpeg-dev -y')
    system('sudo apt install libtiff5-dev -y')
    system('sudo apt-get install libhdf5-dev -y') 
    system('sudo apt-get install libhdf5-serial-dev -y') 
    system('sudo apt-get install libgtk-3-dev -y') 
    
    system('sudo apt install li.jpg12-dev -y')
    system('sudo apt install libqtgui4 libqt4-test -y')
    system('sudo apt install libjasper-dev -y')

    system('sudo pip3 install opencv-contrib-python')
    # install tflite
    # system('sudo pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl')
    system('sudo pip3 install ./tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl')
    # install face_recognition
    system('sudo apt install build-essential cmake libboost-all-dev -y')
    system('sudo pip3 install dlib')
    system('sudo pip3 install face_recognition')
    # install Flask
    system('sudo pip3 install Flask')
    # install picamera
    system('sudo pip3 install picamera')
    # install pyzbar
    system('sudo pip3 install pyzbar')
    
    
    print("Create workspace")
    _, result = run_command("ls /opt")
    if "vilib" not in result:
        do(msg="create dir",
            cmd='run_command("mkdir /opt/vilib")')
    do(msg="copy workspace",
        cmd='run_command("sudo cp -r ./workspace/* /opt/vilib/")')

    # do(msg="add write permission to log file",
    #     cmd='run_command("sudo chmod 666 /opt/vilib/log")')
    
    
    