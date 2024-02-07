from time import sleep, time
from machine import Pin, I2C, UART
# Taste an GPIO-Pin 12
taster_pin = Pin(4, Pin.IN)

# Initialisierung
last_press = False

def tasten_gedrueckt():
  global last_press
  
  # Taste nur ausgeben, wenn sie nicht bereits gedrückt ist
  if not last_press:
    print("Taste gedrückt!")
    last_press = True

# Endlosschleife zum Abfragen der Taste
while True:
  # Zustand der Taste lesen
  tasten_zustand = taster_pin.value()
  
  # Wenn Taste gedrückt ist, Funktion aufrufen
  if tasten_zustand == 1:
    tasten_gedrueckt()
  
  # Taste als "nicht gedrückt" markieren, wenn sie losgelassen wird
  elif tasten_zustand == 0:
    last_press = False
