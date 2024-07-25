<<https://www.raspberrypi.com/documentation/computers/camera_software.html#building-rpicam-apps-without-building-libcamera>

<https://github.com/raspberrypi/picamera2/issues/563>
记得 更新储存路径 sudo ldconfig

- libcamera

    sudo apt install libcamera
    sudo apt install libcamera-dev

    git clone <https://git.libcamera.org/libcamera/libcamera.git>
    cd libcamera
    meson setup build
    ninja -C build install

    sudo apt install g++ clang
    sudo apt install meson ninja-build pkg-config
    sudo apt install libgnutls28-dev libssl-dev openssl

-

- picamera2
  - sudo pip3 install picamera2

  - sudo apt install python3-prctl
  - sudo apt install python3-picamera2
