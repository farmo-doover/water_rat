#!/bin/bash

TEST_MESSAGE="{'unitID': '6075', 'test': 'yeeha'}"

python3.11 -m pydoover publish farmo_connector_recv "$TEST_MESSAGE" --agent-id 6e0af359-add9-4a94-93e3-3b3d43796e12