import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  

input_pins = (17, 22)
for p in input_pins:      
  GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

output_pins = (18, 23)
for p in output_pins:
  GPIO.setup(p, GPIO.OUT)
  GPIO.output(p, False)

print 'Make sure buttons are connected to pin %s' % (input_pins,)
raw_input("Press Enter when ready\n>")  

for p in input_pins:
  GPIO.add_event_detect(p, GPIO.RISING)

p1_state = False
p2_state = False
while True:
  time.sleep(0.020)
  if (GPIO.event_detected(17)):
    p1_state = not p1_state
    GPIO.output(18, p1_state)
  if (GPIO.event_detected(22)):
    p2_state = not p2_state
    GPIO.output(23, p2_state)

