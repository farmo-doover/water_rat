#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
python3.11 -m pydoover deploy_config ./doover_config.json --agent-id 6e0af359-add9-4a94-93e3-3b3d43796e12 --enable-traceback