import React from "react";
import { render } from "react-dom";
import Main from "./react-app/Main.js";
import { MuiThemeProvider, createMuiTheme } from "material-ui/styles";
import Reboot from "material-ui/Reboot";
import { grey, amber, red, white } from "material-ui/colors";

const page_style = {
  padding: 8 * 2,
  backgroundColor: "rgb(36, 36, 36)",
  minHeight: 8 * 40,
  width: "100%",
  height: "100%"
};

const theme = createMuiTheme({
  palette: {
    primary: white,
    accent: amber,
    error: red,
    type: "dark"
  }
});

const gmapsProps = {
  googleMapURL:
    "https://maps.googleapis.com/maps/api/js?key=AIzaSyB6nEb3w16YN08QthPbwgkxsQVlGc4rYIU&v=3.exp&libraries=geometry,drawing,places",
  loadingElement: <div style={{ height: `100%` }} />,
  containerElement: <div style={{ height: `400px` }} />
};

function App() {
  return (
    <div>
      <Reboot />
      <MuiThemeProvider theme={theme}>
        <div style={page_style}>
          <Main gmapsProps={gmapsProps} />
        </div>
      </MuiThemeProvider>
    </div>
  );
}
render(<App />, document.querySelector("#app"));
