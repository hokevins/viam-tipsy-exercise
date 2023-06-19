"""
Copyright: Copyright (C) 2023 Viam - All Rights Reserved
Product: DevRel
Description: A demonstration of the Viam Python SDK with Tipsy.
"""

import os


# Replace these values with your robot’s own secret and address found in Viam App
ROBOT_SECRET = os.getenv("ROBOT_SECRET") or ""
ROBOT_ADDRESS = os.getenv("ROBOT_ADDRESS") or ""

# Change these values if you named your base or camera differently in robot configuration
BASE_NAME = os.getenv("ROBOT_BASE") or "tipsy-base"
CAMERA_NAME = os.getenv("ROBOT_CAMERA") or "cam"

# Change this value if you'd like to adjust Tipsy's pause interval
# Defaults to 3 seconds
PAUSE_INTERVAL = os.getenv("PAUSE_INTERVAL") or 3

# Change this value if you'd like to adjust the number of Tipsy's ultrasonic sensors
# Defaults to 1 sensor
NUMBER_OF_ULTRASONIC_SENSORS = os.getenv("NUMBER_OF_ULTRASONIC_SENSORS") or 1
