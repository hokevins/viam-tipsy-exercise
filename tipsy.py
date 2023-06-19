"""
Copyright: Copyright (C) 2023 Viam - All Rights Reserved
Product: DevRel
Description: A demonstration of the Viam Python SDK with Tipsy.
"""

import asyncio
import random

from viam.components.base import Base
from viam.services.vision import VisionClient

from utils.constants import BASE_NAME, CAMERA_NAME, PAUSE_INTERVAL
from utils.lib import connect, detect_obstacles_greater_than, detect_obstacles_less_than, initialize_sensors


base_state = "stopped"

async def obstacle_detect_loop(base, *sensors):
    """Obstacle detection loop"""
    while(True):
        # If an obstacle is less than 0.6m away and currently moving straight, stop Tipsy
        checked_obstacles_distance = await detect_obstacles_less_than(sensors, threshold=0.6)
        if checked_obstacles_distance and base_state == "straight":
            await base.stop()
            print("Obstacle detected. Awaiting...")
        await asyncio.sleep(.01)

async def person_detect_loop(base, detector, *sensors):
    """Person detection loop"""
    while(True):
        found_person = False
        global base_state
        print("Detecting person...")
        detections = await detector.get_detections_from_camera(CAMERA_NAME)
        for d in detections:
            if d.confidence > 0.7:
                # Matching a 0.7 confidence of the assigned labels from labels.txt
                detected_object = d.class_name
                # Check specifically for detections with the label `Person` and not every object in the `labels.txt` file
                if detected_object != "Person":
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
                print("Tipsy moving straight.")
                base_state = "straight"
                # To move towards a person, Tipsy will always move forward 800mm at 800mm/s
                await base.move_straight(distance=800, velocity=250)
                base_state = "stopped"
        else:
            print("Tipsy spinning.")
            base_state = "spinning"
            # To find a person, Tipsy will always randomly spin at 45deg/s
            await base.spin(random.randrange(360), 45)
            base_state = "stopped"

        await asyncio.sleep(PAUSE_INTERVAL)

async def main():
    """Main Tipsy runner"""

    # Initialize robot, base, ultrasonic sensor(s), and detector
    robot = await connect()
    base = Base.from_robot(robot, BASE_NAME)
    sensors = initialize_sensors(robot)
    detector = VisionClient.from_robot(robot, "myPeopleDetector")

    # Create two background tasks running asynchronously:

    # Background task that looks for obstacles and stops Tipsy if its moving
    obstacle_task = asyncio.create_task(obstacle_detect_loop(base, *sensors))
    # Background task that looks for a person and moves Tipsy towards them, or turns and keeps looking
    person_task = asyncio.create_task(person_detect_loop(base, detector, *sensors))

    results = await asyncio.gather(obstacle_task, person_task, return_exceptions=True)
    print(results)

    # Disconnect from Tipsy
    await robot.close()

    """
    TODO:
    - Split into classes?
    - if person is extremely close, stop Tipsy
    - Stay for x time for people to pick up drinks
    - if Tipsy is stopped for too long it will turn randomly by X degrees
    - write tests or numpy docs?
    - refactor `base_state` into a DataClass?
    - read Viam tutorial docs and Python asyncio docs
    """

if __name__ == "__main__":
    asyncio.run(main())
