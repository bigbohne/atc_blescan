# Mii temperature sensors usung ATC firmware: https://github.com/atc1441/ATC_MiThermometer

from bluepy.btle import Scanner, DefaultDelegate
import binascii, logging, struct, threading
import time
import paho.mqtt.client as mqtt


logging.basicConfig(format='%(asctime)s %(filename)d:%(lineno) %(levelname): %(message)s', level=logging.DEBUG)

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        data = {}
        for entry in dev.getScanData():
            data[entry[0]] = entry[2]

        if 22 not in data or 9 not in data:
            return

        name = data[9]
        if not name.startswith('ATC_'):
            return

        data = binascii.a2b_hex(data[22])
        unpacked = struct.unpack('>8shBBHB', data)

        print(f'{dev.addr} {name}: {unpacked[1]/10.0}C {unpacked[2]}% - {unpacked[3]}% bat {unpacked[4]}mV')

        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqttc.connect("192.168.2.244")

        mqttc.publish(f"atc_sensor/{name}/temperature", unpacked[1]/10.0)
        mqttc.publish(f"atc_sensor/{name}/humidity", unpacked[2])
        mqttc.publish(f"atc_sensor/{name}/bat_percentage", unpacked[3])
        mqttc.publish(f"atc_sensor/{name}/bat_millivolt", unpacked[4])
        mqttc.publish(f"atc_sensor/{name}/rssi", dev.rssi)
        
        mqttc.loop()
        mqttc.loop()
        mqttc.loop()

        mqttc.disconnect()



def doScan():
    scanner = Scanner().withDelegate(ScanDelegate())

    scanner.clear()
    scanner.start()

    try:
        while True:
            scanner.process()
            scanner.stop()
            scanner.start()
            scanner.clear()
    finally:
        exit(1)

def killAfterHours(hours):
    time.sleep(hours * 60 * 60)
    exit(0)


threading.Thread(target=(lambda: doScan())).start()
threading.Thread(target=(lambda: killAfterHours(10))).start()