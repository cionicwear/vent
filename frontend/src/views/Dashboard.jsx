import React from 'react';
import { Line, Bar } from "react-chartjs-2";
import { LineChart } from "../ChartsComponents/ChartsWrapper.js"
import { getSensorData } from '../api.js';
import {GetGraphOptions} from "../ChartsComponents/charts_options.jsx"
import {DataWrapper, DoubleDataWrapper} from "../ChartsComponents/charts_data.jsx";

// reactstrap components
import {
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  Row,
  Col,
} from "reactstrap";

const MAX_SAMPLES = 500

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.pressure = {'x': [],  'y': []}
    this.pressureChart = React.createRef();

    this.flow = {'x': [],  'y': []}
    this.flowChart = React.createRef();

    this.volume = {'x': [],  'y': []}
    this.volumeChart = React.createRef();

    this.last = 0

    this.updateChart = this.updateChart.bind(this);

    setInterval(() => {
      this.getSensor()
    }, 100);
  }

  componentDidMount() {
  }

  componentDidUpdate(){
  }

  async getSensor() {
    const resp = await getSensorData(1)
    for (let i=0; i<resp.samples; i++) {
      if (resp.times[i] > this.last) {
        this.flow['x'].push(resp.times[i])
        this.flow['y'].push(resp.humidity[i])
        this.volume['x'].push(resp.times[i])
        this.volume['y'].push(resp.temperature[i])
        this.pressure['x'].push(resp.times[i])
        this.pressure['y'].push(resp.pressure[i])
        if (resp.times[i] > this.last) this.last = resp.times[i]
      }
    }

    // update graphs
    this.updateFlow()
    this.updateVolume()
    this.updatePressure()
  }

  adjustArray(arr, count) {
    for (let i = arr.length; i > count; i--) {
      arr.shift();
    }
  }

  async updateFlow() {
    this.adjustArray(this.flow['x'], MAX_SAMPLES)
    this.adjustArray(this.flow['y'], MAX_SAMPLES)
    this.updateChart(this.flowChart.current.chartInstance, this.flow['x'], this.flow['y'])
  }

  async updateVolume() {
    this.adjustArray(this.volume['x'], MAX_SAMPLES)
    this.adjustArray(this.volume['y'], MAX_SAMPLES)
    this.updateChart(this.volumeChart.current.chartInstance, this.volume['x'], this.volume['y'])
  }

  async updatePressure() {
    this.adjustArray(this.pressure['x'], MAX_SAMPLES)
    this.adjustArray(this.pressure['y'], MAX_SAMPLES)
    this.updateChart(this.pressureChart.current.chartInstance, this.pressure['x'], this.pressure['y'])
  }

  updateChart(chart, label, data) {
    chart.data.labels = label
    chart.data.datasets.forEach((dataset) => {
        dataset.data = data;
    });
    chart.update();
}

  render() {
    return (
        <div className="content">
          <Row>
          <Col xs="7">
            <h3>BW 60kg</h3>
            </Col>
          </Row>
          <Row>
            <Col xs="7">
              <Card className="card-chart">
                <CardHeader>
                  <Row>
                    <Col className="text-left" sm="6">
                      <CardTitle tag="h3">Pressure  </CardTitle>
                    </Col>
                  </Row>
                </CardHeader>
                <CardBody>
                  <div className="chart-area">
                  <CardBody>
                    <div className="chart-area">
                      <Line
                        ref={this.pressureChart}
                        data={DataWrapper(this.pressure['x'], this.pressure['y'])}
                        options={GetGraphOptions("line")}
                      />
                    </div>
                  </CardBody>
                  </div>
                </CardBody>
              </Card>
            </Col>
          </Row>
          <Row>
            <Col xs="7">
              <Card className="card-chart">
                <CardHeader>
                  <h5 className="card-category"></h5>
                  <CardTitle tag="h3">
                    Flow
                  </CardTitle>
                </CardHeader>
                  <CardBody>
                    <div className="chart-area">
                      <Line
                        ref={this.flowChart}
                        data={DataWrapper(this.flow['x'], this.flow['y'], "green")}
                        options={GetGraphOptions("line", this.props.color )}
                      />
                    </div>
                  </CardBody>
              </Card>
            </Col>
          </Row>
          <Row>
            <Col xs="7">
              <Card className="card-chart">
                <CardHeader>
                  <h5 className="card-category"></h5>
                  <CardTitle tag="h3">
                    Volume
                  </CardTitle>
                </CardHeader>
                <CardBody>
                    <div className="chart-area">
                      <Line
                        ref={this.volumeChart}
                        data={DataWrapper(this.volume['x'], this.volume['y'], "pink")}
                        options={GetGraphOptions("line", "pink" )}
                      />
                    </div>
                  </CardBody>
              </Card>
            </Col>
          </Row>
        </div>
    );
  }
}

export default Dashboard;
