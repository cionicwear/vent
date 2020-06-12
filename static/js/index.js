var Vent = Vent || {};

var MAX_SAMPLES = 100;

Vent.settings = {'VT': 0, 'FiO2': 0, 'PEEP': 0, 'RR': 0, 'PINSP': 0, 'IE': 0}
Vent._inFocus = false
Vent.sensorReadings = {'Ppeak': 0, 'PEEP': 0, 'VT': 0, 'RR': 0, 'FiO2': 0, 'IE': 0}
Vent.MODES = ['VCV', 'PCV', 'PSV'];
Vent.MODE_TO_INPUTS = {
    'VCV': ['PEEP', 'FiO2', 'RR', 'VT'],
    'PCV': ['PINSP', 'RR', 'IE', 'PEEP'],
    'PSV': ['FiO2', 'PINSP', 'RR', 'PEEP']
}
Vent._mode = 'VCV';

Vent._charts = {};
Vent._x = {};
Vent._y = {};
Vent._xaxis = {};
Vent._yaxis = {};
Vent._paths = {};
Vent._lines = {};

Vent._pressure = [];
Vent._flow = [];
Vent._volume = [];
Vent._last = 0;

Vent._timer = null;
Vent._requested = 1;
Vent._isConfirming = false;
Vent._confirmSelected= true;
Vent._oldVal = {};
Vent._ccProgress = null;

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
    var margin = {top: 5, right: 5, bottom: 10, left: 35},
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

Vent.setMeasure = function(selector, value) {
    $(selector).find('.stat-value').html(value);
};

