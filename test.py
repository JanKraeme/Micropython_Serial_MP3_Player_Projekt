"""
ESP32-DevKitC V4/MicroPython exercise
240x240 ST7789 SPI LCD
using MicroPython library:
https://github.com/russhughes/st7789py_mpy

"""

import uos
import machine
import st7789py as st7789
from fonts import vga1_16x32 as font
import random
import ustruct as struct
import utime

"""
ST7789 Display  ESP32-DevKitC (SPI2)
SCL             GPIO13
SDA             GPIO11
                GPIO19  (miso not used)

ST7789_rst      GPIO5
ST7789_dc       GPIO4
"""
#ST7789 use SPI(2)

st7789_res = 5
st7789_dc  = 4
pin_st7789_res = machine.Pin(st7789_res, machine.Pin.OUT)
pin_st7789_dc = machine.Pin(st7789_dc, machine.Pin.OUT)

disp_width = 240
disp_height = 280
CENTER_Y = int(disp_width/2)
CENTER_X = int(disp_height/2)

print(uos.uname())
#spi2 = machine.SPI(2, baudrate=40000000, polarity=1)
pin_spi2_sck = machine.Pin(13, machine.Pin.OUT)
pin_spi2_mosi = machine.Pin(11, machine.Pin.OUT)
pin_spi2_miso = machine.Pin(19, machine.Pin.IN)
spi2 = machine.SPI(2, sck=pin_spi2_sck, mosi=pin_spi2_mosi, miso=pin_spi2_miso,
                   baudrate=40000000, polarity=1)
print(spi2)
display = st7789.ST7789(spi2, disp_width, disp_width,
                          reset=pin_st7789_res,
                          dc=pin_st7789_dc,
                          xstart=0, ystart=0, rotation=0)

display.fill(st7789.BLACK)
display.text(font, "Hello!", 10, 10)
display.text(font, "ESP32", 10, 40)
display.text(font, "MicroPython", 10, 70)
display.text(font, "ST7789 SPI", 10, 100)
display.text(font, "240*280 IPS", 10, 130)

for i in range(1000):
    display.pixel(random.randint(0, disp_width),
          random.randint(0, disp_height),
          st7789.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

# Helper function to draw a circle from a given position with a given radius
# This is an implementation of the midpoint circle algorithm,
# see https://en.wikipedia.org/wiki/Midpoint_circle_algorithm#C_example 
# for details
def draw_circle(xpos0, ypos0, rad, col=st7789.color565(255, 255, 255)):
    x = rad - 1
    y = 0
    dx = 1
    dy = 1
    err = dx - (rad << 1)
    while x >= y:
        display.pixel(xpos0 + x, ypos0 + y, col)
        display.pixel(xpos0 + y, ypos0 + x, col)
        display.pixel(xpos0 - y, ypos0 + x, col)
        display.pixel(xpos0 - x, ypos0 + y, col)
        display.pixel(xpos0 - x, ypos0 - y, col)
        display.pixel(xpos0 - y, ypos0 - x, col)
        display.pixel(xpos0 + y, ypos0 - x, col)
        display.pixel(xpos0 + x, ypos0 - y, col)
        if err <= 0:
            y += 1
            err += dy
            dy += 2
        if err > 0:
            x -= 1
            dx += 2
            err += dx - (rad << 1)
            
draw_circle(CENTER_X, CENTER_Y, 100, st7789.color565(255, 255, 255))
draw_circle(CENTER_X, CENTER_Y, 97, st7789.color565(255, 0, 0))
draw_circle(CENTER_X, CENTER_Y, 94, st7789.color565(0, 255, 0))
draw_circle(CENTER_X, CENTER_Y, 91, st7789.color565(0, 0, 255))
utime.sleep(2)

display.fill(st7789.BLACK)
display.text(font, "Test various", 20, 10)
display.text(font, "approach to", 20, 50)
display.text(font, "fill pixels", 20, 90)
utime.sleep(2)

#test various approach to fill pixels
display.fill(st7789.BLACK)
display.text(font, "pixel()", 20, 10)
display.text(font, "optimized", 20, 70)
display.text(font, "blit_buffer()", 20, 130)
display.text(font, "fill_rect()", 20, 190)
utime.sleep(1)

# fill area with display.pixel()
ms_start = utime.ticks_ms()
for y in range(60):
    for x in range(240):
        display.pixel(x, y, st7789.color565(x, 0, 0))
ms_now = utime.ticks_ms()
display.text(font, str(utime.ticks_diff(ms_now,ms_start))+" ms", 50, 10)

# fill area optimized
#!!! may be NOT suit your setup
ms_start = utime.ticks_ms()
display.set_window(0, 60, 239, 119)
pin_st7789_dc.on()
for y in range(60, 120):
    for x in range(240):
        spi2.write(struct.pack(st7789._ENCODE_PIXEL,
                               (0 & 0xf8) << 8 | (x & 0xfc) << 3 | 0 >> 3))
ms_now = utime.ticks_ms()
display.text(font, str(utime.ticks_diff(ms_now,ms_start))+" ms", 50, 70)

# fill with blit_buffer(buffer, x, y, width, height)
buffer = bytearray(240*60*2)

ms_pre = utime.ticks_ms()
#prepare buffer
for y in range(60):
    for x in range(240):
        idx = ((y*240) + x)*2
        pxCol = (y & 0xf8) << 8 | (0 & 0xfc) << 3 | x >> 3
        packedPx = struct.pack(st7789._ENCODE_PIXEL, pxCol)
        buffer[idx] = packedPx[0]
        buffer[idx+1] = packedPx[1]

ms_start = utime.ticks_ms()
display.blit_buffer(buffer, 0, 120, 240, 60)
ms_now = utime.ticks_ms()
strToDisp = str(utime.ticks_diff(ms_start,ms_pre)) + \
    "/" + str(utime.ticks_diff(ms_now,ms_start)) + " ms"
display.text(font, strToDisp, 50, 130)

# fill area with display.fill_rect()
ms_start = utime.ticks_ms()
display.fill_rect(0, 180, 240, 60, st7789.color565(0, 150, 150))
ms_now = utime.ticks_ms()
display.text(font, str(utime.ticks_diff(ms_now,ms_start))+" ms", 50, 190)

print("- bye-")