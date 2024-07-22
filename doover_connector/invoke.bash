#!/bin/bash

TEST_MESSAGE='{"unitID":"359205101663344","message":{"timestamp":1721622418,"device_name":"WR-3344","farmo_device_type":"water_rat_v2","imei":"359205101663344","frame_count":157,"status":0,"batv":3.45,"gps_lat":-37.2883,"gps_lng":141.9266}}'

python3.11 -m pydoover publish farmo_connector_recv "$TEST_MESSAGE" --agent-id 6e0af359-add9-4a94-93e3-3b3d43796e12