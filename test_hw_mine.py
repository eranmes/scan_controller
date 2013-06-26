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
  #pwm = gpio.PwmPin(PROGRESS_PIN)
  for i in range(5):
    events_on_pins = poller.WaitForEvent()
    print 'Events on pins', events_on_pins

  poller.Cleanup()
  status_pin.Cleanup()


