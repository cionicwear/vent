import os
import sys
import signal
from multiprocessing import Process, Queue, Value, Array
import sensor

# try:
#     import valve
# except:
#     import mock_valve as valve

try:
    import ui
except:
    import mock_ui as ui
    
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


from flask import Flask, request, render_template, jsonify, send_from_directory
app = Flask(__name__, static_folder='frontend/build')

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
    # if seconds and duty:
    #     valve.breath_pwm(g.breathing, duty, seconds)

    return jsonify({})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
    # return render_template('index.html')


if __name__ == '__main__':

    # start sensor process
    p = Process(target=sensor.sensor_loop, args=(
        g.times,
        g.pressure,
        g.humidity,
        g.temperature,
        g.idx,
        g.count))
    p.start()

    # start ui process
    u = Process(target=ui.ui_loop)
    u.start()

    # start app
    app.run(debug=True, host='0.0.0.0', port=PORT)
    
