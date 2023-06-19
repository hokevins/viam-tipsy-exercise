"""
Copyright: Copyright (C) 2023 Viam - All Rights Reserved
Product: DevRel
Description: A demonstration of the Viam Python SDK with Tipsy.
"""

from viam.components.sensor import Sensor
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions

from utils.constants import ROBOT_ADDRESS, ROBOT_SECRET, NUMBER_OF_ULTRASONIC_SENSORS


async def connect():
    """Connect to Tipsy and return robot instance"""
    credentials = Credentials(type="robot-location-secret", payload=ROBOT_SECRET)
    dial_options = DialOptions(credentials=credentials)
    opts = RobotClient.Options(refresh_interval=0, dial_options=dial_options)
    return await RobotClient.at_address(ROBOT_ADDRESS, opts)

async def detect_obstacle_distance(sensor):
    """Get reading from an ultrasonic sensor and return distance in meters"""
    return await sensor.get_readings()["distance"]

async def detect_obstacles_greater_than(sensors, threshold=0.4):
    """Calculate if readings from a series of ultrasonic sensors are greater than a threshold in meters and return as a boolean"""
    for sensor in sensors:
        distance = await detect_obstacle_distance(sensor)
        if distance > threshold:
            # Returns True if just one reading is greater
            return True
    return False

async def detect_obstacles_less_than(sensors, threshold=0.4):
    """Calculate if readings from a series of ultrasonic sensors are less than a threshold in meters and return as a boolean"""
    for sensor in sensors:
        distance = await detect_obstacle_distance(sensor)
        if distance < threshold:
            # Returns True if just one reading is less
            return True
    return False

def initialize_sensors(robot):
    """Initialize all ultrasonic sensors and return as a list of sensors"""
    sensors = []
    for n in range(1, NUMBER_OF_ULTRASONIC_SENSORS + 1)
        sensors.append(Sensor.from_robot(robot, f"ultrasonic{n}"))
    return sensors