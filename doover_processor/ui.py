import logging
from datetime import datetime, timezone

from pydoover import ui


def construct_ui():

    ui_elems = (
        ui.AlertStream("significantEvents", "Notify me of any problems"),
        ui.RemoteComponent("waterRatElement", "Water Rat", component_url="WaterRatElement"),
        ui.NumericVariable("waterRatAngle", "Angle (°)",
            dec_precision=0,
            form=ui.Widget.radial,
            ranges=[
                ui.Range("Ok", 0, 30, ui.Colour.green),
                ui.Range("Not Good", 30, 90, ui.Colour.yellow),
            ],
        ),
        ui.NumericVariable("batteryVoltage", "Battery Voltage (V)",
            dec_precision=1,
            ranges=[
                ui.Range("Low", 5.2, 5.8, ui.Colour.yellow),
                ui.Range("Ok", 5.8, 6.4, ui.Colour.blue),
                ui.Range("Charging", 6.4, 7.0, ui.Colour.green),
                ui.Range("High", 7.0, 7.2, ui.Colour.red),
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
