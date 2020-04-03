
# Site Packages -----
from nanpy import ArduinoApi, SerialManager, AccelStepper   # https://pypi.org/project/nanpy/
from threading import Timer  # https://docs.python.org/3/library/threading.html

# Inbuilt packages ------
import time
import math


# ------------------------------------------------------------------------
# NOTE: Arduino Pins & variables must be defined here
# ------ Arduino Pins & variables ------
Heater_Pin_Out = [8, 2, 9, 10, 11, 12]  # Heater control(PWM outputs)
HeaterTemp_Pin_In = [1, 1, 1, 1, 1, 1]  # Heater temp. sensor(Analog inputs)
ReactorTemp_Pin_In = [2, 2, 2, 2, 2, 2]  # Reactor temp. sensor(Analog inputs)
# - Stepper motor pins
DIR_n_pin = [4, 22, 24, 25, 26, 27]  # DIR-
DIR_p_pin = [5, 28, 30, 31, 32, 33]  # DIR+
PUL_n_pin = [6, 34, 36, 27, 38, 39]  # PUL-
PUL_p_pin = [7, 30, 32, 33, 34, 35]  # PUL+
StepsPerRev = 200  # steps required for a revolution
# ------------------------------------------------------------------------------


# --- global variables ------------------------------------
stepperMotor = [0]*6  # List of the stepper motors
stepperMotor_RPM = [30]*6  # motor RPMs(manipulated by GUI)
stepperMotor_ON = [False]*6  # Enable of the motor(manipulated by program)
#
stirrTimer = 0  # Timer to call MotorControlling()
run = False  # Flag to indicate that arduino is performing properly
# --------------------------------------------------------


# --- Arduino connection function ---------------------------------------------
# This function attemprs to establish arduino communication.
# Arguments: com --> the serial communication port to connect
# * IF the communication could be done, returns an 'ArduinoApi' object
# else, returns a 'False' value
def ArdConnect(com):
    global run, connection
    try:
        # Establish serial communication with Arduino
        ard = ArduinoApi(SerialManager(device=com))
        #

        print('--> Arduino connected in port ' + com)
        run = True  # indicate that arduino connection is done
        return ard  # return an 'ArduinoApi' object

    except Exception:
        print('-->! Arduino is not connected')
        run = False  # indicate that arduino connection could not be done
        return False  # return a 'False' value
# -----------------------------------------------------------------------------


# --- Function to validate if arduino still connected -------------------------
# The function attempts to execute an arduino command to validate
# the connection
# Arguments: ard --> An 'ArduinoApi' object for communication
def checkConnection(ard):
    global run

    try:
        ArdMillis = ard.millis()
        run = True  # indicate that Arduino is performing properly
        return run

    except Exception:
        run = False  # indicate that something went wrong
        return run
# -----------------------------------------------------------------------------


# --- Arduino setup function --------------------------------------------------
# The outputs, inputs and other configuration settings are done
# Arguments: ard --> An 'ArduinoApi' object for communication
def ArdSetup(ard):
    global run, stepperMotor, PRM

    try:
        # --- Definition of output and input Arduino pins ---
        for i in range(6):
            ard.pinMode(ReactorTemp_Pin_In[i], ard.INPUT)  # Reactor temp sens.
            ard.pinMode(HeaterTemp_Pin_In[i], ard.INPUT)  # Heater temp sens.
            ard.pinMode(Heater_Pin_Out[i], ard.OUTPUT)  # Heater power

            # Stepper motors
            stepperMotor[i] = AccelStepper(interface=4,
                                           pin1=DIR_n_pin[i],
                                           pin2=DIR_p_pin[i],
                                           pin3=PUL_n_pin[i],
                                           pin4=PUL_p_pin[i],
                                           enable=True,
                                           connection=ard.connection)

            stepperMotor[i].setMaxSpeed(800.0)
        time.sleep(1)  # wait to crete stepper objects
        # --------------------------------------------------

        # Function to control the stepper motors
        MotorControlling(ard)  # (this function runs on a different
        #  threading on a loop with a timer)

        print('--> Arduino setup')
        run = True  # Indicate that the setup is done

    except Exception:
        print('-->! Arduino setup Failed ')
        run = False  # Indicate that the setup could not be done
