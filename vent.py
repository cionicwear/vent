#!/usr/bin/env python3

import time
import sys
import signal
import logging
import argparse
from multiprocessing import Process, Queue, Value, Array
from sensor import mock_sensor

try:
    from actuator import valve
except Exception as e:
    logging.warn(e)
    from actuator import mock_valve as valve

try:
    from sensor import sensor
except Exception as e:
    logging.warning(e)
    from sensor import mock_sensor as sensor

    
PORT = 3000
MODE_DEMO = 0
MODE_VC = 1
MODE_PC = 2

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

MODE_VC = 1
MODE_PC = 2

class GlobalState():
    idx = Value('i', 0)
    count = Value('i', 10000)
    times = Array('d', range(10000))
    # sensor streams
    in_pressure_1 = Array('d', range(count.value))
    in_pressure_2 = Array('d', range(count.value))
    in_flow = Array('d', range(count.value))
    ex_pressure_1 = Array('d', range(count.value))
    ex_pressure_2 = Array('d', range(count.value))
    ex_flow = Array('d', range(count.value))
    o2_percent = Array('d', range(count.value))
    # derived metrics
    flow = Array('d', range(count.value))
    volume = Array('d', range(count.value))
    tidal = Array('d', range(count.value))
    pmin = Array('d', range(count.value))
    pmax = Array('d', range(count.value))
    expire = Array('d', range(count.value))
    breathing = Value('i', 0)
    peeping = Value('i', 0)
    # ventilator settings
    mode = MODE_VC
    inspire = 1
    rr = 60
    ie = 0.2
    vt = 600
    fio2 = 21
    peep = 5
    # fine grain settings
    top = Value('i', 0)
    pwait = Value('d', 0)
    pcross = Value('d', 0)
    assist = Value('d', 0)
    oxp = Value('i', 0)
    
g = GlobalState()

def percent_difference(setting, measured):
    return abs(setting-measured) / setting

def absolute_difference(setting, measured):
    return abs(setting-measured)

