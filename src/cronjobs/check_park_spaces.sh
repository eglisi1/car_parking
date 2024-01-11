#!/bin/bash
source /home/admin/cronlogs/env_vars.sh
source /home/admin/dev/virtualenvs/cronvenv/bin/activate
python /home/admin/dev/git_projects/car_parking/src/cronjobs/check_park_spaces_on_pi.py
deactivate
