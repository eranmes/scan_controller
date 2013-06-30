import time
import scan_client
import gpio

INPUT_PINS = [17, 22]
PROGRESS_PIN = 18
STATUS_PIN = 23

if __name__ == '__main__':
  status_pin = gpio.OutputPin(STATUS_PIN)
  status_pin.SetHigh()
  poller = gpio.PinPoller(INPUT_PINS)
  pwm = gpio.PwmPin(PROGRESS_PIN)
  print 'Now press the buttons.'
  for i in range(5):
    events_on_pins = poller.WaitForEvent()
    print 'Events on pins', events_on_pins

  print 'Changing status pin state.'
  status_pin.SetLow()
  time.sleep(3)
  status_pin.SetHigh()
  time.sleep(3)
  status_pin.SetLow()
  print 'Pulsing PWM led.'
  for i in range(1, 100):
    pwm.SetValue(i)
    time.sleep(0.01)

  poller.Cleanup()
  status_pin.Cleanup()
  pwm.Cleanup()

