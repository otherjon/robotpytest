from collections import namedtuple
import wpilib
from rev import CANSparkMax
from rev import CANSparkMaxLowLevel
kBrushless = CANSparkMaxLowLevel.MotorType.kBrushless

# For a real swerve module, we'll also need the CAN ID of the drive motor
SwerveConfig = namedtuple("SwerveConfig", ["steering_can_id", "encoder_dio"])

# Define the maximum steering motor speeds for auto and manual
MAX_AUTO_TURN_SPEED = 0.2
MAX_MANUAL_TURN_SPEED = 0.3

class SwerveModule:
    cfg: SwerveConfig
    
    def setup(self):
        """
        Instantiate instance variables: motors, encoders, etc.
        """
        self.steering_motor = CANSparkMax(self.cfg.steering_can_id, kBrushless)
        self.enc = wpilib.DutyCycleEncoder(self.cfg.encoder_dio)
        self.target_heading = None

    def heading(self):
        """
        Return the steering motor encoder's value (0.0-1.0)
        """
        return self.enc.getAbsolutePosition()


    def set_target_heading(self, heading):
        """
        Set the value of the 'target_heading' instance variable.  If set to
        a valid value (not None)
        """
        if heading is None or (heading >= 0.0 and heading < 1.0):
            self.target_heading = heading
        elif type(heading) in (int, float):
            # Input should be >= 0.0 and < 1.0
            # We use the "% 1" operator to enforce this:
            #   0.2 % 1 == 0.2
            #   4.2 % 1 == 0.2
            #  -0.8 % 1 == 0.2  etc.
            self.target_heading = float(heading) % 1
        else:
            raise ValueError("Invalid target heading: %r" % heading)

    def cancel_target_heading(self):
        self.set_target_heading(None)

    def steer(self, steering_amount):
        """
        Grab the input indicating how much and in which direction the user
        wants to steer.  This will be ignored while we're auto-steering toward
        a target heading, but we'll save the number in any case.
        """
        self.steering_amount = steering_amount

    def execute(self):
        """
        Turn toward target_heading if it has a valid non-None value;
        otherwise do nothing
        """
        wpilib.SmartDashboard.putNumber("heading", int(1000*self.heading()))

        if self.target_heading is None:
            # No auto-steering, just do what the user asked.  Easy.
            self.steering_motor.set(self.steering_amount*MAX_MANUAL_TURN_SPEED)
            return

        curr = self.heading()
        diff = (curr - self.target_heading) % 1  # force range into 0->0.99999
        
        if abs(self.target_heading - curr) < 0.001:
            # We've reached our auto-steering target heading!
            self.steering_motor.set(0)
            self.target_heading = None
            return

        # We have a heading, and we haven't finished turning there yet.
        # Should we turn left (toward -1) or right (toward +1)?
        #   curr=0.6, target=0.4 -> diff=0.2 -> turn left
        #   curr=0.4, target=0.6 -> diff=0.8 -> turn right
        #   curr=0.1, target=0.9 -> diff=0.2 -> turn left
        #   curr=0.9, target=0.1 -> diff=0.8 -> turn right
        # General rule:
        #   If diff < 0.5, turn left; if diff > 0.5, turn right.
        #   (Do either if diff is exactly 0.5)
        #   If diff is close to 0.5, turn quickly.
        #   If diff is far from 0.5 (close to 0.0 or 0.9999), turn slowly.

        if diff <= 0.5:
            self.steering_motor.set(MAX_AUTO_TURN_SPEED*diff)
        else:
            self.steering_motor.set(MAX_AUTO_TURN_SPEED*(1.0-diff))
            
