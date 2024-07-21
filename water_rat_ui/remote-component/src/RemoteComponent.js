import RemoteAccess from 'doover_home/RemoteAccess'
import { ThemeProvider } from '@mui/material/styles';
import React, {useState, useEffect, Component} from 'react'
import { Paper, Grid, Box, Card, Button } from '@mui/material'

import SvgComponent from './WaterRatSVG';
import { maxWidth } from '@mui/system';

class RotatingSVG extends Component {
    constructor(props) {
      super(props);
      this.state = {
        rotation: props.rotation || 0, // Default to 0 if no rotation prop is provided
      };
    }
  
    render() {
      const { rotation } = this.state;
  
      const svgStyle = {
        transform: `rotate(${rotation}deg)`,
        transformOrigin: 'center center',
      };
  
      return (
        <div alt="Rotating SVG" style={svgStyle}>
          <SvgComponent/>
        </div>
      );
    }
  }
 
export default class RemoteComponent extends RemoteAccess{
    constructor(props){
        super(props)
        this.state = {
            pending_update : {},
            agent_id: this.getUi().agent_key
        }
    }


    render() {

        let rotation = 20;

        let message = "All is good";
        let message_colour = "green";

        if (rotation >= 30){
            message = "Houston,\nWe have a problem";
            message_colour = "red";
        }

        return (
            // Create a div that fills horizontally and dive into 2 separate divs
            
            <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', overflow: 'hidden'}}>
                <div style={{ maxWidth: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <RotatingSVG rotation={rotation} /> {/* Rotates the SVG by 45 degrees */}
                </div>
                <div style={{ width: '50%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                    <h1 style={{ margin: 'auto' }}>{rotation}°</h1>
                    <h2 style={{ marginLeft: '20px', marginRight: '20px', color: message_colour, whiteSpace: 'pre-wrap', textAlign: 'center' }}>{message}</h2>
                </div>
            </div>
        );

    }
}