# -----------------------------------------------------------------------------


# --- Stirring motors reconfiguration function --------
# Modify variables that are used to control the stepper motors
# Arguments:    ard -> An 'ArduinoApi' object for communication
#               rpm -> list with the speed of the motors (modified from GUI)
#               status -> List with the status of the motors(ON/OFF)
#               enable -> list with the enable status from every reactor
#               op -> list with the power of the heater
def StepperMotorReconfig(ard, rpm, status, enable, op):
    global stepperMotor_ON, stepperMotor_RPM, StepsPerRev

    if checkConnection(ard):    # If arduino is connected,...

        for i in range(len(rpm)):  # repeat for every reactor

            # Update RPMs for stepper motors----
            if stepperMotor_RPM != rpm:

                stepperMotor_RPM[i] = rpm[i]  # stepper RPM variable

                if isinstance(stepperMotor[i], AccelStepper):
                    stepsPerSecond = (stepperMotor_RPM[i]/60) * StepsPerRev
                    stepperMotor[i].setSpeed(stepsPerSecond)
                # Note: setSpeed receives steps per seconds as argument
            # -------------------------------------

            # We move the motor if: - Reactor is Enabled AND
            #                       - (Reactor status is ON or
            #                          heater power is ^50%)
            if enable[i] and ((status[i] is True) or (op[i] > 50)):
                stepperMotor_ON[i] = True
            else:
                stepperMotor_ON[i] = False
# -----------------------------------------------------------------------------


# --- Move stepper motors function --------------------------------------------
# Modify variables that are used to control the stepper motors
# Arguments:    ard -> The 'ArduinoApi' object for communication
def MotorControlling(ard):
    global stirrTimer, RPM_60, stepperMotor_RPM

    if checkConnection(ard):    # If arduino is connected,...
        try:

            for i in range(6):
                if stepperMotor_ON[i] is True:
                    stepperMotor[i].runSpeed()

            # re-call the function after the required time
            stirrTimer = Timer(0.005, MotorControlling, args=(ard,))
            stirrTimer.daemon = True
            stirrTimer.start()
            # --

        except Exception:
            print('-->! Stirring control Failed')

    else:  # if arduino is not connected,
        if isinstance(stirrTimer, Timer):  # stop re-calling the function
            stirrTimer.cancel()
# -----------------------------------------------------------------------------


# --- Heater controlling function ---------------------------------------------
# The heater outputs are controlled
# Arguments:    ard -> The 'ArduinoApi' object for communication
#               op -> Heater power (0%-100%)
#               Enabled -> list with the enable status from every reactor
def ControlHeaters(ard, op, Enabled):

    if checkConnection(ard):  # If arduino is connected,...

        try:
            for i in range(len(op)):
                # Set the digital PWM pin to the OP % duty cycle
                MaxDutyCycle = 100  # limit duty cycle to reduce power(255 is 100%)
                RealDutyCycle = int(op[i]*MaxDutyCycle/100)
                ard.analogWrite(Heater_Pin_Out[i], RealDutyCycle)
        except Exception:

            print('-->! Heater control Failed')
# -----------------------------------------------------------------------------


