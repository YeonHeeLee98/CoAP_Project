from coapthon.resources.resource import Resource
import threading
import logging as logger
import Adafruit_DHT
import RPi.GPIO as gpio
import time


class Buzzer(Resource):
    def __init__(self, name="BuzzerResource", coap_server=None):
        super(Buzzer, self).__init__(name, coap_server, visible=True,
                                     observable=True, allow_children=True)
        gpio.setmode(gpio.BCM)
        gpio.setup(17, gpio.OUT)
        self.Buzzer = gpio.PWM(17, 50)
        self.Buzzer.start(0)
        self.payload = "0"

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload

        if self.payload == "1":
            for dc in range(0, 101, 5):
                self.Buzzer.ChangeDutyCycle(dc)
                time.sleep(0.1)
            for dc in range(100, -1, -5):
                self.Buzzer.ChangeDutyCycle(dc)
                time.sleep(0.1)
        else:
            print("Buzzer OFF")
        return self

class LED(Resource):
    def __init__(self, name="Obs", coap_server=None):
        super(LED, self).__init__(name, coap_server, visible=True,
                                  observable=True, allow_children=False)
        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)

        gpio.setup(13, gpio.OUT)  # Red
        gpio.setup(19, gpio.OUT)  # Green
        gpio.setup(26, gpio.OUT)  # Blue

        self.payload = "0"
        self.period = 5

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        # value = request.payload
        if self.payload == "1":
            gpio.output(13, False)
            gpio.output(19, False)
            gpio.output(26, True)
        elif self.payload == "2":
            gpio.output(13, False)
            gpio.output(19, True)
            gpio.output(26, False)
        elif self.payload == "3":
            gpio.output(13, True)
            gpio.output(19, False)
            gpio.output(26, False)
        return self


class PIR_sensor(Resource):
    def __init__(self, name="Obs", coap_server=None):
        super(PIR_sensor, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)
        self.sensor = Adafruit_DHT.DHT11
        self.pin = 7
        self.payload = "0"
        self.period = 5
        self.update(True)

    def render_GET(self, request):
        self.payload = gpio.setup(7, gpio.IN)
        return self

    def render_POST(self, request):
        self.payload = request.payload
        return self

    def update(self, first=False):
        if not self._coap_server.stopped.isSet():
            timer = threading.Timer(self.period, self.update)
            timer.setDaemon(True)
            timer.start()

            if not first and self._coap_server is not None:
                self.payload = gpio.setup(7, gpio.IN)
                logger.debug("Periodic Update - PIR sensor %s" % self.payload)
                # gpio.output(Buzzer, gpio.IN) #원래 없었음
                self._coap_server.notify(self)
                self.observe_count += 1


class TH_sensor(Resource):
    def __init__(self, name="Obs", coap_server=None):
        super(TH_sensor, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)
        self.sensor = Adafruit_DHT.DHT11
        self.pin = 14
        self.payload = "0.0%0.0"
        self.period = 5
        self.update(True)

    def render_GET(self, request):
        h, t = Adafruit_DHT.read_retry(self.sensor, self.pin)
        self.payload = "%s*%s" % (h, t)
        return self

    def update(self, first=False):
        if not self._coap_server.stopped.isSet():
            timer = threading.Timer(self.period, self.update)
            timer.setDaemon(True)
            timer.start()

            if not first and self._coap_server is not None:
                h, t = Adafruit_DHT.read_retry(self.sensor, self.pin)
                logger.debug("Periodic Update - TH sensor %s*%s" % (h, t))
                self.payload = "%s*%s" % (h, t)
                self._coap_server.notify(self)
                self.observe_count += 1
