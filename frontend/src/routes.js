import React from 'react';
import { Switch, Route, BrowserRouter} from 'react-router-dom';

/* Component Imports */
// import DashboardView from './DashboardView/DashboardView';

// copied from template
import Dashboard from "./views/Dashboard.jsx";

var routes = [
  {
    path: "/workspace",
    name: "Your Workspace",
    icon: "tim-icons icon-chart-pie-36",
    component: Dashboard,
    layout: "/admin"
  }
];

export { routes };

export default () => (
  <BrowserRouter>
    <Switch>
      {/* <Route path="/dashboard" component={DashboardView} /> */}
      {/* this needs to be last */}
      <Route path="*" component={Dashboard} />
    </Switch>
  </BrowserRouter>
);
