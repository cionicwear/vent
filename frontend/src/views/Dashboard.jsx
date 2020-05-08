import React from 'react';
import { randomUniform } from 'd3-random';

import config from '../config';
import {LineChart} from "../ChartsComponents/ChartsWrapper.js"
import { getYearlyCountyRecidivism, createCrimeRateGraphData, getCountyRecidivismByType } from '../helpers';

// reactstrap components
import {
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  Row,
  Col,
} from "reactstrap";

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      pressureX: [],
      pressureY: [],
      flowX: [],
      flowY: [],
      volumeX: [],
      volumeY: []
    };

    setInterval(() => {
      this.getd()
    }, 500);
  }

  componentDidMount() {
    this.getdata()
  }

  componentDidUpdate(){
  }

  async getFlow() {
    // var rates  = await createCrimeRateGraphData(counties)
    var rates  = [0,1,2]
    const flowX = rates[0]
    const flowY = rates[1]
    this.setState({
      flowX,
      flowY
    });
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
          <Col lg="7">
            <h3>BW 60kg</h3>
            </Col>
          </Row>
          <Row>
            <Col lg="7">
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
            <Col lg="7">
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
            <Col lg="7">
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
