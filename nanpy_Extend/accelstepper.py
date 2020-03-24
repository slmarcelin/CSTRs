# this is an extention of the Nanpy package,
# to support the following methods of arduino and AccelStepper library
#   -runSpeed()
#   -SetSpeed(float speed)
#   -stop()
# https://www.airspayce.com/mikem/arduino/AccelStepper/classAccelStepper.html


from nanpy.arduinoboard import ArduinoObject
from nanpy.arduinoboard import arduinomethod, returns, FirmwareClass
from nanpy.arduinoboard import (arduinoobjectmethod, returns)


class AccelStepper(ArduinoObject):

    # Parameters:
    #     interface - Number of pins to interface to.
    #         FUNCTION = 0  Use the functional interface, implementing your own driver
    #         # functions (internal use only)
    #         DRIVER = 1 Stepper Driver, 2 driver pins required
    #         FULL2WIRE=2 2 wire stepper, 2 motor pins required
    #         FULL3WIRE= 3, 3 wire stepper, such as HDD spindle, 3 motor pins required
    #         FULL4WIRE= 4 4 wire full stepper, 4 motor pins required
    #         HALF3WIRE= 6 3 wire half stepper, such as HDD spindle, 3 motor pins required
    #         HALF4WIRE= 8
    #     pin1- Arduino digital pin number for motor pin 1. Defaults to pin 2
    #     pin2- Arduino digital pin number for motor pin 2. Defaults to pin 3.
    #     pin3- Arduino digital pin number for motor pin 3. Defaults to pin 4.
    #     pin4- Arduino digital pin number for motor pin 4. Defaults to pin 5.
    #     enable- If this is true (the default), enableOutputs() will be called to enable the output pins at construction time.
    def __init__(self,
                 interface=4,
                 pin1=2,
                 pin2=3,
                 pin3=4,
                 pin4=5,
                 enable=True,
                 connection=None):
        
		ArduinoObject.__init__(self, connection=connection)
        self.id = self.call('new', interface, pin1, pin2, pin3, pin4)

    # Poll the motor and step it if a step is due, implementing a constant
    # speed as set by the most recent call to setSpeed(). You must call this
    # as frequently as possible, but at least once per step interval.
    #  Returns
    #   true if the motor was stepped.
    @returns(bool)
    @arduinoobjectmethod
    def runSpeed(self):
        pass

    # Sets the desired constant speed for use with runSpeed().
    @arduinoobjectmethod
    def setSpeed(self, speed):
        pass
		
	# Sets the maximum permitted speed.
    @arduinoobjectmethod
    def setMaxSpeed(self, speed):
        pass
		

    # Sets a new target position that causes the stepper to stop as quickly
    # as possible, using the current speed and acceleration parameters.
    @arduinoobjectmethod
    def stop(self):
        pass
