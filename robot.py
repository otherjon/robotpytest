#!/usr/bin/env python3

import wpilib
from magicbot import MagicRobot
from components.swerve_module import SwerveModule, SwerveConfig

JOYSTICK_CHANNEL = 0

class SwerveTestRobot(MagicRobot):
    # Define components (and their configurations) here
    #
    swerve_1: SwerveModule
    swerve_1_cfg = SwerveConfig(steering_can_id=5, encoder_dio=1)

    # You can even pass constants to components

    def createObjects(self):
        """Initialize all wpilib motors & sensors"""
        self.joystick = wpilib.XboxController(JOYSTICK_CHANNEL)

    # No autonomous routine boilerplate required here, anything in the
    # autonomous folder will automatically get added to a list

    def teleopPeriodic(self):
        """Place code here that does things as a result of operator
        actions"""

        try:
            if self.joystick.getAButton():
                self.swerve_1.set_target_heading(0)
            else:
                turn_amt = self.joystick.getRightX()
                self.swerve_1.steer(turn_amt)
        except:
            self.onException()


if __name__ == "__main__":
    wpilib.run(SwerveTestRobot)
