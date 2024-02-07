"""
ESP32-DevKitC V4/MicroPython exercise
240x240 ST7789 SPI LCD
using MicroPython library:
https://github.com/russhughes/st7789py_mpy

"""
#Überarbeitet Jan Krämer 27.11.2023
import uos
from machine import Pin, I2C, UART
import machine
import st7789py as st7789
from fonts import vga1_16x32 as font
from dfplayermini import Player
from time import sleep

music = Player(pin_TX=17, pin_RX=16)

# Initialisierung
play_press = False
pause_press = False
stopp_press = False
rueckwaerts_press = False
vorwaerts_press = False

"""
ST7789 Display  ESP32-DevKitC (SPI2)
SCL             GPIO13
SDA             GPIO11
                GPIO19  (miso not used)

ST7789_rst      GPIO10
ST7789_dc       GPIO9
"""
#ST7789 use SPI(2)

CMD_PLAY = const(0x0D)
uart = UART(1, 9600, tx=17, rx=18)           # init with given baudrate
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

#IN/OUT deklarieren
st7789_res = 10
st7789_dc  = 9
pin_st7789_res = machine.Pin(st7789_res, machine.Pin.OUT)
pin_st7789_dc = machine.Pin(st7789_dc, machine.Pin.OUT)

#Buttons
play = Pin(4, Pin.IN)
pause = Pin(5, Pin.IN)
stopp = Pin(6, Pin.IN)
rueckwaerts = Pin(7, Pin.IN)
vorwaerts = Pin(15, Pin.IN)


#Auflösung einstelllen
disp_width = 240
disp_height = 280

#Displaymitte ermitteln
CENTER_Y = int(disp_width/2)
CENTER_X = int(disp_height/2)

print(uos.uname())

#SPI Pins
pin_spi2_sck = machine.Pin(13, machine.Pin.OUT)
pin_spi2_mosi = machine.Pin(11, machine.Pin.OUT)
pin_spi2_miso = machine.Pin(19, machine.Pin.IN)

#SPI initialisieren
spi2 = machine.SPI(2, sck=pin_spi2_sck, mosi=pin_spi2_mosi, miso=pin_spi2_miso,
                   baudrate=40000000, polarity=1, phase=0, bits=8)
#einmal nachschauen
print(spi2)

#Display initialisieren
display = st7789.ST7789(spi2, disp_width, disp_width,
                          reset=pin_st7789_res,
                          dc=pin_st7789_dc,
                          xstart=0, ystart=0, rotation=0)

#einmal nachschauen
print(display)

def play_gedrueckt():
  global play_press
    # Taste nur ausgeben, wenn sie nicht bereits gedrückt ist
  if not play_press:
    print("start play")
    music.play()
    play_press = True

def pause_gedrueckt():
  global pause_press
    # Taste nur ausgeben, wenn sie nicht bereits gedrückt ist
  if not pause_press:
    print("pause")
    music.pause()
    pause_press = True
    
def stopp_gedrueckt():
  global stopp_press
    # Taste nur ausgeben, wenn sie nicht bereits gedrückt ist
  if not stopp_press:
    print("stopp")
    music.stop()
    stopp_press = True
    
def rueckwaerts_gedrueckt():
  global rueckwaerts_press
    # Taste nur ausgeben, wenn sie nicht bereits gedrückt ist
  if not rueckwaerts_press:
    print("rueckwaerts")
    music.play('prev')
    rueckwaerts_press = True
    
def vorwaertss_gedrueckt():
  global vorwaerts_press
    # Taste nur ausgeben, wenn sie nicht bereits gedrückt ist
  if not vorwaerts_press:
    print("vorwaerts")
    music.play('next')
    vorwaerts_press = True
  
        
print("set volume")
music.volume(20)


while True:
    play_val = play.value()
    pause_val = pause.value()
    stopp_val = stopp.value()
    rueckwaerts_val = rueckwaerts.value()
    vorwaerts_val = vorwaerts.value()
    #print(pause_val)
    if play_val == True:
        play_gedrueckt()
        display.text(font, "play", 20, 20)
    elif play_val == False:
        play_press = False
        
    if pause_val == True:
        pause_gedrueckt()
        display.text(font, "pause", 20, 20)
    elif pause_val == False:
        pause_press = False
        
    if stopp_val == True:
        stopp_gedrueckt()
        display.text(font, "stopp", 20, 20)
    elif stopp_val == False:
        stopp_press = False

    if rueckwaerts_val == True:
        rueckwaerts_gedrueckt()
        display.text(font, "zu", 20, 20)
    elif rueckwaerts_val == False:
        rueckwaerts_press = False

    if vorwaerts_val == True:
        vorwaertss_gedrueckt()
        display.text(font, "vor", 20, 20)
    elif vorwaerts_val == False:
        vorwaerts_press = False



#Test Text ausgeben
display.fill(st7789.BLACK)
display.text(font, "Hello!", 20, 20)
display.text(font, "ESP32", 20, 50)
display.text(font, "MicroPython", 20, 80)
display.text(font, "ST7789 SPI", 20, 110)
display.text(font, "240*280 IPS", 20, 180)



