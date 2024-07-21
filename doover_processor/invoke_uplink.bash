#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
python3.11 -m pydoover invoke_local_task on_uplink . --agent 732e2a6b-d550-4a95-9681-4721922fac38 --enable-traceback
