from nanpy import ArduinoApi, SerialManager, Stepper #pip install nanpy

import time 
import math

run =False


#### Arduino Pins & variables #######
HeatherTempSensor = ['A1','A1','A1','A1','A1','A1'] #Heater Thermistor PIN
ReactorTempSensor = ['A2','A2','A2','A2','A2','A2'] #Reactor Thermistor PIN
StirringMotor = [[46,47,48,49],[46,47,48,49],[46,47,48,49],[46,47,48,49],[46,47,48,49],[46,47,48,49]] # Stirring motor output
#PWM, pins 2-13
Output_heater = [3,3,3,3,3,3] #PWM outputs for heaters
#################


led=13
stepsPerRevolution = 200
#motor = Stepper(stepsPerRevolution, 8,9,10,11)



## CONNECT FUNCTION ##
def ArdConnect(com):
    global run
    try:
  
        connection = SerialManager(device=com)
        ard = ArduinoApi(connection=connection)
        print(">>Arduino connected]")
        run = True
        return ard
    except:
        run=False
        print('->Arduino is not connected')
        return 'EMPTY'

# ArdConnect('COM15')

## SETUP Arduino FUNCTION ##
def ArdSetup(ard):
    global run
    try:
        ard.pinMode(HeatherTempSensor, ard.INPUT)
        ard.pinMode(ReactorTempSensor, ard.INPUT)
        ard.pinMode(led, ard.OUTPUT)

        print('[Arduino setup...OK]')
        run = True
    except:
        run=False
        print("[Arduino setup...Failed]")


## 
def ControlStirringMotors(ard,i,rpm,en=True):
    global run
    try:

        rpm=rpm
        #myStepper.setSpeed(motorSpeed)

        run = True
    except:
        run=False
        print('[Stirring motors Failed]')

## SET OUTPUTS for Heater
def ControlHeaters(ard,i,op,en=True):
    global run
    try:
        ard.digitalWrite(Output_heater[i], op)
        run = True
    except:
        run=False
        print('[Heating Failed]')

## Get Temperature readings from the Reactor
def ReadReactorTemp(ard,i):
    global run
    try:
        read =  ReadToCelcious( ard.analogRead(ReactorTempSensor[i]) )
        run = True
        return read
    except:
        run=False
        print('[Temperature reading Failed]')

## Get Temperature readings from the Heather
def ReadHeatherTemp(ard,i):
    global run
    try:
        read = ReadToCelcious( ard.analogRead(HeatherTempSensor[i]) )
        run = True
        return read
    except:
        run=False

## https://learn.adafruit.com/thermistor/using-a-thermistor
def ReadToCelcious(read):
    # resistance at 25 degrees C
    THERMISTORNOMINAL = 10000      
    # temp. for nominal resistance (almost always 25 C)
    TEMPERATURENOMINAL = 25   
    # how many samples to take and average, more takes longer
    # but is more 'smooth'
    NUMSAMPLES = 5
    # The beta coefficient of the thermistor (usually 3000-4000)
    BCOEFFICIENT = 3950
    # the value of the 'other' resistor
    SERIESRESISTOR = 10000

    # convert the value to resistance
    R = 1023 / (read - 1)
    R = SERIESRESISTOR / R

    steinhart = R / THERMISTORNOMINAL             # (R/Ro)
    steinhart = math.log(steinhart)                    # ln(R/Ro)
    steinhart = steinhart/BCOEFFICIENT                           # 1/B * ln(R/Ro)
    steinhart = steinhart+ 1.0 / (TEMPERATURENOMINAL + 273.15)    # + (1/To)
    steinhart = 1.0 / steinhart                         # Invert
    steinhart = steinhart - 273.15 

    return round(steinhart,1)

def ValidateConnection(ard):
    global run
    try:
        r=ard.digitalRead(led)
        if r:
            ard.digitalWrite(led, ard.LOW )
        else:
            ard.digitalWrite(led, ard.HIGH )
        run = True
        return True
    except:
        run=False
        return False