// Base Options

let base_options = {
  animation: {
    duration: 0 // general animation time
  },
  hover: {
      animationDuration: 0 // duration of animations when hovering an item
  },
  responsiveAnimationDuration: 0, // animation duration after a resize
  maintainAspectRatio: false,
  legend: {
    display: false
  },
  responsive: true,
  scales: {
    yAxes: [
      {
        gridLines: {
          drawBorder: false,
          color: null, // this changes
          zeroLineColor: "transparent",
          display: false
        },
        ticks: {
          padding: 20,
          fontColor: null //Font color
        }
      }
    ],
    xAxes: [
      {
        gridLines: {
          drawBorder: false,
          color: null, // Another Color
          zeroLineColor: "transparent",
          display: false
        },
        ticks: {
          display: false
        }
      }
    ]
  }
};

// Passed in the color of the grid lines
export function GetGraphOptions(type, color) {
  var line_color = null;
  let tick = null;
  if (color === "green") {
    line_color = "rgba(0,242,195,0.1)";
    tick ="#9e9e9e";
  } else if (color === "pink") {
    line_color = "rgba(225,78,202,0.1)";
    tick = "#9e9e9e";
  } else{
    line_color = "rgba(29,140,248,0.1)";
    tick = "#9a9a9a";
  }
  var new_options = JSON.parse(JSON.stringify(base_options))
  new_options["scales"]["xAxes"][0]["gridLines"]["color"] = line_color;
  new_options["scales"]["yAxes"][0]["ticks"]["fontColor"] = tick;

  if (type === "line"){
    new_options["scales"]["xAxes"][0]["barPercentage"] = 1.6
    new_options["scales"]["yAxes"][0]["barPercentage"] = 1.6
    new_options["scales"]["yAxes"][0]["gridLines"]["color"] = "rgba(29,140,248,0.0)";
  }
  else if (type === "bar"){
    new_options["scales"]["yAxes"][0]["gridLines"]["color"] = line_color;
  }

  return new_options
}
