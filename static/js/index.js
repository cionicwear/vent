var Vent = Vent || {};

var MAX_SAMPLES = 500;

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
	.transition()
        .duration(1000)
        .call(Vent._yaxis[field]);

    
    Vent._lines[field] = d3.line()
        .x(function(d) { return Vent._x[field](d.x); }) // set the x values for the line generator
        .y(function(d) { return Vent._y[field](d.y); }) // set the y values for the line generator

    Vent._paths[field].attr("d", Vent._lines[field](data));

}

Vent.initChart = function(field) {

    // setup margins
    var select = "#"+field
    var margin = {top: 15, right: 15, bottom: 30, left: 50},
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

Vent.check = function() {
    $.get('/sensors?count=1',
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
    Vent.initChart('pressure');
    Vent.initChart('temperature');
    Vent.initChart('humidity');

    // replace with a more efficient update
    setInterval(Vent.check, 100);
});