Vent.check = function() {
    $.get('/sensors?count='+Vent._requested,
        {},
        function(response) {
            for (var i=0; i<response.samples; i++) {
                if (response.times[i] > Vent._last) {
                    Vent._pressure.push({"x": response.times[i], "y": response.pressure[i] / 98.0665 });
                    Vent._flow.push({"x": response.times[i], "y": response.flow[i]});
                    Vent._volume.push({"x": response.times[i], "y": response.volume[i]});
                    Vent._last = response.times[i];
                }
                else {
                    console.warn('.');
                }
            }
	    var pmin = response.pmin / 98.0665; // conversion from pascal to cmH2O
	    Vent.max(Vent._flow, MAX_SAMPLES);
            Vent.max(Vent._pressure, MAX_SAMPLES);
            Vent.max(Vent._volume, MAX_SAMPLES);
	    Vent.updateData('flow', Vent._flow);
            Vent.updateData('pressure', Vent._pressure);
            Vent.updateData('volume', Vent._volume);
	    Vent.setMeasure('#peep', pmin.toFixed(1));
	    Vent.setMeasure('#vt', response.tidal.toFixed(0));
	    Vent.setMeasure('#ieRatio', "1:"+response.ie.toFixed(0));
	    Vent.setMeasure('#rr', response.rr.toFixed(0));
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
                Vent.triggerAlarm("high", "peep", "high emergency");
                break;
            case "KeyW": 
                Vent.triggerAlarm("medium", "ppeak", 'med emergency');
                break;
            case "KeyE": 
                Vent.triggerAlarm("low", "vt", 'low emergency');
                break;
            case "KeyR": 
                Vent.silenceAlarm();
                break;
            case "KeyA":
                return Vent.silence();
            case "KeyS":
                return Vent.alarm('boost');
            case "KeyJ":
                if (Vent._isConfirming) {
                    Vent.ccScroll(Vent._confirmSelected, Vent._focus);
                    break;
                }
                if (Vent._inFocus) {
                    Vent.decrementValue(Vent._focus);
                    break;
                }
                else return Vent.menu_scroll(-1);
            case "KeyK":
                const menuItem = Vent._focus;
                // handle Modes
                if (menuItem === 1 && Vent._inFocus) {
                    Vent._inFocus = false;
                    Vent.resetCCUI(menuItem);
                    $(".elipseContainer img").attr("src","./../static/img/elipse.svg");
                    $(".elipseContainer .activeElipse").attr("src","./../static/img/active_elipse.svg");

                    // update choices in UI
                    const inputs = Vent.MODE_TO_INPUTS[Vent._mode];
                    Vent._choices = ['ALARM', 'MODE', ...inputs];
                    for (let i = 0; i < 4; i++) {
                        $(`#menu${i+2}Title`).html(`${inputs[i]}`);
                        $(`#menu${i+2}Value`).html(`${Vent['settings'][inputs[i]]}`);
                    }
                    break;
                }

                // handle Inputs
                else if (Vent._isConfirming) {
                    Vent._inFocus = false;
                    Vent._isConfirming = false;
                    Vent.submitCCUI(Vent._confirmSelected, Vent._focus);
                    break;
                }
                else if (Vent._inFocus) {
                    $('#menu_'+menuItem+' .confirmCancel').css('display', 'flex');
                    $('#menu_'+menuItem+' .confirmCancel .confirm').addClass('ccActive');
                    Vent._isConfirming = true;
                    break;
                }
                else return Vent.menu_focus();
            case "KeyL":
                if (Vent._isConfirming) {
                    Vent.ccScroll(Vent._confirmSelected, Vent._focus);
                    break;
                }
                if (Vent._inFocus) {
                    Vent.incrementValue(Vent._focus);
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

Vent.menu_focus = function() {
    $('.control').removeClass('focused');
    $('#menu_'+Vent._focus).addClass('focused');
    Vent._inFocus = true

    // store old value
    const [field, _] = Vent.getFieldByFocus(Vent._focus);
    Vent._oldVal[field] = Vent['settings'][field];

    // show progress bar if exists (ie not alarms or mode)
    if (field != 'MODE' && field != 'ALARM') {
        Vent.updateCCProgressBar(field, Vent['settings'][field]);
    }
    // we're working with modes
    else if (field === 'MODE') {
        $(".elipseContainer img").attr("src","./../static/img/selected_elipse.svg");
        $(".elipseContainer .activeElipse").attr("src","./../static/img/selected_active_elipse.svg");
    }
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

Vent.decrementValue = (focusElem) => {
    const [field, id] = Vent.getFieldByFocus(focusElem);
    
    // TODO: custom increments based on field type
    // TODO: custom bounds based on field type
    if (field === 'MODE') {
        const idx = Vent.MODES.indexOf(Vent._mode);
        if (idx === 0) return;
        
        Vent._mode = Vent.MODES[idx - 1];
        $(`#${id}`).text(`${Vent._mode}`);

        // change elipses to match current idx
        Vent.updateElipses(idx - 1);
    }

    if (Vent['settings'][field] > 0) {
        Vent['settings'][field] -= 1;
        $(`#${id}`).text(`${Vent['settings'][field]}`);
        Vent.updateCCProgressBar(field, Vent['settings'][field]);
    }
}

Vent.incrementValue = (focusElem) => {
    const [field, id] = Vent.getFieldByFocus(focusElem);
    // TODO: custom increments based on field type
    // TODO: custom bounds based on field type
    if (field === 'MODE') {
        const idx = Vent.MODES.indexOf(Vent._mode);
        if (idx === Vent.MODES.length - 1) return;
        Vent._mode = Vent.MODES[idx + 1];
        $(`#${id}`).text(`${Vent._mode}`);

        // change elipses to match current idx
        Vent.updateElipses(idx + 1);
    }

    else if (Vent['settings'][field] < 10) {
        Vent['settings'][field] += 1;
        $(`#${id}`).text(`${Vent['settings'][field]}`);
        Vent.updateCCProgressBar(field, Vent['settings'][field]);
    }
}

Vent.updateElipses = (elipseNum) => {
    $(".elipseContainer .activeElipse").removeClass("activeElipse");
    $(".elipseContainer img").attr("src","./../static/img/selected_elipse.svg");
    $(`#elipse${elipseNum}`).attr("src","./../static/img/selected_active_elipse.svg");
    $(`#elipse${elipseNum}`).addClass("activeElipse");
}

Vent.getFieldByFocus = (focusElem) => {
    let field, id;

    // TODO: change cases based on active mode
    switch(focusElem){
        case 0: 
            // alarm settings
            field = 'ALARM';
            break;
        case 1: 
            // switch mode
            field = 'MODE';
            id = 'modeValue'
            break;
        case 2:
            // peep
            field = Vent.MODE_TO_INPUTS[Vent._mode][0];
            //'PEEP';
            id = 'menu2Value';
            break;
        case 3: 
            // fio2
            field = field = Vent.MODE_TO_INPUTS[Vent._mode][1];
            id = 'menu3Value';
            break;
        case 4:
            // rr
            field = field = Vent.MODE_TO_INPUTS[Vent._mode][2];
            id = 'menu4Value';
            break;
        case 5: 
            // vt
            field = field = Vent.MODE_TO_INPUTS[Vent._mode][3];
            id = 'menu5Value';
            break;
    }

    return [field, id];
}

Vent.updateSettings = (confirmed, focusElem) => {
    const [field, id] = Vent.getFieldByFocus(focusElem);
    if (confirmed) {
        // update settings
        const data = { [field]: Vent['settings'][field] };
        Vent.asyncReq('POST', '/settings', data);
    } else {
        // set back to old val + reset UI
        Vent['settings'][field] = Vent._oldVal[field];
        Vent._oldVal[field] = null;
        $(`#${id}`).text(`${Vent['settings'][field]}`);
    }

    Vent.resetCCUI(focusElem);
}

Vent.setTime = () => {
    const today = new Date();
    let time = today.toTimeString().split(":");
    $("#time").html(`${time[0]}:${time[1]}`);
}

Vent.setDate = () => {
    const today = new Date();
    let longDate = today.toDateString().split(" ");
    longDate.shift();
    $("#date").html(longDate.join(" "));
}

Vent.getAlarmCSSClassByType = () => {
    if (Vent._alarmType == 'high') return 'highEmergencyStat';
    else if (Vent._alarmType == 'medium') return'mediumEmergencyStat';
    else return 'lowEmergencyStat';
}

Vent.triggerAlarm = (type, stat, text) => {
    Vent.silenceAlarm();
    Vent._alarmType = type;
    Vent._alarmStat = stat;

    const alarmClass = Vent.getAlarmCSSClassByType;
    $(`#${stat}`).addClass(alarmClass);

    if (type === 'high') $(`#controls .alarmSettings`).addClass(alarmClass);
    $(`#${stat} .stat-value`).addClass('whiteText');
    $(`#${stat} .stat-value-unit`).addClass('whiteText');
    $(`#dateAndTime`).addClass('alarm');
    $('#alarm').css('display', 'inline-flex');
    $('#alarm').addClass(alarmClass);
    $('#alarm h2').html(text);
}

Vent.silenceAlarm = () => {
    const alarmClass = Vent.getAlarmCSSClassByType;

    $(`#${Vent._alarmStat}`).removeClass(alarmClass);
    $(`#controls .alarmSettings`).removeClass(alarmClass);
    $(`#${Vent._alarmStat} .stat-value`).removeClass('whiteText');
    $(`#${Vent._alarmStat} .stat-value-unit`).removeClass('whiteText');
    $(`#dateAndTime`).removeClass('alarm');
    $('#alarm').css('display', 'none');
    $(`#alarm`).removeClass(alarmClass);

    Vent._alarmType = null;
    Vent._alarmStat = null;
}

Vent.ccScroll = (isConfirmSelected, focusElem) => {
    if (isConfirmSelected) {
        $('#menu_'+focusElem+' .confirmCancel .confirm').removeClass('ccActive');
        $('#menu_'+focusElem+' .confirmCancel .cancel').addClass('ccActive');
        Vent._confirmSelected = false;
    } else {
        $('#menu_'+focusElem+' .confirmCancel .confirm').addClass('ccActive');
        $('#menu_'+focusElem+' .confirmCancel .cancel').removeClass('ccActive');
        Vent._confirmSelected = true;
    }
}

Vent.resetCCUI = (focusElem) => {
    $('#menu_'+focusElem+' .confirmCancel .cancel').removeClass('ccActive');
    $('#menu_'+focusElem+' .confirmCancel .cancel').removeClass('ccSubmit');
    $('#menu_'+focusElem+' .confirmCancel .confirm').removeClass('ccSubmit');

    $('#menu_'+focusElem+' .confirmCancel .confirm').css('display', 'flex');
    $('#menu_'+focusElem+' .confirmCancel .cancel').css('display', 'flex');

    $('#menu_'+focusElem+' .confirmCancel').css('display', 'none');
    $('#menu_'+focusElem+' .confirmCancel').css('top', '-86px');

    $('#menu_'+focusElem).removeClass('ccConfirmBorder');
    $('#menu_'+focusElem).removeClass('ccCancelBorder');
    $('.control').removeClass('focused');

    $('#menu_'+focusElem+' .confirmCancel .confirm').addClass('ccActive');
    Vent._confirmSelected = true;
}

Vent.submitCCUI = (isConfirmSelected, focusElem) => {
    // update top px to only show 1 elemement
    $('#menu_'+focusElem+' .confirmCancel').css('top', '-46px');

    if (isConfirmSelected) {
        $('#menu_'+focusElem+' .confirmCancel .cancel').css('display', 'none');
        $('#menu_'+focusElem+' .confirmCancel .confirm').addClass('ccSubmit');
        $('#menu_'+focusElem).addClass('ccConfirmBorder');

    } else {
        $('#menu_'+focusElem+' .confirmCancel .confirm').css('display', 'none');
        $('#menu_'+focusElem+' .confirmCancel .cancel').addClass('ccSubmit');
        $('#menu_'+focusElem).addClass('ccCancelBorder');
    }

    Vent.finishCCProgressBar(focusElem);

    setTimeout(function() {
        Vent.updateSettings(isConfirmSelected, focusElem);
    }, 500);
}

Vent.updateCCProgressBar = (field, val) => {
    $('#menu_'+Vent._focus+' .ccProgress').css('display', 'block');
    const elem = document.querySelector(`#menu_${Vent._focus} .ccBar`);
    // TODO: max value based on field instead of scale 0-10
    elem.style.width = val*10 + "%";
}

Vent.finishCCProgressBar = (focusElem) => {
    $('#menu_'+focusElem+' .ccProgress').css('display', 'none');
    Vent._inFocus = false;
    Vent._isConfirming = false;
}

$(document).ready(function() {
    console.log("Vent online");
    Vent.initChart('flow');
    Vent.initChart('pressure');
    Vent.initChart('volume');

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
    
    Vent._choices = ['ALARM', 'MODE', ...Vent.MODE_TO_INPUTS[Vent._mode]];
    Vent._focus = 1;
    Vent.menu_highlight();

    Vent.refresh();
    
    Vent.setTime();
    setInterval(Vent.setTime, 60000);
    Vent.setDate();
});