# --- Converts analog temperature readdings to °C -----------------------------
# Converts the analog read from arduino to °c
# Arguments:    read -> analog read value to convert to °c
# Reference -> https://learn.adafruit.com/thermistor/using-a-thermistor
def ReadToCelcious(read):

    # resistance at 25 degrees C
    THERMISTORNOMINAL = 10_000
    # temp. for nominal resistance (almost always 25 C)
    TEMPERATURENOMINAL = 25

    # The beta coefficient of the thermistor (usually 3000-4000)
    BCOEFFICIENT = 3950
    # the value of the 'other' resistor
    SERIESRESISTOR = 10_000

    # convert the value to resistance
    R = (1023 / read) - 1
    R = SERIESRESISTOR / R

    steinhart = R / THERMISTORNOMINAL           # (R/Ro)
    steinhart = math.log(steinhart)             # ln(R/Ro)
    steinhart = steinhart/BCOEFFICIENT          # 1/B * ln(R/Ro)

    steinhart = steinhart + (1.0 / (TEMPERATURENOMINAL + 273.15))   # + (1/To)
    steinhart = 1.0 / steinhart                         # Invert
    steinhart = steinhart - 273.15

    return round(steinhart, 1)
# -----------------------------------------------------------------------------


# --- Get Temperature readings from the Heater --------------------------------
# Arguments:    ard -> The 'ArduinoApi' object for communication
#               Enabled -> list with the enable status from every reactor
# returns a list with the temperature from every heater in °c
def ReadHeaterTemp(ard, Enabled):

    if checkConnection(ard):     # If arduino is connected,..

        try:
            readDegrees = [0]*6  # Local list to store the readings

            for i in range(6):

                if Enabled[i]:  # If the reactor is enabled,
                    # Get average of temperature readings
                    numSamples = 50  # number of samples to calculate average
                    analogRead = 0  # Local variable to calculate analog reading
                    sumRead = 0  # Local variable to sum all analog readings
                    avRead = 0  # Loval variable to calculate the Average

                    # Calculate average of analog readdings
                    for s in range(numSamples):
                        analogRead = ard.analogRead(HeaterTemp_Pin_In[i])  # Read from arduino
                        sumRead = sumRead + analogRead  # All analog readings
                        time.sleep(0.002)  # wait 2ms per every read
                    avRead = sumRead / numSamples  # Average of readings

                    # Convert to °C
                    readDegrees[i] = ReadToCelcious(avRead)

                else:  # if reactor is not enabled,
                    readDegrees[i] = 0  # return 0 value if reactor not enable

            return readDegrees  # return the temperature list

        except Exception:
            print('-->! Reading Heater temperature Failed')
            return [0]*6  # return a list with 0s when something failed

    else:
        return [0]*6  # return a list with 0s when arduino is not connected
# -----------------------------------------------------------------------------


# --- Get Temperature readings from the Reactor -------------------------------
# Arguments:    ard -> The 'ArduinoApi' object for communication
#               Enabled -> list with the enable status from every reactor
# returns a list with the temperature from every reactor in °c
def ReadReactorTemp(ard, Enabled):

    if checkConnection(ard):     # If arduino is connected,..

        try:
            readDegrees = [0]*6  # Local list to store the readings

            for i in range(6):

                if Enabled[i]:  # If the reactor is enabled,
                    # Get average of temperature readings
                    numSamples = 50  # number of samples to calculate average
                    analogRead = 0  # Local variable to calculate analog reading
                    sumRead = 0  # Local variable to sum all analog readings
                    avRead = 0  # Loval variable to calculate the Average

                    # Calculate average of analog readdings
                    for s in range(numSamples):
                        analogRead = ard.analogRead(ReactorTemp_Pin_In[i])  # Read from arduino
                        sumRead = sumRead + analogRead  # All analog readings
                        time.sleep(0.002)  # wait 2ms per every read
                    avRead = sumRead / numSamples  # Average of readings

                    # Convert to °C
                    readDegrees[i] = ReadToCelcious(avRead)

                else:  # if reactor is not enabled,
                    readDegrees[i] = 0  # return 0 value if reactor not enable

            return readDegrees  # return the temperature list

        except Exception:
            print('-->! Reading Reactor temperature Failed')
            return [0]*6  # return a list with 0s when something failed

    else:
        return [0]*6  # return a list with 0s when arduino is not connected

# -----------------------------------------------------------------------------
