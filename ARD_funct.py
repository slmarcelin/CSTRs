from nanpy import (ArduinoApi, SerialManager, Stepper)
import time
from random import randrange


global run
run =False

#### Pins
sensorPin = 14                     # Pot on A0 - Analog input
led=13
##########



# change this to the number of steps on your motor
STEPS = 100


def ArdConnect(com):
    try:
        #print('Connecting...')
        connection = SerialManager(device=com)
        ard = ArduinoApi(connection=connection)
        run=True
        print("Device connected")
        return ard
    except:
        run=False
        print("Connection Failed!")
        return 'EMPTY'
def ArdSetup(ard):
    global run
    try:
        ard.pinMode(12, ard.INPUT)
        ard.pinMode(led, ard.OUTPUT)
        run=True
        print('Arduino set')
    except:
        run=False
        #print("Connection Failed!")
def UpdateOutputs(ard):
    global run
    try:
        #print('LED: ',ard.digitalRead(led))
        if ard.digitalRead(led) == 0:
            ard.digitalWrite(led, ard.HIGH)
        else:
            ard.digitalWrite(led, ard.LOW)
        run=True
    except:
        run=False
        #print("Connection Failed!")
def GetTemperatures(ard):
    try:
        Sensor = []
        
        Sensor.append( ard.analogRead(15) )
        Sensor.append(Sensor[0] )
        Sensor.append(Sensor[0] )
        Sensor.append(Sensor[0] )
        Sensor.append(Sensor[0] )
        Sensor.append(Sensor[0] )


        run=True
        return Sensor
    except:
        run=False
        return -1
        #print("Connection Failed!")

