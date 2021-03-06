#!/usr/bin/env python
import time
import scan_client
import gpio
from email_config import INPUT_PIN_TO_EMAIL

PROGRESS_PIN = 18
STATUS_PIN = 23

class BlinkReporter(object):
  def __init__(self, pin_pwm_control):
    self._pwm_pin = pin_pwm_control
    self._pwm_pin.SetValue(1)

  def Blink(self):
    for i in (range(1, 100) + range(99, 0, -1)):
      self._pwm_pin.SetValue(i)
      time.sleep(0.01)

if __name__ == '__main__':
  status_pin = gpio.OutputPin(STATUS_PIN)
  poller = gpio.PinPoller(INPUT_PIN_TO_EMAIL.keys())
  blinker = BlinkReporter(gpio.createPwm(PROGRESS_PIN))
  #status_pin.SetLow()
  #time.sleep(0.01)
  status_pin.SetHigh()
  last_scan_time = time.time() # Now
  while True:
    print 'Waiting for events...'
    events_on_pins = poller.WaitForEvent()
    recipients = [INPUT_PIN_TO_EMAIL[p] for p in events_on_pins]
    debounce_check = (time.time() - last_scan_time) > 15
    print 'Recipients:',recipients
    if recipients and debounce_check:
      scan_mail_subject = 'Your scan at %s' % (
          time.strftime('%Y-%m-%d %H:%M:%S'))
      scan_name = 'scan_' + time.strftime('%Y_%m_%d_%H_%M:%S')
      scan_res = scan_client.scan_and_wait(
          scan_name, blinker.Blink, recipients, scan_mail_subject)
      last_scan_time = time.time() # Now
      if scan_res:
        status_pin.SetHigh() # Green for OK. Could be red from a previous attempt.
      else:
        status_pin.SetLow() # Red for failure
    else:
      print 'No events, re-trying. Debounce:', debounce_check
