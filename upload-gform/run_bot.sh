#!/bin/bash

# Activate Python virtual environment
source venv/bin/activate

# Run the bot (pass all arguments to the python script)
python3 code.py "$@"
