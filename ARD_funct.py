from nanpy import (ArduinoApi, SerialManager, Stepper)
import time
from random import randrange

run =False


#### Pins #######
HeatherTempSensor = 'A1'      #Heater Thermistor PIN
ReactorTempSensor = 'A2'      #Reactor Thermistor PIN
led=13
#################


## CONNECT FUNCTION ##
def ArdConnect(com):
    global run
    run = True
    try:
        #print('Connecting...')
        connection = SerialManager(device=com)
        ard = ArduinoApi(connection=connection)
        print("Device connected")
        return ard
    except:
        run=False
        print("Connection Failed!")
        return 'EMPTY'

## SETUP Arduino FUNCTION ##
def ArdSetup(ard):
    global run
    run = True
    try:
        ard.pinMode(HeatherTempSensor, ard.INPUT)
        ard.pinMode(ReactorTempSensor, ard.INPUT)
        ard.pinMode(led, ard.OUTPUT)
        print('Arduino set')
    except:
        run=False
        print("Setup Failed!")



## 
def ControlStirringMotors(ard,rpm=10,en=True):
    global run
    run = True
    try:
        ard.digitalWrite(led, ard.HIGH)
        time.sleep(rpm)
        ard.digitalWrite(led, ard.LOW)
        time.sleep(rpm)
        ard.digitalWrite(led, ard.HIGH)
        time.sleep(rpm)
        ard.digitalWrite(led, ard.LOW)
        time.sleep(rpm)
        ard.digitalWrite(led, ard.HIGH)
        time.sleep(rpm)
        ard.digitalWrite(led, ard.LOW)
    except:
        run=False
        print("Stirring motors Failed!")


## SET OUTPUTS for Heater
def ControlHeaters(ard,op=0.1,en=True):
    global run
    run = True
    try:
        ard.digitalWrite(led, ard.HIGH)
        time.sleep(op)
        ard.digitalWrite(led, ard.LOW)
        time.sleep(op)
        ard.digitalWrite(led, ard.HIGH)
        time.sleep(op)
        ard.digitalWrite(led, ard.LOW)
    except:
        run=False
        print("Heating Failed!")





## Get Temperature readings from the Reactor
def ReadReactorTemp(ard):
    global run
    run = True
    try:
        s= ard.analogRead(ReactorTempSensor) 
        Sensor = [s]*6
        return Sensor
    except:
        run=False
        print("Temp reading Failed!")

## Get Temperature readings from the Heather
def ReadHeatherTemp(ard):
    global run
    run = True
    try:
        s= ard.analogRead(HeatherTempSensor) 
        Sensor = [s]*6
        return Sensor
    except:
        run=False
        print("Temp reading Failed!")

##def VoltsToCelc():





