"""
Autor: Jan Krämer
Kurs: ETS23 Microcontroller - Micropython
Klassenarbeit Nr.1 Teil 1
Datum: 09.02.2024

Das Programm steuer über die Serielle Schnittstelle den Serial MP3 Player an.
Bei betätigen eines Tasters werden die jeweiligen kommando Bytes an den Player übertragen.
Auf dem Display werden Titelnummer, aktueller Zustand (Play, Pause oder Stopp), und die Spielzeit Übertragen.
Auf der SD-Karte ist Musik im MP3 Format gespeichert. Damit der Player diese aufrufen kann, müssen
die Titel umbenannt werden in 01xxx.mp3, 02xxx.mp3 usw. und in einen Ordner mit dem Namen 01 geladen werden.

Benötigt:
 - Espressif ESP32 S3
 - 5x Pulldown Taster
 - Serial MP3 Player Modul
 - ST7789 Display
 
Taster:
Taster Play     GPIO4
Taster Pause    GPIO5
Taster Stopp    GPIO6
Taster zurück   GPIO7
Taster weiter   GPIO15

Serial MP3 Player:
RX GPIO16
TX GPIO17

ST7789 Display  ESP32-DevKitC (SPI2)
SCL             GPIO13
SDA             GPIO11
                GPIO19  (miso not used)

ST7789_rst      GPIO10
ST7789_dc       GPIO9

Bibliotheken
st7789.py
dfplayermini.py
"""
#Überarbeitet Jan Krämer 27.11.2023
import uos
from machine import Pin, I2C, UART
import machine
import st7789py as st7789
from fonts import vga1_16x16 as font
from dfplayermini import Player
from time import ticks_ms, ticks_diff

music = Player(pin_TX=17, pin_RX=16)

# Initialisierung der Taster
play_press = False
pause_press = False
stopp_press = False
rueckwaerts_press = False
vorwaerts_press = False

# Initialisierung für MP3 player und Display Infos
track_ID = 1
zustand = ""
track_start = False
#Zeitvariablen
zeit = 0
sekunden = 0
minuten = 0
alte_zeit = 0

#Konfiguration der Seriellen Schnittstelle
uart = UART(1, 9600, tx=17, rx=18)           # init with given baudrate
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

#IN/OUT Display deklarieren
st7789_res = 10
st7789_dc  = 9
pin_st7789_res = machine.Pin(st7789_res, machine.Pin.OUT)
pin_st7789_dc = machine.Pin(st7789_dc, machine.Pin.OUT)

#Eingänge
#Taster
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

#Bei erstem Start die Lautstärke auf Maximum
print("set volume")
music.volume(15) #maximales Volume

#Start Text ausgeben
display.fill(st7789.BLACK)
display.text(font, "MP3 Player", 20, 20)
display.text(font, "Track: {0}".format(track_ID), 20, 100)
display.text(font, "Play druecken", 20, 180)

#Play Funktion
def play_gedrueckt():
  global play_press
  global zustand
  global track_start
    # Bei Zustandsänderung Variablen an den Zustand anpassen
  if not play_press:
    print("start play")
    zustand = "Play"
    music.play() #sende Befehl bytes für Play (0x0D)
    track_start = True
    play_press = True
    display_update()

#Pause Funktion
def pause_gedrueckt():
  global pause_press
  global zustand
  global track_start
    # Bei Zustandsänderung Variablen an den Zustand anpassen
  if not pause_press:
    print("pause")
    zustand = "Pause"
    track_start = False
    music.pause() #sende Befehl bytes für pause (0x0E)
    pause_press = True
    display_update()

#Stopp Funktion 
def stopp_gedrueckt():
  global stopp_press
  global track_ID
  global zustand
  global track_start
  global sekunden, minuten
    # Bei Zustandsänderung Variablen an den Zustand anpassen
  if not stopp_press:
    print("stopp")
    zustand = "Stopp"
    music.stop() #sende Befehl bytes für stopp (0x16)
    track_start = False
    #zeit zurücksetzen
    sekunden = 0
    minuten = 0
    track_ID += 1
    stopp_press = True
    display_update()

#Titel zurück Funktion
def rueckwaerts_gedrueckt():
  global rueckwaerts_press
  global track_ID
  global sekunden, minuten
    # Bei Zustandsänderung Variablen an den Zustand anpassen
  if not rueckwaerts_press:
    print("rueckwaerts")
    music.play('prev') #sende Befehl bytes für zurück (0x02)
    sekunden = 0
    minuten = 0
    if track_ID == 1:
        track_ID = 1
    else:
        track_ID -= 1
    rueckwaerts_press = True
    display_update()

#Titel weiter Funktion    
def vorwaertss_gedrueckt():
  global vorwaerts_press
  global track_ID
  global sekunden, minuten
    # Bei Zustandsänderung Variablen an den Zustand anpassen
  if not vorwaerts_press:
    print("vorwaerts")
    music.play('next') #sende Befehl bytes für weiter (0x01)
    #Zeit auf 0 setzen
    sekunden = 0
    minuten = 0
    track_ID += 1 #zeige nächsten Titel an
    vorwaerts_press = True
    display_update()
  
#Funktion zur Darstellung der Track Infos        
def display_update():
    #Text ausgeben
    display.text(font, "Track:     ", 20, 100)
    display.text(font, "Track: {0}".format(track_ID), 20, 100)
    display.text(font, "0:0 ", 20, 140)
    display.text(font, "                     ", 20, 180)
    display.text(font, zustand, 20, 180)

#Funktion zur Darstellung der Spielzeit
def display_zeit():
    #Zeit ausgeben
    display.text(font, "{0}:{1} ".format(minuten, sekunden), 20, 140)
    if sekunden > 59: #wenn eine minute um ist, muss die Null entfernt werden durch überschreiben...
        display.text(font, "{0}:{1} ".format(minuten, sekunden), 20, 140)

#loop
while True:
    #Auslesen der Taster Pins
    play_val = play.value()
    pause_val = pause.value()
    stopp_val = stopp.value()
    rueckwaerts_val = rueckwaerts.value()
    vorwaerts_val = vorwaerts.value()
    
    #Zeit setzen
    neue_zeit = ticks_ms()
      
    #Wenn Musik läuft dann Zeitberechnung
    if track_start == True:
        if (ticks_diff(neue_zeit, alte_zeit) > 1000): #Wenn die differenz zwischen neue_zeit und alte_zeit >= 1000ms...
            sekunden += 1
            print(sekunden)
            alte_zeit = neue_zeit #Setze alte_zeit auf den Wert von neue_zeit
            display_zeit()
            if sekunden > 59: #wenn eine minute rum ist dann minute um 1 erhöhen
                sekunden = 0
                minuten += 1
    else:
        display_zeit()

    #Wenn Taste gedrückt, dann Funktion aufrufen
    if play_val == True:
        play_gedrueckt()
    elif play_val == False: # Taste als "nicht gedrückt" markieren, wenn sie losgelassen wird
        play_press = False
        
    if pause_val == True:
        pause_gedrueckt()
    elif pause_val == False:
        pause_press = False
        
    if stopp_val == True:
        stopp_gedrueckt()
    elif stopp_val == False:
        stopp_press = False

    if rueckwaerts_val == True:
        rueckwaerts_gedrueckt()
    elif rueckwaerts_val == False:
        rueckwaerts_press = False

    if vorwaerts_val == True:
        vorwaertss_gedrueckt()
    elif vorwaerts_val == False:
        vorwaerts_press = False






