var Vent = Vent || {};

var MAX_SAMPLES = 500;

Vent.settings = {'VT': 0, 'FiO2': 0, 'PEEP': 0, 'RR': 0}
Vent._inFocus = false
Vent.sensorReadings = {'Ppeak': 0, 'PEEP': 0, 'VT': 0, 'RR': 0, 'FiO2': 0, 'IE': 0}
Vent.MODES = ['VCV', 'PCV', 'PSV'];

Vent._charts = {};
Vent._x = {};
Vent._y = {};
Vent._xaxis = {};
Vent._yaxis = {};
Vent._paths = {};
Vent._lines = {};

Vent._pressure = [];
Vent._humidity = [];
Vent._temperature = [];
Vent._last = 0;

Vent._timer = null;
Vent._requested = 1;

Vent.getdata = function() {
    var dataset = []
    for (var i = 0; i < 20; i++) {
	var y = d3.randomUniform(-50,50)();
	dataset.push({"x": i, "y": y});
    }
    return dataset
}

Vent.updateData = function(field, data) {
    Vent._x[field].domain(d3.extent(data, function(d) { return d.x; }))
    Vent._y[field].domain([d3.min(data, function(d) { return d.y; }),
			   d3.max(data, function(d) { return d.y; })]);

    Vent._charts[field].selectAll(".yaxis")
        .call(Vent._yaxis[field]);
    
    Vent._lines[field] = d3.line()
        .x(function(d) { return Vent._x[field](d.x); }) // set the x values for the line generator
        .y(function(d) { return Vent._y[field](d.y); }) // set the y values for the line generator

    Vent._paths[field].attr("d", Vent._lines[field](data));

}

Vent.initChart = function(field) {

    // setup margins
    var select = "#"+field
    var margin = {top: 5, right: 5, bottom: 10, left: 25},
	width = $(select).innerWidth() - margin.left - margin.right,
	height = $(select).innerHeight() - margin.top - margin.bottom;
    
    Vent._charts[field]  = d3.select(select)
	.append("svg")
	.attr("height", height + margin.top + margin.bottom)
	.attr("width", width + margin.left + margin.right)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var data = Vent.getdata();

    // xaxis
    Vent._x[field] = d3.scaleLinear()
    	.range([0, width]);
    Vent._xaxis[field] = d3.axisBottom().scale(Vent._x[field]);
    Vent._charts[field].append("g")
        .attr("class", "xaxis")
        .attr("transform", "translate(0," + height + ")");
    
    // yaxis
    Vent._y[field] = d3.scaleLinear()
	.range([height, 0]);
    Vent._yaxis[field] = d3.axisLeft().scale(Vent._y[field]);    
    Vent._charts[field].append("g")
        .attr("class", "yaxis");

    // path
    Vent._paths[field] = Vent._charts[field].append("path")
	.attr("class", "line")

}

Vent.max = function(arr, count) {    
    for (var i = arr.length; i > count; i--) {
	arr.shift();
    }
}

// Generic async request. Log non-200 responses to the console.
//
// Params:
//   method - HTTP Verb: GET, POST, PUT, PATCH, DELETE
//   url - endpoint to fetch
//   data - JSONable request body
// Returns: status, JSON body
//
Vent.asyncReq = async function(method, url, data = null) {
    let options = {
        method,
        url,
        credentials: 'include'
    };
    if (data != null) {
        data = JSON.stringify(data);
        options.headers = {...options, 'Content-Type': 'application/json'};
        options.body = data;
    }
    try {
        const res = await fetch(url, options);
        const contentType = res.headers.get("content-type");
        let resBody;
        if (contentType && contentType.indexOf("application/json") !== -1) {
            resBody = await res.json();
        } else {
            resBody = await res.text();
        }

        return [res.status, resBody];

    } catch (e) {
        console.log(`${method} ${url} threw error: ${e}`);
    }
};

Vent.check = function() {
    $.get('/sensors?count='+Vent._requested,
        {},
        function(response) {
            for (var i=0; i<response.samples; i++) {
                if (response.times[i] > Vent._last) {
                    Vent._pressure.push({"x": response.times[i], "y": response.pressure[i]});
                    Vent._temperature.push({"x": response.times[i], "y": response.temperature[i]});
                    Vent._humidity.push({"x": response.times[i], "y": response.humidity[i]});
                    Vent._last = response.times[i];
                }
                else {
                    console.warn('.');
                }
            }
            Vent.max(Vent._pressure, MAX_SAMPLES);
            Vent.max(Vent._temperature, MAX_SAMPLES);
            Vent.max(Vent._humidity, MAX_SAMPLES);
            Vent.updateData('pressure', Vent._pressure);
            Vent.updateData('temperature', Vent._humidity);
            Vent.updateData('humidity', Vent._temperature);
    });
}

