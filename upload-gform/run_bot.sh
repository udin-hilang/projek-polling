#!/bin/bash

# Dynamically determine the project root directory
PROJECT_ROOT=$(dirname "$(readlink -f "$0")")

# Activate Python virtual environment using absolute path
source "$PROJECT_ROOT/venv/bin/activate"

# Run the bot using absolute path to the python script
python3 "$PROJECT_ROOT/code.py" "$@"
