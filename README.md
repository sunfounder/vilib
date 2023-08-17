# vilib -- Vision Library for Raspberry Pi
Image visual processing library for Raspberry Pi. It is developed based on opencv, picamera, tflite, mediapipe, pyzbar. Integrate multiple functions such as color recognition, face recognition, hands detection, image_classification, objects_detection, Wireless video transmission, etc...
</br>
</br>

If you want to use the new version of Raspberry Pi camera driver libcamera, please switch to the picamera2 branch:
  
  https://github.com/sunfounder/vilib/tree/picamera2

Quick Links:
- [Documentions](#documentions)
- [Compatibility](#compatibility)
- [Install](#install)
- [Usage](#usage)
- [ChangeLog](#changelog)
- [About SunFounder](#about-sunfounder)
- [License](#license)
- [Contact us](#contact-us)

## Documentions
- vilib API

  https://docs.sunfounder.com/projects/vilib-rpi/en/latest/

- Reference Link

  Picamera : https://picamera.readthedocs.io/en/latest/index.html

  TFLite ：https://www.tensorflow.org/lite/examples

  Mediapipe : https://mediapipe-studio.webapps.google.com/home, https://github.com/google/mediapipe


## Compatibility

  | fuction |python version |os bit |
  | :---: | :---: | :---: |
  | web display (flask)| py37, py38, py39 | 32-bit
  | color detection (opencv) | py37, py38, py39 | 32-bit
  | face detection (opencv)| py37, py38, py39 | 32-bit
  | image classification (tflite)| py37, py38, py39 | 32-bit
  | objects detection (tflite)| py37, py38, py39 | 32-bit
  | qrcode detection (pyzbar)| py37, py38, py39 | 32-bit
  | take photo (opencv)| py37, py38, py39 | 32-bit
  | record video (opencv)| py37, py38, py39 | 32-bit
  | hands detection (mediapipe)| py37 | 32-bit
  | pose detection (mediapipe)| py37 | 32-bit
  | others | - | - |

## Install
- clone code 
```shell
cd ~
git clone https://github.com/sunfounder/vilib.git
```
- install
```shell
cd ~/vilib
sudo python3 install.py 
```
## Usage
Before using, you need to use "sudo raspi-config " to open the camera port
```bash
cd ~/vilib/examples
sudo python3 xxx.py
```

Stop running the example by using <kbd>Ctrl</kbd>+<kbd>C</kbd>

## ChangeLog

- [CHANGELOG]

## About SunFounder
SunFounder is a technology company focused on Raspberry Pi and Arduino open source community development. Committed to the promotion of open source culture, we strives to bring the fun of electronics making to people all around the world and enable everyone to be a maker. Our products include learning kits, development boards, robots, sensor modules and development tools. In addition to high quality products, SunFounder also offers video tutorials to help you make your own project. If you have interest in open source or making something cool, welcome to join us!

## License
-
## Contact us

website:
    ezblock.cc

E-mail:
    service@sunfounder.com


[CHANGELOG]:https://github.com/sunfounder/vilib/blob/master/CHANGELOG.md