Vent.post = function(command, payload) {

    $.post(command, payload,
        function(response) {
            console.log(response);
        });
};

Vent.refresh = function() {
    if (Vent._timer != null) {
        clearInterval(Vent._timer);
        Vent._timer = null;
        $("#refresh").html("Play");
    }
    else {
        Vent._requested = 1
	// replace with a more efficient update
        Vent._timer = setInterval(Vent.check, 100);
        $("#refresh").html("Pause");
    }
};

Vent.alarm = function(msg) {
    $('#alarms').html(msg);
};

Vent.silence = function() {
    $('#alarms').html("");
}

Vent.listen = function() {
    document.addEventListener('keydown', function(event) {
        switch(event.code) {
            case "KeyQ": 
                Vent.triggerAlarm("high", "peep");
                break;
            case "KeyW": 
                Vent.triggerAlarm("medium", "ppeak");
                break;
            case "KeyE": 
                Vent.triggerAlarm("low", "vt");
                break;
            case "KeyR": 
                Vent.silenceAlarm();
                break;
            case "KeyA":
                return Vent.silence();
            case "KeyS":
                return Vent.alarm('boost');
            case "KeyJ":
                if (Vent._inFocus) {
                    Vent.decrementValue();
                    break;
                }
                else return Vent.menu_scroll(-1);
            case "KeyK":
                if (Vent._inFocus) {
                    Vent.updateSettings();
                    Vent._inFocus = false;
                    $('.control').removeClass('focused');
                    break;
                }
                else return Vent.menu_focus();
            case "KeyL":
                if (Vent._inFocus) {
                    Vent.incrementValue();
                    break;
                }
                else return Vent.menu_scroll(1);
            case "KeyP":
                return Vent.refresh();
            default:
                console.warn('unknown event');
        }
    });
};  

Vent.menu = function(choices) {
    var markup = [];
    for( var i = 0; i < choices.length; i++) {
        let val = '';
        if (typeof Vent[choices[i]] !== 'undefined') val = Vent[choices[i]];
        console.log(val);
        markup.push(
            DIV({
            'class' : 'control',
            'id' : 'menu_'+i
            },
                DIV({"class":"pinputcell"}, choices[i]) +
                DIV({'id': choices[i]}, `${val}`)
            )
        );
    }
    $('#controls').html(markup.join(""));
    Vent._choices = choices;
    Vent._focus = 0;
    Vent.menu_focus();
};

Vent.menu_focus = function() {
    $('.control').removeClass('focused');
    $('#menu_'+Vent._focus).addClass('focused');
    Vent._inFocus = true
};

Vent.menu_highlight = function() {
    $('.control').removeClass('highlighted');
    $('#menu_'+Vent._focus).addClass('highlighted');
};

Vent.menu_scroll = function(dir) {
    Vent._focus += dir;
    if (Vent._focus < 0) {
        Vent._focus = Vent._choices.length - 1;
    }
    if (Vent._focus >= Vent._choices.length) {
        Vent._focus = 0;
    }
    Vent.menu_highlight();
};

Vent.menu_select = function() {
    // hacky just to show ui
    switch(Vent._choices[Vent._focus]) {
        case 'VT':
        case 'FiO2':
        case 'PEEP':
        case 'RR':
            Vent._inFocus = true
            break
        case "VC":
            return Vent.menu(["VT", "FiO2","PEEP", "RR", "BACK"]);
        case "BACK":
        default:
            return Vent.menu(["VC", "PS", "AC"]);
    }	
};

Vent.decrementValue = () => {
    const [field, id] = Vent.getFieldByFocus();
    
    Vent['settings'][field] -= 1;
    $(`#${id}`).text(`${Vent['settings'][field]}`);
}

Vent.incrementValue = () => {
    const [field, id] = Vent.getFieldByFocus();

    Vent['settings'][field] += 1;
    $(`#${id}`).text(`${Vent['settings'][field]}`);
}

