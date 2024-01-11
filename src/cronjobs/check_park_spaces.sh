#!/usr/bin/env bash

# Define paths
VENV_PATH="/home/admin/dev/virtualenvs/cronvenv/bin/activate"
SCRIPT_PATH="/home/admin/dev/git_projects/car_parking/src/cronjobs/check_park_spaces_on_pi.py"

# Check if the virtual environment exists
if [ ! -f "$VENV_PATH" ]; then
    echo "Virtual environment not found at $VENV_PATH"
    exit 1
fi
source "$VENV_PATH"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Python script not found at $SCRIPT_PATH"
    exit 1
fi

python "$SCRIPT_PATH"
SCRIPT_EXIT_STATUS=$?

deactivate
exit $SCRIPT_EXIT_STATUS
