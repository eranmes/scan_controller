import select

GPIO_PWM_PIN = 18

def _export_pin(pin_num):
  with open('/sys/class/gpio/export', 'w') as f:
    f.write('%s\n' % pin_num)

def _unexport_pin(pin_num):
  with open('/sys/class/gpio/unexport', 'w') as f:
    f.write('%s\n' % pin_num)

def _write_pin_direction(pin_num, pin_mode):
  if pin_mode != 'in' and pin_mode != 'out':
    raise RuntimeError('Pin mode can only be in or out, was %s' % pin_mode)
  with open('/sys/class/gpio/gpio%d/direction' % pin_num, 'w') as f:
    f.write('%s\n' % pin_mode)

def setup_pin_for_output(pin_num):
  _export_pin(pin_num)
  _write_pin_direction(pin_num, 'out')

def setup_pin_for_input(pin_num):
  _export_pin(pin_num)
  _write_pin_direction(pin_num, 'in')
  with open('/sys/class/gpio/gpio%d/edge' % pin_num, 'w') as f:
    f.write('falling\n')

class PwmPin(object):
  def __init__(self, pin_num):
    if pin_num != GPIO_PWM_PIN:
      raise RuntimeError('PWM only supported on pin %d, not %d' %
          (GPIO_PWM_PIN, pin_num))
    self._pin = pin_num
    setup_pin_for_output(self._pin)
    with open('/sys/class/rpi-pwm/pwm0/active', 'w') as f:
      f.write('1')
    self._output_file = open('/sys/class/rpi-pwm/pwm0/duty', 'w')

  def SetValue(self, pwm_value):
    self._output_file.write('%d\n' % pwm_value)

class OutputPin(object):
  def __init__(self, output_pin):
    self._pin = output_pin
    setup_pin_for_output(self._pin)
    self._output_file = open('/sys/class/gpio/gpio%d/value' % self._pin, 'w')

  def _WriteValue(self, v):
    self._output_file.write('%d\n')

  def SetHigh(self):
    self._WriteValue(1)

  def SetLow(self):
    self._WriteValue(0)

  def Cleanup(self):
    try:
      self._output_file.close()
    except IOError as e:
      pass
    self._output_file = None
    _unexport_pin(self._pin)

event_to_string = {
    select.EPOLLERR: 'EPOLLERR',
    select.EPOLLHUP: 'EPOLLHUP',
    select.EPOLLMSG: 'EPOLLMSG',
    select.EPOLLOUT: 'EPOLLOUT',
    select.EPOLLRDBAND: 'EPOLLRDBAND',
    select.EPOLLWRBAND: 'EPOLLWRBAND',
    select.EPOLLET: 'EPOLLET',
    select.EPOLLIN: 'EPOLLIN',
    select.EPOLLONESHOT: 'EPOLLONESHOT',
    select.EPOLLPRI: 'EPOLLPRI',
    select.EPOLLRDNORM: 'EPOLLRDNORM',
    select.EPOLLWRNORM: 'EPOLLWRNORM'
    }

def eventmask_to_strings(eventmask):
  ret = []
  for ev, ev_string in event_to_string.items():
    if eventmask & ev:
      ret.append(ev_string)
  return ret

class PinPoller(object):
  def __init__(self, input_pins):
    self._input_pins = input_pins[:]
    self._pin_to_fd = {}

  def _Setup(self):
    if not self._pin_to_fd:
      self._poller = select.epoll()
      for pin in self._input_pins:
        setup_pin_for_input(pin)
      for pin in self._input_pins:
        f = open('/sys/class/gpio/gpio%d/value' % pin, 'r')
        f.read() # To clear any remaining events
        print 'Adding fd %d for pin %d' % (f.fileno(), pin)
        self._poller.register(f.fileno(), select.POLLPRI)
        self._pin_to_fd[pin] = f

  def WaitForEvent(self):
    self._Setup()
    res = self._poller.poll(10000)
    print 'poll res:',res
    for fd, eventmask in res:
      print 'On FD %d: %s' % (fd, ','.join(eventmask_to_strings(eventmask)))

    return [p for p in self._input_pins if self._pin_to_fd[p].read() != '']

  def Cleanup(self):
    pins = self._pin_to_fd.keys()
    for p in pins:
      f = self._pin_to_fd.pop(p)
      self._poller.unregister(f.fileno())
      f.close()
      _unexport_pin(p)