Vent.getFieldByFocus = () => {
    let field, id;

    // TODO: custom increments based on field type
    switch(Vent._focus){
        case 0: 
            // switch mode
            break;
        case 1:
            // peep
            field = 'PEEP';
            id = 'peepValue';
            break;
        case 2: 
            // fio2
            field = 'FiO2';
            id = 'fio2Value';
            break;
        case 3:
            // rr
            field = 'RR';
            id = 'rrValue';
            break;
        case 4: 
            // vt
            field = 'VT';
            id = 'vtValue';
            break;
    }

    return [field, id];
}

Vent.updateSettings = () => {
    const [field, _] = Vent.getFieldByFocus();
    const data = { [field]: Vent['settings'][field] };
    Vent.asyncReq('POST', '/settings', data);
}

Vent.setTime = () => {
    const today = new Date();
    let ampm = today.toLocaleTimeString().split(" ")[1];
    let time = today.toLocaleTimeString().split(":");
    $("#time").html(`${time[0]}:${time[1]} ${ampm}`);
}

Vent.setDate = () => {
    const today = new Date();
    let longDate = today.toDateString().split(" ");
    longDate.shift();
    $("#date").html(longDate.join(" "));
}

Vent.initDataDOM = () => {
    // TODO change this so its scroll menu
    Vent._mode =  document.getElementById('modeValue');

    Vent._peepValue = document.getElementById('peepValue');
    Vent._peepValue.innerText = `${Vent.settings['PEEP']}`;

    Vent._fio2Value = document.getElementById('fio2Value');
    Vent._fio2Value.innerText = `${Vent.settings['FiO2']}`;

    Vent._rrValue = document.getElementById('rrValue');
    Vent._rrValue.innerText = `${Vent.settings['RR']}`;

    Vent._vtValue = document.getElementById('vtValue');
    Vent._vtValue.innerText = `${Vent.settings['VT']}`;
    
    Vent._choices = ['ALARM_SETTINGS', Vent._modeValue, Vent._peepValue, Vent._fio2Value, Vent._rrValue, Vent._vtValue]

    Vent._focus = 1;
    Vent.menu_highlight();
}

Vent.getAlarmCSSClassByType = () => {
    if (Vent._alarmType == 'high') return 'highEmergencyStat';
    else if (Vent._alarmType == 'medium') return'mediumEmergencyStat';
    else return 'lowEmergencyStat';
}

Vent.triggerAlarm = (type, stat) => {
    Vent.silenceAlarm();
    Vent._alarmType = type;
    Vent._alarmStat = stat;

    const alarmClass = Vent.getAlarmCSSClassByType;
    $(`#${stat}`).addClass(alarmClass);
    $(`#controls .alarmSettings`).addClass(alarmClass);
    $(`#${stat} .stat-value`).addClass('whiteText');
    $(`#${stat} .stat-value-unit`).addClass('whiteText');
    $(`#dateAndTime`).addClass('alarm');
    $('#alarm').css('display', 'inline-flex');
    $('#alarm').addClass(alarmClass);
}

Vent.silenceAlarm = () => {
    const alarmClass = Vent.getAlarmCSSClassByType;

    $(`#${Vent._alarmStat}`).removeClass(alarmClass);
    $(`#controls .alarmSettings`).removeClass(alarmClass);
    $(`#${Vent._alarmStat} .stat-value`).removeClass('whiteText');
    $(`#${Vent._alarmStat} .stat-value-unit`).removeClass('whiteText');
    $(`#dateAndTime`).removeClass('alarm');
    $('#alarm').css('display', 'none');
    $(`#alarm`).removeClass('alarm');

    Vent._alarmType = null;
    Vent._alarmStat = null;
}

$(document).ready(function() {
    console.log("Vent online");
    Vent.initChart('pressure');
    Vent.initChart('temperature');
    Vent.initChart('humidity');

    $("#refresh").click(Vent.refresh);
    $("#breath").click(function() {
	var seconds = $('#seconds').val()
	var duty = $('#duty').val()
	Vent.post('/breath', {
	    'seconds' : seconds,
	    'duty' : duty
	});
    });

    Vent.listen();
    // Vent.menu(["VC", "PS", "AC"]);
    Vent.initDataDOM();
    Vent.refresh();
    
    Vent.setTime();
    setInterval(Vent.setTime, 60000);
    Vent.setDate();
});
