"""
Copyright: Copyright (C) 2023 Kevin Ho | Viam - All Rights Reserved
Product: DevRel
Description: A demonstration of the Viam Python SDK with Tipsy.
"""

import os


# Replace these values with your robot’s own secret and address found in Viam App
ROBOT_SECRET = os.getenv("ROBOT_SECRET") or ""
ROBOT_ADDRESS = os.getenv("ROBOT_ADDRESS") or ""

# Change these values if you named your base or camera differently in robot configuration
BASE_NAME = os.getenv("ROBOT_BASE") or "tipsy-base"
CAMERA_NAME = os.getenv("ROBOT_CAMERA") or "tipsy-camera"

# Change this value if you'd like to adjust the minimum ML confidence score of the assigned labels from `labels.txt`
ML_CONFIDENCE_THRESHOLD = os.getenv("ML_CONFIDENCE_THRESHOLD") or 0.7

# Change this value if you'd like to adjust the number of Tipsy's ultrasonic sensors
NUMBER_OF_ULTRASONIC_SENSORS = os.getenv("NUMBER_OF_ULTRASONIC_SENSORS") or 1

# Change this value if you'd like to adjust Tipsy's pause interval
PAUSE_INTERVAL = os.getenv("PAUSE_INTERVAL") or 3

class BaseState:
    """Dataclass to represent the states of Tipsy's base"""
    BACKWARD = "backward"
    FORWARD = "forward"
    SPINNING = "spinning"
    STOPPED = "stopped"

class Label:
    """Dataclass to represent the assigned labels of the ML model"""
    PERSON = "Person"
