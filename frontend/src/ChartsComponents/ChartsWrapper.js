import React from 'react';
import { Line, Bar } from "react-chartjs-2";
import {
  CardBody,
} from "reactstrap";

import {GetGraphOptions} from "./charts_options.jsx"
import {DataWrapper, DoubleDataWrapper} from "./charts_data.jsx";

// This should take in data


// Options that can be configured (data,color, size, icon, multiple toggles (todo))

// Classic Line Graph
// Parameters: dataX, dataY, color (blue, green, pink), size (1-12)(n), title(n), (n)ylabel (took out size and labels to work with aneesh better)
class LineChart extends React.Component {
  render() {
    return(
      <CardBody>
        <div className="chart-area">
          <Line
            data={DataWrapper(this.props.dataX, this.props.dataY, this.props.color)}
            options={GetGraphOptions("line", this.props.color )}
          />
        </div>
      </CardBody>
    )
  }
}



// Bar Graph Component
class BarChart extends React.Component {
  render() {

    return(
      <CardBody>
        <div className="chart-area">
          <Bar
            data={DataWrapper(this.props.dataX, this.props.dataY, this.props.color)}
            options={GetGraphOptions("bar", this.props.color )}
          />
        </div>
      </CardBody>

    )
  }
}


class DoubleBarChart extends React.Component {
  render() {

    return(
      <CardBody>
        <div className="chart-area">
          <Bar
            data={DoubleDataWrapper(this.props.dataX, this.props.dataY, this.props.dataCali, this.props.color, this.props.county)}
            options={GetGraphOptions("bar", this.props.color )}
          />
        </div>
      </CardBody>
    )
  }
}



// Pie Chart Component
export {
  LineChart,
  BarChart,
  DoubleBarChart,
}
