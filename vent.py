import sys
import signal
import logging
from multiprocessing import Process, Queue, Value, Array

try:
    import valve
except:
    import mock_valve as valve

try:
    import ui
except:
    import mock_ui as ui

try:
    import sensor
except:
    import mock_sensor as sensor

    
PORT = 3000


from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'WARNING',
        'handlers': ['wsgi']
    }
})


from flask import Flask, request, render_template, jsonify
app = Flask(__name__, static_folder='static')

class GlobalState():
    idx = Value('i', 0)
    count = Value('i', 10000)
    times = Array('d', range(10000))
    tank_pressure = Array('d', range(10000))
    breath_pressure = Array('d', range(10000))
    flow = Array('d', range(10000))
    v1_pressure = Array('d', range(count.value))
    v2_pressure = Array('d', range(count.value))
    breathing = Value('i', 0)
    rr = Value('i', 0)
    vt = Value('i', 0)
    fio2 = Value('i', 0)
    peep = Value('i', 0)
    
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
        'pressure' : g.v1_pressure[last:curr],
        'humidity' : g.v2_pressure[last:curr],
        'temperature' : g.flow[last:curr]
    }
    return jsonify(values)

@app.route('/settings', methods=['POST'])
def update_sensors():
    if 'VT' in request.json:
        g.vt = request.json['VT']

    if 'RR' in request.json:
        g.rr = request.json['RR']

    if 'PEEP' in request.json:
        g.peep = request.json['PEEP']

    if 'FiO2' in request.json:
        g.fio2 = request.json['FiO2']

    return jsonify({})

@app.route('/breath', methods=['POST'])
def breath():
    seconds = int(request.form.get('seconds', '0'))
    duty = int(request.form.get('duty', '0'))
    if seconds and duty:
        valve.breath_pwm(g.breathing, duty, seconds)

    return jsonify({})

@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == '__main__':
    # start sensor process
    p = Process(target=sensor.sensor_loop, args=(
        g.times,
        g.tank_pressure,
        g.breath_pressure,
        g.v1_pressure,
        g.v2_pressure,
        g.flow,
        g.idx,
        g.count,
        60
    ))
    p.start()

    # start app
    app.run(debug=True, host='0.0.0.0', port=PORT)
    
