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
## SETUP Arduino FUNCTION ##
def ArdSetup(ard):
    global run
    try:
        ard.pinMode(HeatherTempSensor, ard.INPUT)
        ard.pinMode(ReactorTempSensor, ard.INPUT)
        ard.pinMode(led, ard.OUTPUT)
        run=True
        print('Arduino set')

    except:
        run=False
        #print("Setup Failed!")


## 
def MoveStirrMotors(ard,rpm=10,en=True):
    global run
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
        run=True

    except:
        run=False
        #print("Stirring motors Failed!")

## 
def Heat(ard,op=0,en=True):
    global run
    try:
        ard.digitalWrite(led, ard.HIGH)
        time.sleep(op)
        ard.digitalWrite(led, ard.LOW)
        time.sleep(op)
        ard.digitalWrite(led, ard.HIGH)
        time.sleep(op)
        ard.digitalWrite(led, ard.LOW)
        time.sleep(op)
        ard.digitalWrite(led, ard.HIGH)
        time.sleep(op)
        ard.digitalWrite(led, ard.LOW)
        run=True

    except:
        run=False
        #print("Heating Failed!")


## Get Temperature readings from the Reactor
def ReadReactorTemp(ard):
    try:
        s= ard.analogRead(ReactorTempSensor) 
        Sensor = [s]*6
        run=True
        return Sensor
    except:
        run=False
        return -1
        #print("Temp reading Failed!")


## Get Temperature readings from the Heather
def ReadHeatherTemp(ard):
    try:
        s= ard.analogRead(HeatherTempSensor) 
        Sensor = [s]*6
        run=True
        return Sensor
    except:
        run=False
        return -1
        #print("Temp reading Failed!")


##def VoltsToCelc():








##CODE TO TEST SCRIPT

debug= 0
if debug:
    A = ArdConnect('COM15')
    ArdSetup(A)
    while True:

        ReactTemp = ReadReactorTemp(A)
        print(ReactTemp[1])
        HeatherTemp = ReadHeatherTemp(A)
        print(HeatherTemp[1])

        # MoveStirrMotors(A,rpm=0.1,en=True)
        # Heat(A,op=0.3,en=True)
        print(run)
        time.sleep(5)
   

