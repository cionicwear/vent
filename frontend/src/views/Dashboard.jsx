import React from 'react';
import { randomUniform } from 'd3-random';

import { LineChart } from "../ChartsComponents/ChartsWrapper.js"
import { getSensorData } from '../api.js';

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
    this.state = {
      last: 0,
      pressureX: [],
      pressureY: [],
      flowX: [],
      flowY: [],
      volumeX: [],
      volumeY: []
    };

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

    let flowX = this.state.flowX.slice()
    let flowY = this.state.flowY.slice()

    let volumeX = this.state.volumeX.slice()
    let volumeY = this.state.volumeY.slice()

    let pressureX = this.state.pressureX.slice()
    let pressureY = this.state.pressureY.slice()

    for (let i=0; i<resp.samples; i++) {
      if (resp.times[i] > this.state.last) {
        flowX.push(resp.times[i])
        flowY.push(resp.humidity[i])
        volumeX.push(resp.times[i])
        volumeY.push(resp.temperature[i])
        pressureX.push(resp.times[i])
        pressureY.push(resp.pressure[i])

        if (resp.times[i] > this.state.last) this.setState({ last: resp.times[i] })
      }
    }
    

    // adjust all arr
    this.adjustArray(flowX, MAX_SAMPLES)
    this.adjustArray(flowY, MAX_SAMPLES)
    this.adjustArray(volumeX, MAX_SAMPLES)
    this.adjustArray(volumeY, MAX_SAMPLES)
    this.adjustArray(pressureX, MAX_SAMPLES)
    this.adjustArray(pressureY, MAX_SAMPLES)

    // update state (and graphs)
    this.updateFlow(flowX, flowY)
    this.updateVolume(volumeX, volumeY)
    this.updatePressure(pressureX, pressureY)
  }

  adjustArray(arr, count) {
    for (let i = arr.length; i > count; i--) {
      arr.shift();
    }
  }

  async updateFlow(flowX, flowY) {
    this.setState({ flowX });
    this.setState({ flowY });
  }

  async updateVolume(volumeX, volumeY) {
    this.setState({ volumeX });
    this.setState({ volumeY });
  }

  async updatePressure(pressureX,  pressureY) {
    this.setState({ pressureX });
    this.setState({ pressureY });
  }

  getdata() {
    const x = []
    const y = []
    for (var i = 0; i < 20; i++) {
      const yVal = randomUniform(-50,50)()
      x.push(i)
      y.push(yVal)
    }
    this.setState({
      flowX: x,
      flowY: y,
      pressureX: x,
      pressureY: y,
      volumeX: x,
      volumeY: y
    })
  }

  getd() {
    const yVal = randomUniform(-50,50)()
    var flowX = this.state.flowX.slice();
    flowX.splice(0, 1)
    flowX.push(flowX[flowX.length - 1] + 1)
    this.setState({ flowX });

    var flowY = this.state.flowY.slice();
    flowY.splice(0, 1)
    flowY.push(yVal)
    this.setState({ flowY });
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
                    <LineChart
                      dataX={this.state.pressureX}
                      dataY={this.state.pressureY}
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
                    Flow
                  </CardTitle>
                </CardHeader>
                <LineChart color="green" dataX={this.state.flowX} dataY={this.state.flowY} />
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
                <LineChart color="pink" dataX={this.state.volumeX} dataY={this.state.volumeY}/>
              </Card>
            </Col>
          </Row>
        </div>
    );
  }
}

export default Dashboard;
