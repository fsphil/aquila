
# Aquila - experiments in 10kbit/s wenet

Transmits images using wenet, a fast data mode for high altitude balloon flights.

Based on: https://github.com/projecthorus/wenet/

## Requirements

* Raspberry Pi with a PiCam
* RFM98W or compatible radio module
* Python >= 3.4
* ssdv (https://github.com/fsphil/ssdv)

## Building

Most of the code is python, with some performance critical parts written in C. This can be built with:

`# ./setup.py build_ext --inplace clean`

