"""
Copyright: Copyright (C) 2023 Viam - All Rights Reserved
Product: DevRel
Description: A demonstration of the Viam Python SDK with Tipsy.
"""

import asyncio
import random
from datetime import datetime

from viam.components.base import Base
from viam.components.movement_sensor import MovementSensor
from viam.services.vision import VisionClient

from utils.constants import BASE_NAME, CAMERA_NAME, PAUSE_INTERVAL, BaseState, Label
from utils.lib import connect, detect_obstacles_greater_than, detect_obstacles_less_than, initialize_ultrasonic_sensors


BASE_STATE = BaseState.STOPPED
TIME_LAST_STOPPED = datetime.now()

async def obstacle_detect_loop(base, *sensors):
    """Obstacle detection loop"""
    while True:
        checked_obstacles_distance = await detect_obstacles_less_than(sensors, threshold=0.6)
        # If an obstacle is less than 0.6m away and currently moving forward, stop Tipsy
        if checked_obstacles_distance and BASE_STATE == BaseState.FORWARD:
            await base.stop()
            print("Obstacle detected. Awaiting...")

        await asyncio.sleep(0.01)

async def person_detect_loop(base, detector, *sensors):
    """Person detection loop"""
    while True:
        found_person = False
        global BASE_STATE
        global TIME_LAST_STOPPED
        print("Detecting person...")
        detections = await detector.get_detections_from_camera(CAMERA_NAME)
        for d in detections:
            if d.confidence > 0.7:
                # Matching a 0.7 confidence of the assigned labels from labels.txt
                detected_object = d.class_name
                # Check specifically for detections with the label `Person` and not every object in the `labels.txt` file
                if detected_object != Label.PERSON:
                    print(f"{detected_object} detected. Not a person.")
                else:
                    found_person = True

        if found_person:
            # Goes toward person as long as there are no obstacles in front
            print("Person detected! Maybe they'd like a drink?")
            # First check for obstacles, and don't start moving if obstacle detected
            checked_person_distance = await detect_obstacles_greater_than(sensors, threshold=0.6)
            # If a person is more than 0.6m away, start Tipsy
            if checked_person_distance:
                print("Tipsy moving forward.")
                BASE_STATE = BaseState.FORWARD
                # To move towards a person, Tipsy will always move forward 800mm at 250mm/s
                await base.move_straight(distance=800, velocity=250)
                BASE_STATE = BaseState.STOPPED
                TIME_LAST_STOPPED = datetime.now()
        else:
            print("Tipsy spinning.")
            BASE_STATE = BaseState.SPINNING
            # To find a person, Tipsy will always spin randomly at 45deg/s
            await base.spin(random.randrange(360), 45)
            BASE_STATE = BaseState.STOPPED
            TIME_LAST_STOPPED = datetime.now()

        await asyncio.sleep(PAUSE_INTERVAL)

async def stopped_detect_loop(base):
    """Stopped tracker loop for mingle mechanism"""
    while True:
        global BASE_STATE
        global TIME_LAST_STOPPED
        elapsed_time = (datetime.now() - TIME_LAST_STOPPED).total_seconds()
        # Spin Tipsy randomly if it's been longer than 30s since base was last stopped
        if elapsed_time > 30:
            print(f"It's been {elapsed_time} seconds since Tipsy last moved. Tipsy spinning.")
            BASE_STATE = BaseState.SPINNING
            await base.spin(random.randrange(360), 45)
            BASE_STATE = BaseState.STOPPED
            TIME_LAST_STOPPED = datetime.now()

        await asyncio.sleep(0.01)

async def orientation_detect_loop(base, sensor):
    """Orientation detection loop"""
    while True:
        global BASE_STATE
        global TIME_LAST_STOPPED
        orientation = await sensor.get_orientation() # Get the current orientation vector
        # If Tipsy is tipping backwards in the event of a collision, self-heal by moving backward and turning around
        if orientation is not level:
            # TODO: Fix pseudocode above with known API to calculate orientation
            # Docs: https://docs.viam.com/components/movement-sensor/#getorientation
            print(f"Collision possibly detected. Tipsy moving backward and turning around.")
            BASE_STATE = BaseState.BACKWARD
            await base.move_straight(distance=-800, velocity=100)
            BASE_STATE = BaseState.SPINNING
            await base.spin(180, 45)
            BASE_STATE = BaseState.STOPPED
            TIME_LAST_STOPPED = datetime.now()

        await asyncio.sleep(0.01)

async def main():
    """Main Tipsy runner"""

    # Initialize robot, base, ultrasonic sensor(s), and detector
    robot = await connect()
    base = Base.from_robot(robot, BASE_NAME)
    detector = VisionClient.from_robot(robot, "person_detector")
    movement_sensor = MovementSensor.from_robot(robot, "movement_sensor")
    ultrasonic_sensors = initialize_ultrasonic_sensors(robot)

    # Create background tasks running asynchronously:

    # Background task that looks for obstacles and stops Tipsy if its moving
    obstacle_task = asyncio.create_task(obstacle_detect_loop(base, *ultrasonic_sensors))
    # Background task that looks for a person and moves Tipsy towards them, or turns and keeps looking
    person_task = asyncio.create_task(person_detect_loop(base, detector, *ultrasonic_sensors))
    # Background task that tracks how long it's been since base was last stopped
    spin_task = asyncio.create_task(stopped_detect_loop(base))
    # Background task that monitors orientation in the event of a collision
    orientation_task = asyncio.create_task(orientation_detect_loop(base, movement_sensor))

    results = await asyncio.gather(obstacle_task, person_task, spin_task, orientation_task, return_exceptions=True)
    print(results)

    # Disconnect from Tipsy
    await robot.close()

    """
    TODOs:
    - Split into classes?
    - make a helper spinning method, make a helper going forward method, make a helper going backward method
    - write tests or numpy docstrings for Sphinx generated docs?
    - read Viam tutorial docs and Python asyncio docs
    """

if __name__ == "__main__":
    asyncio.run(main())
