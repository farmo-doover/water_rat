import logging
from datetime import datetime, timezone

from pydoover import ui


def construct_ui():

    ui_elems = (
        ui.AlertStream("significantEvent", "Notify me of any problems"),
        # ui.RemoteComponent("waterRatElement", "Water Rat", component_url="WaterRatElement"),
        ui.NumericVariable("waterRatElement", "Water Rat", component_url="WaterRatElement"),
        ui.BooleanVariable("waterRatStatus", "All Good?"),
        ui.NumericVariable("batteryVoltage", "Battery Voltage (V)",
            dec_precision=1,
            ranges=[
                ui.Range("Low", 2.5, 3.0, ui.Colour.yellow),
                ui.Range("Ok", 3.0, 3.3, ui.Colour.blue),
                ui.Range("Good", 3.3, 3.6, ui.Colour.green),
            ],
        ),
        ui.NumericVariable("signalStrength", "Signal Strength (%)",
            dec_precision=0,
            ranges=[
                ui.Range("Poor", 0, 30, ui.Colour.red),
                ui.Range("Ok", 30, 60, ui.Colour.blue),
                ui.Range("Good", 60, 100, ui.Colour.green),
            ],
        ),
        ui.ConnectionInfo(name="connectionInfo",
            connection_type=ui.ConnectionType.periodic,
            connection_period=(12 * 60*60),
            next_connection=(12 * 60*60),
            offline_after=(24 * 3600),
        )
    )
    return ui_elems
