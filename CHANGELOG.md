# Change Log

## [0.3.20] - 2026-10-08

### Fixed

- Pin NumPy to 1.26.4 on Debian 12 (bookworm) and older: the installer used to run `pip3 install numpy` with no version constraint, which installed NumPy 2.x into /usr/local and shadowed the system NumPy 1.x, breaking `import picamera2` / vilib with `ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject` (the apt simplejpeg is built against NumPy 1.x)

## [0.3.19] - 2026-07-30

### Fixed

- Fix display freeze caused by imshow exception breaking the main loop

## [0.3.18] - 2025-01-01

## [0.3.2] - 2024-6-17

### Optimized

- Separate different functions into separate files to improve code readability
- Optimize detection mark drawing

### Added

- Add draw fps
- Add QRcode making

## [0.2.1] - 2024-3-15

### Optimized

- Change logger level of libcamera & flask to "ERROR"

## [0.2.0] - 2023-11-2

### Optimized

- Compatible with bookworm system
- Some small optimizations

## [0.1.0] - 2023-7-17

### Changed

- Use  picamera2 library instead of picamera

## [0.0.5] - 2023-5-5

### Optimized

- Change method of getting user name
- Add color for Error print

## [0.0.4] - 2022-5-19

### Fixed

- Increase compatibility for pi3 and pi4
- Fix bug
- Fixed use of setuptools and opencv-contrib-python version to avoid problems caused by new version

## [0.0.3] - 2022-5-19

### Fixed

- Compatible with python version 3.9
- Fix display bug
- Fix detect_obj_parameter error when close
- Fix the bug that only the first video is valid

### Added

- Add install working tip
- Uniform version file

### Optimized

- Optimize some details of examples

## [0.0.2] - 2022-1-14

### Added

- Add change log
- Add installation script
- Add script statement

### Fixed

- Progressive function test
- Fix bugs of installation procedure

### Changed

- Change the installation method
- Abandon the reference to face-recognition library
- Modify the README.d documentation

### Optimized

- Optimize code redundancy
- Organize and optimize the installation script
- Dynamic import, speed up startup
- Optimize the default save path of pictures and videos
- Optimize the start and end of flask

## [0.0.1] - 2021-11-29

- Complete the construction and testing of basic functions

[0.0.1]: https://github.com/sunfounder/vilib/tree/0.0.1
