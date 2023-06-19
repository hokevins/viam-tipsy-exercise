"""
NOTE: Uses pre-trained ML packages. To use the provided Machine Learning model, copy the effdet0.tflite file and the labels.txt to the Raspberry Pi on Tipsy.
"""

import asyncio
import os

from viam.components.base import Base
from viam.components.sensor import Sensor
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionClient

# Replace these values with your robot’s own secret and address found in Viam App
ROBOT_SECRET = os.getenv("ROBOT_SECRET") or ""
ROBOT_ADDRESS = os.getenv("ROBOT_ADDRESS") or ""

# Change these values if you named your base or camera differently in robot configuration
BASE_NAME = os.getenv("ROBOT_BASE") or "tipsy-base"
CAMERA_NAME = os.getenv("ROBOT_CAMERA") or "cam"

PAUSE_INTERVAL = os.getenv("PAUSE_INTERVAL") or 3

# TODO: refactor base_state into a DataClass?
base_state = "stopped"

async def connect():
    """Connect to Tipsy"""
    credentials = Credentials(type="robot-location-secret", payload=ROBOT_SECRET)
    dial_options = DialOptions(credentials=credentials)
    opts = RobotClient.Options(refresh_interval=0, dial_options=dial_options)
    return await RobotClient.at_address(robot_address, opts)

async def obstacle_detect(sensor):
    """Gets readings from an ultrasonic sensor and returns distance in meters"""
    return await sensor.get_readings()["distance"]

async def obstacle_detect_loop(sensor, base):
    """Asynchronously loops through the readings to stop the base if it’s closer than a certain distance from an obstacle"""
    while(True):
        reading = await obstacle_detect(sensor)
        # If an obstacle is less than 0.4m away and moving straight, stop Tipsy
        if reading < 0.4 and base_state == "straight":
            await base.stop()
            print("Obstacle detected. Awaiting...")
        await asyncio.sleep(.01)

async def person_detect(detector, sensor, base):
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
            # First manually call `obstacle_detect` so don't start moving if obstacle detected
            distance = await obstacle_detect(sensor)
            # If an obstacle is more than 0.4m away, start Tipsy
            if distance > 0.4:
                print("Tipsy moving straight.")
                base_state = "straight"
                # To move towards a person, Tipsy will always move forward 800mm at 800mm/s
                await base.move_straight(distance=800, velocity=250)
                base_state = "stopped"
        else:
            print("Tipsy spinning.")
            base_state = "spinning"
            # To find a person, Tipsy will always spin at 45deg at 45deg/s
            await base.spin(45, 45)
            base_state = "stopped"

        await asyncio.sleep(PAUSE_INTERVAL)

async def main():
    """Main Tipsy runner"""

    # Connect to Tipsy, initialize the base, ultrasonic sensor, and detector
    robot = await connect()
    base = Base.from_robot(robot, BASE_NAME)
    sensor = Sensor.from_robot(robot, "ultrasonic")
    detector = VisionClient.from_robot(robot, "myPeopleDetector")

    # Create two background tasks running asynchronously:

    # Background task that looks for obstacles and stops Tipsy if its moving
    obstacle_task = asyncio.create_task(obstacle_detect_loop(sensor, base))
    # Background task that looks for a person and moves Tipsy towards them, or turns and keeps looking
    person_task = asyncio.create_task(person_detect(detector, sensor, base))

    results = await asyncio.gather(obstacle_task, person_task, return_exceptions=True)
    print(results)

    # Disconnect from Tipsy
    await robot.close()

    """
    TODO:
    - if person is extremely close, stop Tipsy
    - Stay for x time for people to pick up drinks
    - if person gives a thumbs up, tipsy will turn randomly and look for other people
    - if Tipsy is stopped for too long it will turn randomly
    - maybe Tipsy can look for a paddle like at an auction to hail down the waiter?
    - maybe voice recognition to have tipsy be summoned?  how to triangulate voice and location though...
    - maybe voice reocgnition to say thank you tipsy instead of thumbs up in camera
    - "Not get “stuck” next to the same person, mingle! (but don’t over-engineer it, randomness is OK, no need to track individual people or where Tipsy has been)"
    - research Roomba's algo for this?
    - "How might you deal with Tipsy running into an object and starting to tip backwards (perhaps if the object was not in the field of detection for the ultrasonic sensor)" - IMU sensor (inertial measurement unit) to detect orientation and go backwards if so until flat again
    """

if __name__ == "__main__":
    asyncio.run(main())