@app.route('/sensors')
def sensors():
    curr = g.idx.value

    o2 = g.o2_percent[curr]
    ie = g.ie if g.expire[curr] == 0 else g.expire[curr]/g.inspire
    rr = 60.0/ie
    tidal = g.tidal[curr]
    pmin = g.pmin[curr]
    pmax = g.pmax[curr]
    
    last = curr - int(request.args.get('count', '20'))
    if last < 0:
        times = g.times[last:] + g.times[:curr]
        pressures = g.in_pressure_2[last:] + g.in_pressure_2[:curr]
        flows = g.flow[last:] + g.flow[:curr]
        volumes = g.volume[last:] + g.volume[:curr]
    else:
        times = g.times[last:curr]
        pressures = g.in_pressure_2[last:curr]
        flows = g.flow[last:curr]
        volumes = g.volume[last:curr]

         
    alarm_plat = False
    alarm_power = False
    alarm_pmax = pmax > 35  # verify hw this should be thresholded
    alarm_pmin = absolute_difference(g.peep, pmin) > 0.5
    alarm_fio2 = percent_difference(g.fio2, o2) > 0.2
    alarm_tidal = percent_difference(g.vt, tidal) > 0.2
    alarm_rate = percent_difference(g.rr, rr) > 0.2
    
    values = {
        'samples'  : len(times),
        'times'    : times,
        'pressure' : pressures,
        'flow'     : flows,
        'volume'   : volumes,
        'tidal'    : tidal,
        'pmin'     : pmin,
        'pmax'     : pmax,
        'ie'       : round(ie),
        'rr'       : round(rr),
        'o2'       : o2,
        'alarms'   : {
            'ppeak'  : alarm_pmax,
            'peep'  : alarm_pmin,
            'plat'  : alarm_plat,
            'fio2'  : alarm_fio2,
            'rate'  : alarm_rate,
            'vt'    : alarm_tidal,
            'power' : alarm_power
        }
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

@app.route('/tune', methods=['POST'])
def tune():
    if 'top' in request.json:
        g.top.value = request.json['top']
        logging.warning("setting top to %d" % (g.top.value,))
        
    if 'pcross' in request.json:
        g.pcross.value = request.json['pcross']
        logging.warning("setting peep cross to %f" % (g.pcross.value,))

    if 'oxp' in request.json:
        g.oxp.value = request.json['oxp']
        logging.warning("setting oxp to %d" % (g.oxp.value,))

    return jsonify({})

@app.route('/')
def hello():
    return render_template('index.html')

def main(args):
    # update global state based on params
    g.rr = 60 / (args.inspire + args.expire)
    g.ie = args.expire/args.inspire
    g.inspire = args.inspire
    g.mode = MODE_PC if (args.rampdn > args.inspire/2) else MODE_VC
    g.vt = args.vtidal
    g.fio2 = args.fio2
    g.peep = args.pcross
    # set fine tuning params
    g.top.value = args.top
    g.pwait.value = args.pwait
    g.pcross.value = args.pcross
    g.assist.value = args.assist

    g.oxp.value = 0
    
    print("Starting vent rr:%d vt:%d fi02:%d peep:%d" % (g.rr, g.vt, g.fio2, g.peep))
    print("Fine grain top:%d assist:%f" % (g.top.value, g.assist.value))
    

    if args.mode == MODE_DEMO:
        # start sensor process
        p = Process(target=mock_sensor.sensor_loop, args=(
            g.times, g.flow, g.volume, g.tidal, g.o2_percent,
            g.pmin, g.pmax, g.expire, g.breathing, g.peeping,
            g.in_pressure_1, g.in_pressure_2, g.in_flow,
            g.ex_pressure_1, g.ex_pressure_2, g.ex_flow,
            g.idx, g.count, g.assist, g.pcross))
        p.start()
    else:
        # start sensor process
        p = Process(target=sensor.sensor_loop, args=(
            g.times, g.flow, g.volume, g.tidal, g.o2_percent,
            g.pmin, g.pmax, g.expire, g.breathing, g.peeping,
            g.in_pressure_1, g.in_pressure_2, g.in_flow,
            g.ex_pressure_1, g.ex_pressure_2, g.ex_flow,
            g.idx, g.count, g.assist, g.pcross))
        p.start()

        # wait for sensors to initialize
        time.sleep(10)
    
        # start valve process
        v = Process(target=valve.valve_loop, args=(
            g.breathing, g.peeping, g.oxp,
            args.start,  args.rampup,
            g.top, (args.inspire - args.rampup - args.rampdn),
            args.pause,  args.rampdn,
            args.bottom, args.expire,
            g.pwait,
            args.count))
        v.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run vent')
    # mode
    parser.add_argument('-m', '--mode', default=MODE_VC, type=int, help='0 = Demo 1 = Volume Control 2 = Pressure Control')
    parser.add_argument('-a', '--assist', default=0, type=float, help='pressure trigger for assist 0 = no assist')
    # times
    parser.add_argument('-i', '--inspire', default=1.0, type=float, help='seconds of inspiration time')
    parser.add_argument('-e', '--expire',  default=2.0, type=float, help='seconds of expiration time')
    parser.add_argument('-u', '--rampup',  default=0.1, type=float, help='seconds to ramp from <start> to <top>')
    parser.add_argument('-d', '--rampdn',  default=0.0, type=float, help='seconds to ramp from <top> to <pause> ')
    # thresholds
    parser.add_argument('-s', '--start',   default=80,  type=int, help='percent open at start of breathing cycle')
    parser.add_argument('-t', '--top',     default=100, type=int, help='percent open at peak of breathing cycle')
    parser.add_argument('-p', '--pause',   default=0,   type=int, help='percent open at pause in breathing cycle')
    parser.add_argument('-b', '--bottom',  default=0,   type=int, help='percent open at end of breathing cycle')
    # counts
    parser.add_argument('-c', '--count',   default=30,  type=int, help='number of breathing cycles')
    # settings
    parser.add_argument('-f', '--fio2',    default=20,  type=int,  help='fio2')
    parser.add_argument('-v', '--vtidal',  default=300,  type=int, help='tidal volume')
    # peep
    parser.add_argument('-w', '--pwait',   default=1.0,   type=float, help='seconds to wait before closing peep')
    parser.add_argument('-x', '--pcross',  default=5,     type=float, help='peep crossing threshold')
    # run main loop
    g_args = parser.parse_args(sys.argv[1:])
    main(g_args)
    # start server
    app.run(debug=False, host='0.0.0.0', port=PORT)
    
