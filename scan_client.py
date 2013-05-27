#!/usr/bin/env python

from collections import namedtuple
import urllib2
import time
import re
from urllib import urlencode
import smtplib,email,email.encoders,email.mime.text,email.mime.base

SERVER_URL = 'http://raspberrypi.local:8081/do_scan'
MAX_WAIT = 60
POLL_INTERVAL = 0.5 # seconds
FROM_ADDRESS = 'scanner@over-here.org'

def extract_scan_name(get_reply):
  img_re = re.compile('<a href=\"(.*)\">')
  m = img_re.search(get_reply)
  if m is None:
    return
  return m.group(1)

def send_email(to_list, scan_name, scan_contents, scan_content_type):
  emailMsg = email.MIMEMultipart.MIMEMultipart()
  emailMsg['Subject'] = 'Test email with attachment.'
  emaisMsg['From'] = FROM_ADDRESS
  emailMsg['To'] = ', '.join(to_list)
  emailMsg.attach(email.mime.text.MIMEText('Your scan from today.', 'text'))
  fileMsg = email.mime.base.MIMEBase(scan_content_type.split('/'))
  fileMsg.set_payload(scan_contents)
  email.encoders.encode_base64(fileMsg)
  fileMsg.add_header('Content-Disposition','attachment;filename=%s' % (scan_name))
  emailMsg.attach(fileMsg)
  smtpclient = smtplib.SMTP(smtpserver)
  smtpclient.sendmail(FROM_ADDRESS, to_list, emailMsg.as_string())
  smtpclient.quit()

ScanResults = namedtuple('ScanResults', ['success', 'image_url', 'image_name'], verbose=True)

def initiate_scan(scan_name, progress_callback = None):
  params = urlencode({'scan_name': scan_name})
  # Post request
  try:
    req = urllib2.urlopen(SERVER_URL, data=params)
  except urllib2.HTTPError as e:
    print 'Exception: ',e
    return ScanResults(success=False)

  # Get request
  scan_done = False
  scan_start = time.time()
  while (not scan_done) and (req.code == 200) and (time.time() - scan_start < MAX_WAIT):
    reply = req.read()
    print 'Current reply: %s, headers: %s' % (reply, req.headers)
    if progress_callback:
      progress_callback()
    else:
      time.sleep(POLL_INTERVAL)
    scan_done = 'Still scanning' not in reply and 'Scan initiated' not in reply
    req = urllib2.urlopen(SERVER_URL)
  print 'Last reply: %s, headers: %s code: %d' % (reply, req.headers, req.code)
  if scan_done:
    scan_url = extract_scan_name(reply)
    return ScanResults(success=True,
        image_url=SERVER_URL.replace('/do_scan', scan_url),
        image_name=scan_url.split('?')[0].split('/')[2])
  return ScanResults(success=False)

def scan_and_wait(scan_name, progress_callback):
  res = initiate_scan(scan_name, progress_callback)
  if not res.success:
    print 'Scanning failed.'
    return False

  img_req = urllib2.urlopen(res.image_url)
  if img_req.code != 200:
    print 'Fetching scan failed.'
    return False
  image_buffer = img_req.read()
  content_type = img_req.headers.getheader('Content-Type')
  send_email(['eran@over-here.org', 'eran.mes@gmail.com'], scan_name, image_buffer, content_type)
  return True


def progress_callback():
  print 'Starting PWM...'
  time.sleep(POLL_INTERVAL)
  print 'Finishing PWM...'

if __name__ == '__main__':
  scan_name = 'scan_' + time.strftime('%Y_%m_%d_%H_%S')
  r = scan_and_wait(scan_name, progress_callback)
  print 'Scan successful?',r
