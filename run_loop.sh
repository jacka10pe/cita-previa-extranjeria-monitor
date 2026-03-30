#!/bin/bash

# Navigate to your project directory
cd /home/hound/PycharmProjects/cita-previa-extranjeria-monitor

echo "Starting scraper loop. Press [CTRL+C] to stop."

while true
do
    # Execute with env var and poetry
    poetry run python src/main.py

    # 3600 seconds = 1 hour
    sleep 3600
done