# Mii temperature sensors usung ATC firmware: https://github.com/atc1441/ATC_MiThermometer

from bluepy.btle import Scanner, DefaultDelegate
import binascii, logging, struct, threading
import time
import sys


datastore = {}
mutex = threading.Lock()

logging.basicConfig(format='%(asctime)s %(filename)d:%(lineno) %(levelname): %(message)s', level=logging.DEBUG)

class ScanDelegate(DefaultDelegate):
    def __init__(self, datastore):
        DefaultDelegate.__init__(self)
        self._datastore = datastore

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

        global mutex
        with mutex:
            self._datastore[name] = {
                'name': name,
                'addr': dev.addr,
                'temp': unpacked[1]/10.0,
                'humi': unpacked[2],
                'bat_perc': unpacked[3],
                'bat_mv': unpacked[4],
                'rssi': dev.rssi,
                'lastseen': time.time()
            }



def doScan(datastore):
    scanner = Scanner().withDelegate(ScanDelegate(datastore))

    scanner.clear()
    scanner.start()

    while True:
        scanner.process()
        scanner.stop()
        scanner.start()
        scanner.clear()

def killAfterHours(hours):
    time.sleep(hours * 60 * 60)
    exit(0)


def cleanupLoop():
    while True:
        time.sleep(60)
        now = time.time()
        global mutex
        with mutex:
            if len(datastore) == 0:
                sys.exit(1)

            for key in datastore.keys():
                if now - datastore[key]['lastseen'] > 120:
                    del datastore[key]

threading.Thread(target=(lambda: doScan(datastore))).start()
threading.Thread(target=(lambda: killAfterHours(10))).start()
threading.Thread(target=(lambda: cleanupLoop())).start()

from bottle import Bottle, run, view

app = Bottle()


@app.route('/data.json')
def data_json():
    global mutex
    now = time.time()
    with mutex:
        return {'sensors' : [v for k, v in datastore.items()]}

@app.route('/')
@view('index')
def main():
    global mutex
    with mutex:
        return {'sensors' : [v for k, v in datastore.items()]}

@app.route('/metrics')
def metrics():
    global mutex
    with mutex:
        for k, v in datastore.items():
            yield f"atc_sensor_temp{{name=\"{v['name']}\"}} {v['temp']}\n"
            yield f"atc_sensor_humi{{name=\"{v['name']}\"}} {v['humi']}\n"
            yield f"atc_sensor_bat_perc{{name=\"{v['name']}\"}} {v['bat_perc']}\n"
            yield f"atc_sensor_bat_mv{{name=\"{v['name']}\"}} {v['bat_mv']}\n"
            yield f"atc_sensor_rssi{{name=\"{v['name']}\"}} {v['rssi']}\n"

run(app, host='0.0.0.0', port=80, server='paste')
