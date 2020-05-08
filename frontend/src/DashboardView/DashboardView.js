import React, { Component } from 'react';
import {
    Row,
    Col,
    Button,
    Form,
    FormGroup,
    Input,
} from 'reactstrap';
import Dashboard from '../views/Dashboard'
import './dashboard-view.css';

export default class DashboardView extends Component {
    constructor(props) {
        super(props);

        this.state = {
        }
    }

    render() {
        return (
        <Dashboard></Dashboard>
        );
    }
}
