import sys
import signal
from multiprocessing import Process, Queue, Value, Array
import sensor
import valve

PORT = 3000

from flask import Flask, request, render_template, jsonify
app = Flask(__name__, static_folder='static')

class GlobalState():
    idx = Value('i', 0)
    count = Value('i', 10000)
    times = Array('d', range(10000))
    pressure = Array('d', range(10000))
    humidity = Array('d', range(10000))
    temperature = Array('d', range(10000))
    breathing = Value('i', 0)

    
g = GlobalState()

@app.route('/sensors')
def sensors():
    curr = g.idx.value
    last = curr - int(request.args.get('count', '20'))
    if last < 0:
        last = 0
    times = g.times[last:curr]
    values = {
        'samples' : len(times),
        'times' : times,
        'pressure' : g.pressure[last:curr],
        'temperature' : g.temperature[last:curr],
        'humidity' : g.humidity[last:curr]
    }
    return jsonify(values)

@app.route('/breath', methods=['POST'])
def breath():
    seconds = int(request.form.get('seconds', '0'))
    duty = int(request.form.get('duty', '0'))
    if seconds and duty:
        g.breathing.value = 1
        valve.breath_pwm(g.breathing, duty, seconds);

    return jsonify({})

@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == '__main__':

    # start bluetooth
    #bleno.on('stateChange', onStateChange)
    #bleno.on('advertisingStart', onAdvertisingStart)
    #bleno.start()

    # start sensors
    
    p = Process(target=sensor.sensor_loop, args=(
        g.times,
        g.pressure,
        g.humidity,
        g.temperature,
        g.idx,
        g.count))
    
    p.start()
    
    app.run(debug=True, host='0.0.0.0', port=PORT)
    


#print ('Hit <ENTER> to disconnect')

#if (sys.version_info > (3, 0)):
#    input()
#else:
#    raw_input()
    
#bleno.stopAdvertising()
#bleno.disconnect()
    
#print ('terminated.')
#sys.exit(1)
