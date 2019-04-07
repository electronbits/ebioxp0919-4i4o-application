This a python3 application which is made for [EBIOXP0919-4I4O](https://www.electronbits.com/product/ebioxp0919-4i4o) and running on Raspbeery Pi on EBRPIH1118 board. The board is powered by [TCA9534A I/O](http://www.ti.com/lit/ds/symlink/tca9534a.pdf?ts=1591595018761) expander chip.

Considering the board is connected to EBRPIH1118 
    
    |-------------------|
    |   SCL <-> SCL     |
    |   SDA <-> SDA     |
    |   GND <-> GND     |
    |-------------------|

### Required python3 module to install:
    smbus or smbus2

### usage#1:
    To turn on relay number 1: python3 ebioxp4i4o_app.py -r1 --on

### usage#2:
    To read digital input number 3: python3 ebioxp4i4o_app.py -di 1

