"""
Copyright: Copyright (C) 2023 Kevin Ho | Viam - All Rights Reserved
Product: DevRel
Description: A demonstration of the Viam Python SDK with Tipsy.
"""

import asyncio
from datetime import datetime

from viam.components.base import Base
from viam.components.movement_sensor import MovementSensor
from viam.services.vision import VisionClient

from robot_interface import RobotInterface
from utils.constants import BASE_NAME, CAMERA_NAME, ML_CONFIDENCE_THRESHOLD, PAUSE_INTERVAL, BaseState, Label
from utils.lib import connect, detect_obstacles, initialize_ultrasonic_sensors


async def obstacle_detect_loop(robot_interface, *sensors):
    """Obstacle detection loop"""
    while True:
        checked_obstacles_distance = await detect_obstacles(sensors, compare_operator="less", threshold=0.6)
        # If any obstacle is less than 0.6m away and Tipsy is currently moving forward, then stop moving
        if checked_obstacles_distance and robot_interface.BASE_STATE == BaseState.FORWARD:
            print("Obstacle detected. Awaiting...")
            await robot_interface.stop()

        await asyncio.sleep(0.01)

async def orientation_detect_loop(robot_interface, sensor):
    """Orientation detection loop"""
    while True:
        orientation = await sensor.get_orientation() # Get the current orientation vector
        # If Tipsy is tipping backwards in the event of a collision, then self-heal by moving backward and turning around
        if orientation is not level:
            # TODO: Fix pseudocode above with correct API usage to calculate orientation
            # Unclear how to achieve this from the [docs](https://docs.viam.com/components/movement-sensor/#getorientation)
            print("Collision possibly detected.")
            await robot_interface.move_backward_and_turn_around()

        await asyncio.sleep(0.01)

async def person_detect_loop(robot_interface, detector, *sensors):
    """Person detection loop"""
    while True:
        found_person = False
        print("Detecting person...")
        detections = await detector.get_detections_from_camera(CAMERA_NAME)
        for d in detections:
            if d.confidence > float(ML_CONFIDENCE_THRESHOLD):
                detected_object = d.class_name
                if detected_object != Label.PERSON:
                    print(f"{detected_object} detected. Not a person.")
                else:
                    found_person = True

        if found_person:
            print("Person detected! Maybe they'd like a drink?")
            checked_person_distance = await detect_obstacles(sensors, compare_operator="greater", threshold=0.6)
            # If any person is more than 0.6m away, then start moving
            if checked_person_distance:
                await robot_interface.move_forward()
        else:
            await robot_interface.spin_randomly()

        await asyncio.sleep(float(PAUSE_INTERVAL))

async def stopped_detect_loop(robot_interface):
    """Stopped tracker loop for mingle mechanism"""
    while True:
        elapsed_time = (datetime.now() - TIME_LAST_STOPPED).total_seconds()
        # If it's been longer than 30s since Tipsy last moved, then spin randomly
        if elapsed_time > 30:
            print(f"It's been {elapsed_time} seconds since Tipsy last moved.")
            await robot_interface.spin_randomly()

        await asyncio.sleep(0.01)

async def main():
    """Main coroutine that creates and runs several subtasks in parallel"""

    robot = await connect()
    base = Base.from_robot(robot, BASE_NAME)
    detector = VisionClient.from_robot(robot, "person_detector")
    movement_sensor = MovementSensor.from_robot(robot, "movement_sensor")
    ultrasonic_sensors = initialize_ultrasonic_sensors(robot)

    robot_interface = RobotInterface(base)

    # Schedule coroutines to run asynchronously
    tasks = [
        # Background task that looks for obstacles
        asyncio.create_task(obstacle_detect_loop(robot_interface, *ultrasonic_sensors)),
        # Background task that monitors orientation
        asyncio.create_task(orientation_detect_loop(robot_interface, movement_sensor)),
        # Background task that looks for a person
        asyncio.create_task(person_detect_loop(robot_interface, detector, *ultrasonic_sensors)),
        # Background task that tracks how long it's been since base was last stopped
        asyncio.create_task(stopped_detect_loop(robot_interface))
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(results)

    await robot.close()

if __name__ == "__main__":
    asyncio.run(main())
