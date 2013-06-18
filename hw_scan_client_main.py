import time
import scan_client
import gpio

INPUT_PIN_TO_EMAIL = {17: 'eran.mes@gmail.com', 22: 'p.lital@gmail.com'}
PROGRESS_PIN = 18
STATUS_PIN = 23
OUTPUT_PINS = (PROGRESS_PIN, STATUS_PIN)

class BlinkReporter(object):
  def __init__(self, pin_pwm_control):
    self._pwm_pin = pin_pwm_control

  def Blink(self):
    for i in (range(1000) + range(1000, -1, -1)):
      self._pwm_pin.SetValue(i)
      time.sleep(0.001)

if __name__ == '__main__':
  #progress_pin = gpio.OutputPin(PROGRESS_PIN)
  status_pin = gpio.OutputPin(STATUS_PIN)
  status_pin.SetHigh()
  poller = gpio.PinPoller(INPUT_PIN_TO_EMAIL.keys())
  blinker = BlinkReporter(gpio.PwmPin(PROGRESS_PIN))
  while True:
    events_on_pins = poller.WaitForEvent()
    recipients = [INPUT_PIN_TO_EMAIL[p] for p in events_on_pins]
    if recipients:
      scan_name = 'scan_' + time.strftime('%Y_%m_%d_%H_%S')
      scan_res = scan_client.scan_and_wait(scan_name, recipients, None)
      if scan_res:
        status_pin.SetHigh() # Green for OK. Could be red from a previous attempt.
      else:
        status_pin.SetLow() # Red for failure
