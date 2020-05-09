export function DataWrapper(dataX, dataY, color) {
  let line_color = null;
  let border_color = null;
  if (color === "green") {
    line_color = "rgba(0,242,195";
    border_color = "#00d6b4"
  } else if (color === "pink") {
    line_color = "rgba(225,78,202";
    border_color = "#d048b6"
  } else{
    line_color = "rgba(29,140,248";
    border_color = "#1f8ef1"
  }


  let data_fn =  canvas => {
    let ctx = canvas.getContext("2d");

    let gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
      gradientStroke.addColorStop(1, line_color + ",0.2)"); // this changes
      gradientStroke.addColorStop(0.4, line_color + ",0.0)"); // this changes
      gradientStroke.addColorStop(0, line_color + ",0)"); //this changes

    return {
      labels: dataX,
      datasets: [
        {
          borderColor: border_color,
          pointRadius: 1,
          lineTension: 0,
          data: dataY,
          fill: false,
          // showLine: false,
          minRotation: 10,
          maxRotation: 10
        }
      ]
    };
  }

  return data_fn
}




export function DoubleDataWrapper(dataX, dataY, dataCali, color, county) {
  let line_color = null;
  let border_color = null;
  if (color === "green") {
    line_color = "rgba(0,242,195";
    border_color = "#00d6b4"
  } else if (color === "pink") {
    line_color = "rgba(225,78,202";
    border_color = "#d048b6"
  } else{
    line_color = "rgba(29,140,248";
    border_color = "#1f8ef1"
  }


  let data_fn =  canvas => {
    let ctx = canvas.getContext("2d");

    let gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
      gradientStroke.addColorStop(1, line_color + ",0.2)"); // this changes
      gradientStroke.addColorStop(0.4, line_color + ",0.0)"); // this changes
      gradientStroke.addColorStop(0, line_color + ",0)"); //this changes

    let gradientStrokeCali = ctx.createLinearGradient(0, 230, 0, 50);
      gradientStroke.addColorStop(1, "rgba(255,255,0,0.2)"); // this changes
      gradientStroke.addColorStop(0.4, "rgba(255,255,0,0.0)"); // this changes
      gradientStroke.addColorStop(0, "rgba(255,255,0,0)"); //this changes

    return {
      labels: dataX,
      datasets: [
        {
          label: county,
          fill: true,
          backgroundColor: gradientStrokeCali,
          borderColor: border_color,
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          data: dataY
        },
        {
          label: "California",
          fill: true,
          backgroundColor: gradientStrokeCali,
          borderColor: "#FFFF00",
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          data: dataCali
        },
      ]
    };
  }

  return data_fn
}
