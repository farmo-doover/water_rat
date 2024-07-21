#!/bin/bash

# python3.11 -m pydoover get_channel gasflux_connector_recv --agent-id 1da45161-373e-450b-81b6-009bc059693c
TEST_MESSAGE="{'unitID': '6075', 'test': 'yeeha'}"

python3.11 -m pydoover publish gasflux_connector_recv "$TEST_MESSAGE" --agent-id 1da45161-373e-450b-81b6-009bc059693c