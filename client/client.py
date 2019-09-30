import pyaudio
import numpy as np
import math, sys, os, random, logging, warnings, json
from time import sleep
from collections import deque
from threading import Thread
from datetime import datetime
from ctypes import *
from contextlib import contextmanager

from cv2 import VideoCapture, imencode,imwrite
from base64 import b64encode

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage


# CLOUD SERVICES CONFIG ---------------------------------------------------- #

FIRE_CERTIFICATE = "<CERTIFICATE PATH"
DEVICE_ID = 'cam01'

AWS_CONFIG = {
    'host': "< ADD HOST HERE>",
    'clientId': "publisher",
    'topic': "pilot",
    'rootCA': "root-CA.crt",
    'private_key': "pilot.private.key",
    'thing_cert': "pilot.cert.pem"
}

# ------ CONFIG ------------------------------------------------------------ #

SLEEPTIME=.1
paused_monitor = False
exit_threads = False
TOTAL_TIME = 8
START_PATTERN = [1] * TOTAL_TIME

# GLOBAL VARS ------------------------------------------------------------ #

signal_dq = deque('',maxlen=100)
send_dq = deque()
tx = deque([],maxlen=50)

# -------------------------------------------------------------------------- #



# AWS CONFIG --------------------------------------------------------------- #

def AWS_init(config):
    aws_client = None
    aws_client = AWSIoTMQTTClient(config['clientId'])
    aws_client.configureEndpoint(config['host'], 8883)
    aws_client.configureCredentials(
        config['rootCA'], config['private_key'], config['thing_cert'])
    # AWSIoTMQTTClient connection configuration
    aws_client.configureAutoReconnectBackoffTime(1, 32, 20)
    # Infinite offline Publish queueing
    aws_client.configureOfflinePublishQueueing(-1)
    aws_client.configureDrainingFrequency(2)  # Draining: 2 Hz
    aws_client.configureConnectDisconnectTimeout(10)  # 10 sec
    aws_client.configureMQTTOperationTimeout(5)  # 5 sec
    aws_client.connect()
    return aws_client


# boilerplate error handling -----------------------------------------------------
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt): pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)


if not sys.warnoptions: warnings.simplefilter("ignore")


class AudioCaptureThread(Thread):
  def __init__(self, logger):
    Thread.__init__(self)
    self._logger = logger

  def run(self):
    global signal_dq
    global exit_threads

    RATE = 44100
    BUFFER = 882
    with noalsaerr():
      p = pyaudio.PyAudio()

    stream = p.open(
        format = pyaudio.paFloat32,
        channels = 1,
        rate = RATE,
        input = True,
        output = False,
        frames_per_buffer = BUFFER)

    r = range(0,int(RATE/2+1),int(RATE/BUFFER))
    l = len(r)
    self._logger.info("Audio Capture Start")

    while (not exit_threads):
      try:
        data = np.fft.rfft(np.frombuffer(
            stream.read(BUFFER), dtype=np.float32))
      except IOError: pass

      data = np.log10(np.sqrt(np.real(data)**2+np.imag(data)**2) / BUFFER) * 10
      signal_dq.append(1 if data[300] > -20.0 else 0)
    
    self._logger.info("Audio Capture Stop")


class MonitorThread(Thread):
  def __init__(self, logger):
    Thread.__init__(self)
    self._logger = logger
    self.cred = credentials.Certificate(FIRE_CERTIFICATE)
    firebase_admin.initialize_app(self.cred)
    self.db = firestore.client()
    self.bucket = storage.bucket("noise-iot.appspot.com")
    self.aws = AWS_init(AWS_CONFIG)
    self.topic = AWS_CONFIG['topic']

  def run(self):
    global signal_dq
    global SLEEPTIME
    global exit_threads
    global paused_monitor

    self._logger.info("Monitor Ready")

    startup = deque([0 for _ in range(len(START_PATTERN))], maxlen=len(START_PATTERN))

    while (not exit_threads):
      while ((not paused_monitor) and (not exit_threads)):
        sleep(SLEEPTIME)
        startup.append(signal_dq.pop())
        if list(startup) == START_PATTERN:
          startup.append(2) #delay
          self._logger.info("Alert found. run actions")
          self.send_data()
          self._logger.info("Monitor READY")
    self._logger.info("Receiver Thread Stop")

  def send_data(self, device_id=1, topic='security_feed'):
    s, img = VideoCapture(0).read()
    
    
    now = str(datetime.utcnow())
    image_path = f'{now}.jpg'
    imwrite(image_path,img)
    imageBlob = self.bucket.blob(image_path)
    #my_image = imencode('.jpg', img)[1]
    imageBlob.upload_from_filename(image_path)
    url_image = imageBlob.generate_signed_url(datetime.max)
     #'image' : str(b64encode(imencode('.jpg', img)[1]))
    
    message = {
      'message' : "ALERTA",
      'device_id' : device_id,
      'time' : now,
      'image': url_image
      }


    self.db.collection(u'security').document(f'{now}').set(message)
    aws_json = json.dumps(message)
    self.aws.publish(self.topic, aws_json,1)
    self._logger.info(f"Alerta Publicado: {topic} - {message['device_id']} {message['time']}")
  
    pass


def main():
  global paused_monitor
  global exit_threads

  running = True
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

  capture = AudioCaptureThread(logging)
  monitor = MonitorThread(logging)
  
  capture.setDaemon(True) 
  monitor.setDaemon(True) 
  
  capture.start();
  sleep(1)
  #os.system('clear')
  monitor.start()

  while (not exit_threads):
    x = input('>')
    try:
      if x == 'exit':
        logging.info("Exiting")
        exit_threads = True
      elif x == 'stop':
        paused_monitor = True
        logging.info("Paused Reader")
      elif x == 'start':
        logging.info("Restarted Reader")
      elif x[:4] == 'send':
        msg = x[5:]
        if msg:
          send_dq.append(msg)
        else:
          logging.info("missing message")
    except Exception as e: 
      print(e)

main()
