# Importieren der GPIO-Bibliothek
import machine

# Definieren des GPIO-Pins für den Taster
taster_pin = 4

# Einrichten des GPIO-Pins als Eingang
machine.Pin(taster_pin, machine.Pin.IN)

# Variable zum Speichern der Zahl
zahl = 0

# Funktion zum Erhöhen der Zahl
def zahl_erhoehen():
  global zahl
  zahl += 1

# Interrupt-Handler für den Taster
def taster_gedrueckt():
  zahl_erhoehen()

# Hinzufügen des Interrupt-Handlers zum Taster-Pin
taster_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=taster_gedrueckt)

# Endlosschleife zum Warten auf Tastendrücke
while True:
  # Ausgabe der aktuellen Zahl
  print(zahl)
  # Warten auf 100 Millisekunden
  time.sleep_ms(100)
