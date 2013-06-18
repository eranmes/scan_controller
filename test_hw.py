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
  try:
    print 'Press the button connected to pin %d' % p
    GPIO.wait_for_edge(p, GPIO.FALLING)
    print 'Button pressed for pin %d' % p
  except KeyboardInterrupt:  
	  GPIO.cleanup()

print 'Testing LEDs'
for p in output_pins:
  print 'Turning LED connected to pin %d ON' % p
  GPIO.output(p, True)
  time.sleep(2)
  print 'Turning LED connected to pin %d OFF' % p
  GPIO.output(p, False)

print 'Trying out PWM'
p = GPIO.PWM(18, 50)
p.start(1)
raw_input("Press Enter to stop PWM.\n>")  
p.stop()

time.sleep(2)

GPIO.cleanup()
