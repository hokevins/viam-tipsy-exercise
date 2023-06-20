"""
Copyright: Copyright (C) 2023 Kevin Ho | Viam - All Rights Reserved
Product: DevRel
Description: A demonstration of the Viam Python SDK with Tipsy.
"""

import random
from datetime import datetime

from utils.constants import BaseState


class RobotInterface:
    """Robot interface for Tipsy's internal state and locomotion controls"""

    def __init__(self, base):
        self.base = base
        # Robot state:
        self.BASE_STATE = BaseState.STOPPED
        self.TIME_LAST_STOPPED = datetime.now()

    async def move_backward_and_turn_around(self):
        """Locomotion method to move Tipsy"""
        print("Tipsy moving backward and turning around.")
        self.BASE_STATE = BaseState.BACKWARD
        await self.base.move_straight(distance=-800, velocity=100)
        self.BASE_STATE = BaseState.SPINNING
        await self.base.spin(180, 45)
        self.BASE_STATE = BaseState.STOPPED
        self.TIME_LAST_STOPPED = datetime.now()

    async def move_forward(self):
        """Locomotion method to move Tipsy"""
        print("Tipsy moving forward.")
        self.BASE_STATE = BaseState.FORWARD
        await self.base.move_straight(distance=800, velocity=250)
        self.BASE_STATE = BaseState.STOPPED
        self.TIME_LAST_STOPPED = datetime.now()

    async def spin_randomly(self):
        """Locomotion method to move Tipsy"""
        print("Tipsy spinning.")
        self.BASE_STATE = BaseState.SPINNING
        await self.base.spin(random.randrange(360), 45)
        self.BASE_STATE = BaseState.STOPPED
        self.TIME_LAST_STOPPED = datetime.now()

    async def stop(self):
        """Locomotion method to stop Tipsy"""
        print("Tipsy stopping.")
        # Intentionally do not update `TIME_LAST_STOPPED`
        await self.base.stop())
