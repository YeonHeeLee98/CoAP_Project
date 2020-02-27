from coapthon.server.coap import CoAP
import Exam_Resource2


class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        self.add_resource('pir_sensor/', Exam_Resource2.PIR_sensor(coap_server=self))
        self.add_resource('buzzer/', Exam_Resource2.Buzzer(coap_server=self))

        self.add_resource('th_sensor/', Exam_Resource2.TH_sensor(coap_server=self))
        self.add_resource('led/', Exam_Resource2.LED(coap_server=self))


def main():
    server = CoAPServer("0.0.0.0", 5683)
    print(server.server_address)
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")


if __name__ == '__main__':
    main()