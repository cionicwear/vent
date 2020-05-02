var Vent = Vent || {};
var Samples = Samples || {};

var SAMPLES = 200;

Vent._count = 0;
Vent._index = 0;
Vent._clip = 0;

Vent._data = {
    'humidity'    : [],
    'temperature' : [],
    'pressure'    : []
};

Vent._chart_data = {
    'humidity'    : [],
    'temperature' : [],
    'pressure'    : []
};

Vent._charts = {};
Vent._x = {};
Vent._y = {};
Vent._xaxis = {};
Vent._yaxis = {};
Vent._paths = {};

Vent._bounds = {
    'humidity' : [4000,0],
    'temperature' : [4000,0],
    'pressure' : [4000,0]
}

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

    Vent._charts[field].selectAll(".xaxis")
	.transition()
        .duration(1000)
        .call(Vent._xaxis[field]);

    Vent._charts[field].selectAll(".yaxis")
	.transition()
        .duration(1000)
        .call(Vent._yaxis[field]);

    
    var line = d3.line()
        .x(function(d) { return Vent._x[field](d.x); }) // set the x values for the line generator
        .y(function(d) { return Vent._y[field](d.y); }) // set the y values for the line generator
        .curve(d3.curveMonotoneX) // apply smoothing to the line

    Vent._paths[field].attr("d", line(data));

}

Vent.initChart = function(field) {

    // setup margins
    var margin = {top: 15, right: 15, bottom: 30, left: 30},
	width = $(field).innerWidth() - margin.left - margin.right,
	height = $(field).innerHeight() - margin.top - margin.bottom;
    
    Vent._charts[field]  = d3.select(field)
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

    // update data
    Vent.updateData(field, data);
}

Vent.update = function(data, field, num) {
    var samples = data[field];
    
    for (var i=0; i<num; i++) {
	var sample = samples[i];
	if (sample < Vent._bounds[field][0]) {
	    Vent._charts[field].options.axisY.minimum = sample;
	    Vent._bounds[field][0] = sample;
	}
	if (sample > Vent._bounds[field][1]) {
	    Vent._charts[field].options.axisY.maximum = sample;
	    Vent._bounds[field][1] = sample;
	}
	Vent._data[field].shift();
	Vent._data[field].push(sample);
    }
};

Vent.check = function() {
    $.get('/sensors',
	  {},
	  function(response) {
	      Vent._count += response.samples;
	      Vent._clip += response.samples;
	      console.warn(Vent._count, Vent._clip);
	      /*
	      Vent.update(response, 'pressure', response.samples);
	      Vent.update(response, 'temperature', response.samples);
	      Vent.update(response, 'humidity', response.samples);
*/
	      //Vent.chart(response, 'humidity', Vent._humidity, Vent._humidity_line);
	      //Vent.chart(response, 'temperature', Vent._temp, Vent._temp_line);
	  });
}

Vent.update_chart = function(field) {
    //Vent._chart_data[field].shift();
    //Vent._chart_data[field].push({x: Vent._index, y:Vent._data[field][Vent._index-Vent._clip]});
    //Vent._charts[field].render();
};

Vent.chart = function() {
    if (Vent._index < (Vent._count-1)) {
	Vent._index += 1;
	Vent.update_chart('pressure');
	Vent.update_chart('temperature');
	Vent.update_chart('humidity');
    }
}


Vent.respond = function(command, payload) {

    $.post('/respond',
	   {
	       'command' : command,
	       'payload' : payload
	   },
	   function(response) {
	       console.log(response);
	   });

};

$(document).ready(function() {
    console.log("Vent online");

    Vent._count = SAMPLES;
    Vent._index = SAMPLES;
    Vent.initChart('#pressure');
    //Vent.initChart('#temperature');
    //Vent.initChart('#humidity');

    // consider web sockets
    setInterval(Vent.check, 1000);
    setInterval(Vent.chart, 16.6);
});
