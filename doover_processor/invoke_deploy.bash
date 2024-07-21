#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
python3.11 -m pydoover invoke_local_task on_deploy . --agent-id 9ebc1e65-dd39-4b82-908d-e2fabee8672d --enable-traceback
