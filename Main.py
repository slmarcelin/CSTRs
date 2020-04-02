# !/usr/bin/python3

# ==== Required Packages =================================================
# Site Packages -----
from simple_pid import PID  # https://pypi.org/project/simple-pid/
import matplotlib.pyplot as plt  # https://pypi.org/project/matplotlib/
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk  # https://pypi.org/project/Pillow/

# Inbuilt packages ------
import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import sys
import os
from functools import partial
from threading import Timer
from datetime import datetime, timedelta
import time

# Project files ---------
import ArdFunct as ard
import CsvFunct as CSV
import PandaFunct as Panda
# ==== Required Packages (END) ===============================================


# --- Definition of _Reactor class and object creation -------------------
class Reactor(object):

    def __init__(self, Name):
        self.Name = Name  # Name of reactor
        self.Enable = CSV.Enable  # Enable/Disable of reactor

        # Temperature Control part
        self.DesiredTemp = CSV.DesiredTemp  # Desired temperature in °C
        self.CurrentTemp = [0] * 6  # Current temperature in °C
        self.oldHeaterTemp = [0] * 6  # Previous heater temperature
        self.HeaterTemp = [0] * 6  # Heater temeperature read in °C
        self.OP = [0] * 6  # power of Heater (0-100% )
        self.Kp = list(CSV.Kp)
        self.Ki = CSV.Ki
        self.Kd = CSV.Kd   # PID parameters
        self.pid = [0]*6  # PID controller
        self.ThermalProtect = [0] * 6  # Thermal protection alert

        # Stirring Control part
        self.TimeOn = CSV.TimeOn    # Stirring duration in ON state
        self.TimeOff = CSV.TimeOff  # Stirring duration in OFF state
        self.StateTime = [datetime.now()] * 6  # Time when state changed
        self.RPM = CSV.RPM  # Speed of stirring
        self.StirrState = [True]*6  # Stirring state (On/Off)
# ------------------------------------------------------------------------


# Create a _Reactor class object
Reactor = Reactor(
    Name=['Reactor 1', 'Reactor 2', 'Reactor 3',
          'Reactor 4', 'Reactor 5', 'Reactor 6']
)

# Definition of PID for every reactor
for i in range(6):
    Reactor.pid[i] = PID(Reactor.Kp[i], Reactor.Ki[i], Reactor.Kd[i], Reactor.DesiredTemp[i])
    Reactor.pid[i].output_limits = (0, 100)

# -----------------------------------------------------------------------------


# ==== Application functions =================================================
#
# --- Stirring control by timmer ---------------------------------------------
# In this function, the stirring state is going to be managed...
# - A stirring state(On/Off) is going to change untill the curent time is equal
#   to the time when the state started(StateTime), plus the duration of
#   the state(TimeOn or TimeOff)
# - If an Arduino connection is not established or the current reactor
#   is 'disabled', the stirring state is going to remain same
def StirrOnOff():

    global StirrOnOffTimer  # Timmer used to loop this function

    for i in range(6):

        if ard.run is True:  # If arduino is connected,

            if Reactor.Enable[i] is True:  # If reactor is enabled,

                now = datetime.now()  # current time

                # --- Stirring state: 'On' ------
                if Reactor.StirrState[i] is True:  # if stirring is 'On'
                    # Change state to 'Off' when the 'On' time duration passed
                    if(Reactor.StateTime[i] +
                       timedelta(minutes=Reactor.TimeOn[i]) <= now):
                        # change State to 'Off'
                        Reactor.StirrState[i] = False
                        # update the time when the state changed
                        Reactor.StateTime[i] = now

                # --- Stirring state: 'Off' ------
                if Reactor.StirrState[i] is False:  # if stirring is 'Off'
                    # Change state to 'On' when the 'Off' time duration passed
                    if(Reactor.StateTime[i] +
                       timedelta(minutes=Reactor.TimeOff[i]) <= now):
                        # change State to 'On'
                        Reactor.StirrState[i] = True
                        # update the time when the state changed
                        Reactor.StateTime[i] = now

            else:  # if reactor is disabled, stirr state does not change
                # update the time when the state changed to the current time
                Reactor.StateTime[i] = datetime.now()

        else:  # if arduino is not connected, stirr state does not change
            # update the time when the state changed to the current time
            Reactor.StateTime[i] = datetime.now()

    # Update configuration control of stirring motors
    ard.StepperMotorReconfig(A, Reactor.RPM,
                             Reactor.StirrState,
                             Reactor.Enable,
                             Reactor.OP)

    # --- Loop this function on a timer threading ----
    StirrOnOffTimer = Timer(1, StirrOnOff)
    StirrOnOffTimer.daemon = True
    StirrOnOffTimer.start()
# ----------------------------------------------------------------------------


# Update apparence and values of Labels, Texts and Buttons from GUI --
def GuiOutputUpdate():

    global GuiUpdateOutputsTimer  # Timmer used to loop this function

    r = selReact  # Current selected reactor(to be used as index)
    datenow = datetime.now()  # Current time

    # --- Left frame --------------------
    # date display
    dateStr = datenow.strftime('%A %d. %B %Y\n %H:%M:%S')
    GUI_Clock.configure(text=dateStr)

    # Reactor buttons
    for i in range(6):
        if i is not r:
            GUI_ReactorButtons[i].configure(bg=RGB_LeftBar_LightBlue,
                                            relief='raised')
    GUI_ReactorButtons[r].configure(bg=RGB_LeftBar_MidBlue, relief='sunken')
    # ------------------------------------

    # --- Reactor frame ------------------
    # reactor name
    GUI_Reactor_Name.configure(text=Reactor.Name[r])

    # Enable/Disable button configuration
    if Reactor.Enable[r] is True:
        GUI_Enable_Button.configure(text='Enabled',
                                    bg='green2', fg='dark green')
    else:
        GUI_Enable_Button.configure(text='Disabled',
                                    bg='red', fg='dark red')
    # ------------------------------------

    # --- Temperature frame --------------
    # Current temperature
    GUI_CurrentTemp_Value.configure(text='{}°C'.format(Reactor.CurrentTemp[r]))
    # Heater power output
    GUI_HeaterPower_Label.configure(text='Heating power: {}% '. format(int(Reactor.OP[r])))
    # Heater temperature
    GUI_HeaterTemp_Label.configure(text='Heater: {}°C'.format(
        Reactor.HeaterTemp[r]))
    # ------------------------------------

    # --- Stirring frame -----------------
    # Stirring state
    if Reactor.StirrState[r] is True:
        GUI_StirrState_Label.configure(text='ON', bg='lime green')
    else:
        GUI_StirrState_Label.configure(text='OFF', bg='dark green')
    # Duration of current status
    s = (datetime.now() - Reactor.StateTime[r]).total_seconds()
    time = 'Timer: {:02d}:{:02d}:{:02d}'.format(
        int(s // 3600),  # Hours
        int(s % 3600 // 60),  # Minutes
        int(s % 60))  # Seconds
    GUI_StirrTime_Label.configure(text=time)
    # ------------------------------------

    # --- Bottom state bar -------------------
    # -Serial communication ports-
    ports = serial.tools.list_ports.comports()
    serial_ports = ['--']
    for port in sorted(ports):
        serial_ports.append(port.device)
    GUI_SerialPortValue.configure(values=serial_ports)
    GUI_SerialPortValue.delete(0, "end")
    GUI_SerialPortValue.insert(0, com)

    # connection status
    if A is not False:
        GUI_StateInfo.configure(text='Connected', fg='green4')
    else:
        GUI_StateInfo.configure(text='Connecting', fg='red')

    # Thermal protection
    for i in range(6):
        if Reactor.ThermalProtect[i] is True:
            GUI_ErrorInfo[i].configure(bg='red')
        else:
            GUI_ErrorInfo[i].configure(bg='GRAY87')
    # --------------------------------------

    # --- Loop this function on a timer threading ----
    GuiUpdateOutputsTimer = Timer(1, GuiOutputUpdate)
    GuiUpdateOutputsTimer.daemon = True
    GuiUpdateOutputsTimer.start()
# --------------------------------------------------------------------


# Update the input elements from the User interface of the GUI ------
def GUI_EntriesUpdate():

    r = selReact  # Current selected reactor(to be used as index)

    # Desired temperature value
    GUI_TargetTemp_Value.configure(state='normal')
    GUI_TargetTemp_Value.delete(0, 'end')
    GUI_TargetTemp_Value.insert(0, str(Reactor.DesiredTemp[r]))
    GUI_TargetTemp_Value.configure(state='readonly')

    # Stirring 'RPMs'
    GUI_Rpm_Value.configure(state='normal')
    GUI_Rpm_Value.delete(0, 'end')  # TimeOn Spin
    GUI_Rpm_Value.insert(0, str(Reactor.RPM[r]))
    GUI_Rpm_Value.configure(state='readonly')

    # Stirring 'ON' duration
    GUI_On_Value.configure(state='normal')
    GUI_On_Value.delete(0, 'end')  # TimeOn Spin
    GUI_On_Value.insert(0, str(Reactor.TimeOn[r]))
    GUI_On_Value.configure(state='readonly')

    # Stirring 'OFF' duration
    GUI_Off_Value.configure(state='normal')
    GUI_Off_Value.delete(0, 'end')  # TimeOn Spin
    GUI_Off_Value.insert(0, str(Reactor.TimeOff[r]))
    GUI_Off_Value.configure(state='readonly')
# -------------------------------------------------------------------


# Get new temperature values from arduino and manipulate actuators
# - Request new information to arduino(temperature values) and control
#   the heaters
# - The thermal protection is implemented here,to ensure a normal functionality
# - When an arduino connection is not established, this function is going to
#   try to start a connection with the selected serial communication port
# - This function is going to be called every 5 seconds
def UpdateStatus():
    global A,        UpdateStatusTimer

    # Get Reactor temperatures(Current temperature)
    Reactor.CurrentTemp = ard.ReadReactorTemp(A, Reactor.Enable)
    # Calculate OP with the PID functions
    Reactor.OP = PIDfunct()
    # Get Heater temperatures
    Reactor.HeaterTemp = ard.ReadHeaterTemp(A, Reactor.Enable)

    # -- Thermal protection control -----------------------------------------------
    # if the temperature of a heater is not increasing when the power is abobe 10%
    # then the thermal protection is going to turn on and the reactor is going to
    # be desabled (when a reactor is desabled, the heater and motor are off)
    for i in range(6):
        # (If reactor is enabled
        # and oldHeaterTemp already changed from the start of program
        # and change in heater temperature is < 3°c
        # and the heater power is above 20%)
        # Activate thermal protect and disable Reactor
        if ((Reactor.Enable[i] is True)and
                (Reactor.oldHeaterTemp[i] != 0)and
                (Reactor.HeaterTemp[i] - Reactor.oldHeaterTemp[i] < 5)and
                (Reactor.OP[i] > 20)):
            Reactor.ThermalProtect[i] = True  # thermal protect activated
            Reactor.Enable[i] = False  # reactor is disabled
            GuiOutputUpdate()
            msg = 'The heater temperature of Reactor {} is not changing. \
                 ,\n The reactor is now disabled.'.format(i+1)
            tk.messagebox.showwarning('Thermal protection', msg)
            print(msg)
    # --------------------------------------------------------------------------

    # Control heatres
    ard.ControlHeaters(A, Reactor.OP, Reactor.Enable)

    # Attempt to connect arduino(when connection is not established)
    if not(ard.run):
        A = ard.ArdConnect(com)
        if ard.run:
            ard.ArdSetup(A)

    # Save the last temperture(used for thermal protection)
    Reactor.oldHeaterTemp = Reactor.CurrentTemp

    # Timed repeated function
    UpdateStatusTimer = Timer(5, UpdateStatus)
    UpdateStatusTimer.daemon = True
    UpdateStatusTimer.start()
# ------------------------------------------------------------------


# Save the current temperature values in the CSV file
def DataLogger():
    global MinuteLoopTimer

    if ard.run:
        date = datetime.strftime(datetime.now(), '%Y-%m-%d')

        for i in range(6):
            if Reactor.Enable[i] is True and Reactor.CurrentTemp[i] != 0 and Reactor.HeaterTemp[i] != 0:
                print('--> Logs of Reactor{} saved'.format(i + 1))

                # ------ Logging Reactor Temperature -------------------------
                path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                 CSV.TempReactorName[i])

                # Check if CSV file is older than 30 days or bigger than 10MB
                check = fileCheck(CSV.TempReactorName[i], path, i)
                if check:  # If yes -> Create a new file

                    os.remove(path)  # Delete old file

                    # Update the file name and save it in the memory csv
                    CSV.TempReactorName[
                        i] = '{}-CSTR-{}-1.csv'.format(date, i + 1)
                    print('--> new file:', (CSV.TempReactorName[i]))
                    # Save the name in the Memory file
                    CSV.Memory_CSVnames(f=CSV.MemoryFile,
                                        trn=CSV.TempReactorName,
                                        thn=CSV.TempHeaterName,
                                        sin=CSV.StirringInfoName,
                                        fmn=CSV.FeedingMaterialName)
                    # Update path variable
                    path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                     CSV.TempReactorName[i])
                # Register temperature value
                CSV.LOG(f=path, header='Date,Reactor Temperature °C',
                        v1=Reactor.CurrentTemp[i])
                # ----------------------------------------------------------

                #
                # ------ Logging Heter temperature -------------------------
                path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                 CSV.TempHeaterName[i])

                # Check if CSV file is older than 30 days or bigger than 10MB
                check = fileCheck(CSV.TempHeaterName[i], path, i)
                if check:  # If yes -> Create a new file

                    os.remove(path)  # Delete old file

                    # Update the file name and save it in the memory csv
                    CSV.TempHeaterName[
                        i] = '{}-CSTR-{}-2.csv'.format(date, i + 1)
                    print('new file:', (CSV.TempHeaterName[i]))
                    # Save the name in the Memory file
                    CSV.Memory_CSVnames(f=CSV.MemoryFile,
                                        trn=CSV.TempReactorName,
                                        thn=CSV.TempHeaterName,
                                        sin=CSV.StirringInfoName,
                                        fmn=CSV.FeedingMaterialName)
                    # Update path variable
                    path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                     CSV.TempHeaterName[i])
                # Register heater temperature value
                CSV.LOG(f=path, header='Date,Heater Temperature °C',
                        v1=Reactor.HeaterTemp[i])
                # ----------------------------------------------------------

                # ------ Logging Stirring information -----------------------
                path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                 CSV.StirringInfoName[i])

                # Check if CSV file is older than 30 days or bigger than 10MB
                check = fileCheck(CSV.StirringInfoName[i], path, i)
                if check:  # If yes -> Create a new file

                    os.remove(path)  # Delete old file

                    # Update the file name and save it in the memory csv
                    CSV.StirringInfoName[
                        i] = '{}-CSTR-{}-3.csv'.format(date, i + 1)
                    print('new file:', (CSV.StirringInfoName[i]))
                    # Save the name in the Memory file
                    CSV.Memory_CSVnames(f=CSV.MemoryFile,
                                        trn=CSV.TempReactorName,
                                        thn=CSV.TempHeaterName,
                                        sin=CSV.StirringInfoName,
                                        fmn=CSV.FeedingMaterialName)
                    # Update path variable
                    path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                     CSV.StirringInfoName[i])
                # Register Stirring information
                CSV.LOG(f=path, header='Date,RPM,ON,OFF',
                        v1=Reactor.RPM[i],
                        v2=Reactor.TimeOn[i],
                        v3=Reactor.TimeOff[i])
                # -----------------------------------------------------------

    MinuteLoopTimer = Timer(30*60, DataLogger)  # Save data every 30 mins
    MinuteLoopTimer.daemon = True
    MinuteLoopTimer.start()  # Restart Timer
# ------------------------------------------------------------


# Check if the file is older than 30 days or bigger than 10 MB
# Return True when the file is older than 30 days OR bigger than 10 MB
def fileCheck(fileName, path, reactor):

    # get how old the file is
    date = fileName[0:10]  # CVS's date (dd-mm-yyyy)
    delta = datetime.now() - datetime.strptime(date, '%Y-%m-%d')
    age = abs(delta.days)

    # get size of file
    statinfo = os.stat(path)
    size = statinfo.st_size  # output in bytes

    # Condition evaluation
    if age > 30 or size > 30 * 1_000_000:
        return True
    else:
        return False
# ------------------------------------------------------------


# Get the Operation point(OP) value in (0-100%)
def PIDfunct():
    op = [0] * 6

    for i in range(6):
        if Reactor.Enable[i] and ard.run is True:
            op[i] = Reactor.pid[i](Reactor.CurrentTemp[i])  # compute a new output value
    return op
# ------------------------------------------------------------
#
# ==== Application functions (END) ============================================


# ==== Function commands used in GUI Objects ==================================
#
# Change of a resired temperature value
def SetPointChange(value=0):
    print(value)
    # Update vallue
    Reactor.DesiredTemp[selReact] = int(GUI_TargetTemp_Value.get())

    # Change setpoint of the corresponding PID
    Reactor.pid[selReact].setpoint = Reactor.DesiredTemp[selReact]
    print('Reactor{}, DesiredTemp: {}'.format(selReact+1, Reactor.DesiredTemp[selReact]))
# --------------------------------------


# Change of the 'ON' duration of stiring device
def OnTimeChange():
    # Update vallue
    Reactor.TimeOn[selReact] = int(GUI_On_Value.get())
    print('Reactor{}, TimerOn changed', format(selReact))
# -----------------------------------------------


# Change of the 'OFF' duration of stiring device
def OffTimeChange():
    # Update vallue
    Reactor.TimeOff[selReact] = int(GUI_Off_Value.get())
    print('Reactor{}, TimerOff changed', format(selReact))
# -----------------------------------------------


# Change of the speed of stiring device
def StirrRpmChange():

    # Update vallue
    Reactor.RPM[selReact] = int(GUI_Rpm_Value.get())
    print('Reactor', selReact + 1, 'changed to', Reactor.RPM[selReact], 'RPMs')
# -----------------------------------------------


# Change of serial communication port
def SerialPortChange(event):
    global com, A

    com = GUI_SerialPortValue.get()

    print('--> Selected port changed to:', com)
    return True
# -----------------------------------------------


# Change of state of Enable button
def EnableReactChange():

    # (Enable/Disable) Reactor
    Reactor.Enable[selReact] = not Reactor.Enable[selReact]
    print('--> Reactor', selReact + 1, 'enabled:', Reactor.Enable[selReact])

    # When Reactor changed from 'Disabled' to 'Enabled':
    if Reactor.Enable[selReact] is True:
        Reactor.ThermalProtect[selReact] = False  # Deactivate thermal alarm

    GUI_EntriesUpdate()  # update input elements in GUI
    GuiOutputUpdate()  # update labels in GUI
# ------------------------------------------------


# Entering of new feeding material data
def FeedMaterialEnter():
    date = datetime.strftime(datetime.now(), '%Y-%m-%d')

    # Get values to save
    Amount = GUI_Qty_value.get()
    Unit = GUI_Unit_value.get()
    Material = GUI_Material_value.get()
    #

    # if all inputs are entered,then the feed material is going to be saved
    if (Amount != '') and (Unit != '') and (Material != ''):

        i = selReact
        # ------ Logging Feeding material -----------------------
        path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                         CSV.FeedingMaterialName[i])

        # Check if CSV file is older than 30 days or bigger than 10MB
        check = fileCheck(CSV.FeedingMaterialName[i], path, i)
        if check:  # If yes -> Create a new file

            os.remove(path)  # Delete old file

            # Update the file name and save it in the memory csv
            CSV.FeedingMaterialName[
                i] = '{}-CSTR-{}-4.csv'.format(date, i + 1)
            print('new file:', (CSV.FeedingMaterialName[i]))
            # Save the name in the Memory file
            CSV.Memory_CSVnames(f=CSV.MemoryFile,
                                trn=CSV.TempReactorName,
                                thn=CSV.TempHeaterName,
                                sin=CSV.StirringInfoName,
                                fmn=CSV.FeedingMaterialName)
            # Update path variable
            path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                             CSV.FeedingMaterialName[i])
        # Register Stirring information
        CSV.LOG(f=path, header='Date,Qty,Unit,Material',
                v1=GUI_Qty_value.get(),
                v2=GUI_Unit_value.get(),
                v3=GUI_Material_value.get())
        # -----------------------------------------------------------

        # Display confirmation message and clear feed material objects
        tk.messagebox.showinfo(title='Feeding material', message='Feed material entered')
    else:
        tk.messagebox.showerror(title='Feeding material', message='The information is not complete')

    # Clear input values
    GUI_Qty_value.delete(0, 'end')
    GUI_Unit_value.delete(0, 'end')
    GUI_Material_value.delete(0, 'end')
    print('Material fed')
# ------------------------------------------------


# Pressing of PID changing parameter button
def PidTunningButton():

    # Window creation and geometry patameters
    top = tk.Toplevel()
    top.title('Reactor{} PID controler'.format(selReact + 1))
    top.resizable(False, False)

    # PIDTunning parameter label
    PIDlabel = tk.Label(top, text='TUNNING PARAMETERS',
                        bg=RGB_LeftBar_DarkBlue, fg='white',
                        font=font_medium, width=30)
    PIDlabel.grid(pady=5, row=0, column=0, columnspan=2)

    # PID parameters
    # Proportional gain parameter
    Kplabel = tk.Label(top, text='Proportional gain (Kp):',
                       font=font_small)
    Kplabel.grid(row=1, column=0, sticky='W')
    #
    KpValue = tk.Entry(top, fg='green', font=font_small)
    KpValue.insert(0, Reactor.Kp[selReact])
    KpValue.grid(row=1, column=1)

    # Integral gain parameter
    Kilabel = tk.Label(top, text='Integral gain (Ki):',
                       font=font_small)
    Kilabel.grid(row=2, column=0, sticky='W')
    #
    KiValue = tk.Entry(top, fg='green', font=font_small)
    KiValue.insert(0, Reactor.Ki[selReact])
    KiValue.grid(row=2, column=1)

    # Derivative gain parameter
    Kdlabel = tk.Label(top, text='Derivative gain (Kd):',
                       font=font_small)
    Kdlabel.grid(row=3, column=0, sticky='W')
    #
    KdValue = tk.Entry(top, fg='green', font=font_small)
    KdValue.insert(0, Reactor.Kd[selReact])
    KdValue.grid(row=3, column=1)

    # Enter button action
    def enter_btn():
        Reactor.Kp[selReact] = KpValue.get()
        Reactor.Ki[selReact] = KiValue.get()
        Reactor.Kd[selReact] = KdValue.get()
        Reactor.pid[selReact].tunings = (Reactor.Kp[selReact],
                                         Reactor.Ki[selReact],
                                         Reactor.Kd[selReact])
        print('Reactor', selReact+1, 'PID parameter modified')
        top.destroy()
        top.update()

    # Enter button
    PID_EnterButton = tk.Button(top, text='Enter',
                                font=font_small, width=40, command=enter_btn)
    PID_EnterButton.grid(row=4, column=0, columnspan=2)

    top.mainloop()
# ------------------------------------------------


# Pressing of a Reactor selecting button
def ChangeReactor(r=0):
    global selReact
    selReact = r

    print('Reactor {0} selected'.format(selReact + 1))

    GUI_EntriesUpdate()
    GuiOutputUpdate()
    UpdatePlot(days=selRange, ax=ax)
# ------------------------------------------------


# Update of a ploth by a selected range(by buttons)
def UpdatePlot(days, ax):

    global selRange, selReact

    if days != 0:
        selRange = days

    # Reactor temperature CSV file
    RTPath = '{}/{}'.format(CSV.ReactorFolder[selReact],
                            CSV.TempReactorName[selReact])
    # Heater temperature CSV file
    HTPath = '{}/{}'.format(CSV.ReactorFolder[selReact],
                            CSV.TempHeaterName[selReact])

    # obtain date for last 24 hrs
    desiredRange = timedelta(hours=24 * selRange)
    now = datetime.now()  # get today's date
    TimeRange = now - desiredRange  # Get the date

    if selRange == 1:
        # desiredRange=datetime.timedelta(hours=24) #obtain date for last 24
        # hrs

        GUI_24HourButton.configure(relief='sunken')
        GUI_WeekButton.configure(relief='raised')
        GUI_MonthButton.configure(relief='raised')
        GraphTitle = 'Hour Rate'  # Title of the graph
        xlabel = 'Last 24 hours'  # set the x axis label
        rate = '360min'
        rate = '1min'

    if selRange == 7:
        # desiredRange=datetime.timedelta(days=7) #obtain date for last 24 hrs

        GUI_24HourButton.configure(relief='raised')
        GUI_WeekButton.configure(relief='sunken')
        GUI_MonthButton.configure(relief='raised')
        GraphTitle = 'Week Rate'  # Title of the graph
        xlabel = 'Last 7 days'  # set the x axis label
        rate = '12h'

    if selRange == 32:
        # desiredRange=datetime.timedelta(days=32) #obtain date for last 24 hrs

        GUI_24HourButton.configure(relief='raised')
        GUI_WeekButton.configure(relief='groove')
        GUI_MonthButton.configure(relief='raised')
        GraphTitle = 'Month Rate'  # Title of the graph
        xlabel = 'Last 32 days'  # set the x axis label
        rate = 'D'

    now = datetime.now()  # get today's date
    TimeRange = now - desiredRange  # Get the date

    ReactorTemperatureDF = Panda.FileDataFrame(
        path=RTPath, rate=rate, TimeRange=TimeRange, now=now)  # Reactor Temperature DataFrame
    HeaterTemperatureDF = Panda.FileDataFrame(
        path=HTPath, rate=rate, TimeRange=TimeRange, now=now)  # Heater Temperature DataFrame

    # This arrays formats the x axis, according to time or dates
    locator = mdates.AutoDateLocator()  # from the matpotlib library package
    formatter = mdates.ConciseDateFormatter(locator)  # specific type of style
    formatter.formats = ['%y', '%b', '%d', '%H:%M',
                         '%H:%M', '%S.%f', ]  # Format the dates
    formatter.zero_formats = [''] + formatter.formats[:-1]  # add format
    formatter.zero_formats[3] = '%d-%b'  # format
    formatter.offset_formats = [
        '', '%Y', '%b %Y', '%d %b %Y', '%d %b %Y', '%d %b %Y %H:%M', ]  # other format

    if not ReactorTemperatureDF.empty and not HeaterTemperatureDF.empty:
        ax.cla()
        p1 = ax.plot(ReactorTemperatureDF, marker='.',
                     markersize=8, linestyle='-', color='DarkBlue')
        p2 = ax.plot(HeaterTemperatureDF, marker='.', markersize=8,
                     linestyle='-', color='red')  # plot the data
        ax.legend((p1[0], p2[0]), ('Reactor', 'Heater'))
        ax.grid()

        ax.xaxis.set_major_locator(locator)  # set the x axis locator
        ax.xaxis.set_major_formatter(formatter)  # set format

    else:
        ax.cla()
        GraphTitle = 'Not enough data to graph the ' + GraphTitle + ' for Reactor ' + \
            str(selReact + 1) + '\nTry again later or pick another option'

    ax.set_title(GraphTitle, size=12 * zl)  # set the graph title
    ax.set_xlabel(xlabel, size=12 * zl)  # set the x axis label
    ax.set_ylabel('°C Degrees', size=12 * zl)  # set the y axis label

    graph.draw()

    print('PLOT UPDATED')
# ---------------------------------------------
#
# ==== Function commands used in GUI Objects (END) ============================


# ==== GUI SECTION ============================================================

selReact = 0  # Current selected reactor to be displayed
selRange = 1  # Selected range to be ploted

# ---- Arduino Serial communication port --------------------
serial_ports = []  # List of communication ports
com = CSV.COM  # Initialize communication port to the last saved value
A = []  # variable used to store communication object


# Color formats
RGB_LeftBar_DarkBlue = '#{:02X}{:02X}{:02X}'.format(0, 0, 140)
RGB_LeftBar_MidBlue = '#{:02X}{:02X}{:02X}'.format(82, 136, 174)
RGB_LeftBar_LightBlue = '#{:02X}{:02X}{:02X}'.format(199, 214, 221)

RGB_Temperature_title = 'dodgerBlue4'
RGB_Stirring_title = 'springgreen4'
RGB_Feeding_title = 'gold'
#
RGB_Sections_bg = 'gray92'
#
RGB_Graph_b1 = 'gray79'


# Main Window
GUI_Main_Window = tk.Tk()
GUI_Main_Window.title('CSRT Reactors control')

# get screen width and height
if os.name == 'nt':  # windows os
    GUI_Main_Window.state(newstate='zoomed')  # maximize main window(windows)
elif os.name == 'posix':  # linux os
    GUI_Main_Window.attributes('-zoomed', True)  # maximize main window(linux)
GUI_Main_Window.update()  # update size values
sw = GUI_Main_Window.winfo_width()  # width of the screen
sh = GUI_Main_Window.winfo_height()  # height of the screen

# Main window resize according to zoom value
z = 0.9  # Main window zoom(1 is full screen)
w = int(sw * z)  # width for the Tk root
h = int(sh * z)  # height for the Tk root
zl = 1.5 * z  # Font zoom

# get x and y Main window position values
x = GUI_Main_Window.winfo_x()
y = GUI_Main_Window.winfo_y()

# Configurate size and position of Main window
if os.name == 'nt':  # windows os
    GUI_Main_Window.state(newstate='normal')  # normalize main window(windows)
elif os.name == 'posix':  # linux os
    GUI_Main_Window.attributes('-zoomed', False)  # normalize main window(linux)
GUI_Main_Window.geometry('{}x{}+{}+{}' .format(w, h, x, y))
GUI_Main_Window.resizable(False, False)


# Font config
font_name = 'calibri'
font_small = (font_name, int(10 * zl))
font_small_bold = (font_name, int(11 * zl), 'bold')
font_medium = (font_name, int(12 * zl))
font_medium_bold = (font_name, int(12 * zl), 'bold')
font_big = (font_name, int(32 * zl))


# ----- Left section of GUI  -------------------------------
GUI_Selection_Area = tk.Canvas(GUI_Main_Window,
                               bg=RGB_LeftBar_DarkBlue, highlightthickness=0)
GUI_Selection_Area.place(relx=0, rely=0, relwidth=0.2, relheight=1)
# Date info
GUI_Clock = tk.Label(GUI_Selection_Area,
                     bg='blue', fg='white',
                     font=font_medium_bold)
GUI_Clock.place(relx=0, rely=0.03, relwidth=1, relheight=(1/12))
# # -- Column of buttons
GUI_ReactorButtons = [0] * 6
for i in range(6):
    GUI_ReactorButtons[i] = tk.Button(GUI_Selection_Area,
                                      text=Reactor.Name[i],
                                      bg=RGB_LeftBar_LightBlue,
                                      font=font_medium,
                                      command=partial(ChangeReactor, i))
    GUI_ReactorButtons[i].place(relx=0, rely=(3+i)*(1/16),
                                relwidth=1, relheight=1/16)
# --------------------------------------------------------------


# ----- Right main display Area -------------------------------
GUI_Display_Area = tk.Frame(GUI_Main_Window, bg='white', bd=2)
GUI_Display_Area.place(relx=0.2, rely=0,
                       relwidth=0.8, relheight=1)
#

# ------- Reactor frame --------------
GUI_Reactor_Frame = tk.Frame(GUI_Display_Area,
                             bg='black', bd=1, padx=2, pady=2,
                             relief='solid')
GUI_Reactor_Frame.place(relx=0.0, rely=0.025,
                        relwidth=1, relheight=0.4)

GUI_Reactor_Name = tk.Label(GUI_Reactor_Frame, text='Name',
                            bg='white', fg='black', bd=2,
                            relief='solid',
                            font=font_medium, anchor='w')
GUI_Reactor_Name.place(relx=0.0, rely=0.0,
                       relwidth=1, relheight=0.12)

GUI_Enable_Button = tk.Button(GUI_Reactor_Frame, text='EN/DIS',
                              bg='light blue', bd=2,
                              relief='solid',
                              font=font_medium, command=EnableReactChange)
GUI_Enable_Button.place(relx=0.8, rely=0.0,
                        relwidth=0.2, relheight=0.12)

# ------- TEMPERATURE FRAME -----------------------------
# Frame
GUI_Temperature_Frame = tk.Frame(GUI_Reactor_Frame,
                                 bg=RGB_Sections_bg, bd=2, padx=5, pady=5,
                                 relief='solid')
GUI_Temperature_Frame.place(relx=0, rely=0.12,
                            relwidth=1/3, relheight=0.88)
# Temperature label
GUI_TempLabel = tk.Label(GUI_Temperature_Frame, text='Temperature',
                         bg=RGB_Temperature_title, fg='white',
                         font=font_medium, anchor='w')
GUI_TempLabel.place(relx=0, rely=0,
                    relwidth=1, relheight=0.14)
# Target temp. label
GUI_TargetTemp_Label = tk.Label(GUI_Temperature_Frame, text='Target',
                                bg=RGB_Sections_bg, fg='black',
                                font=font_small_bold, anchor='w')
GUI_TargetTemp_Label.place(relx=0, rely=0.15,
                           relwidth=0.5, relheight=0.15)
# Target temp. value
GUI_TargetTemp_Value = tk.Spinbox(GUI_Temperature_Frame, from_=20, to=50,
                                  fg='green', command=SetPointChange,
                                  font=font_big, relief='solid')
GUI_TargetTemp_Value.place(relx=0, rely=0.3,
                           relwidth=0.3, relheight=0.25)
# Current temp. label
GUI_CurrentTemp_Label = tk.Label(GUI_Temperature_Frame, text='Current',
                                 bg=RGB_Sections_bg, fg='black',
                                 font=font_small_bold, anchor='w')
GUI_CurrentTemp_Label.place(relx=0.5, rely=0.15,
                            relwidth=0.5, relheight=0.15)
GUI_CurrentTemp_Value = tk.Label(GUI_Temperature_Frame, text='x °C',
                                 bg=RGB_Sections_bg, fg=RGB_Temperature_title,
                                 font=font_big, anchor='w')
GUI_CurrentTemp_Value.place(relx=0.5, rely=0.3,
                            relwidth=0.5, relheight=0.25)
# Heater power level
GUI_HeaterPower_Label = tk.Label(GUI_Temperature_Frame, text='Heater power',
                                 bg='white', fg='red', borderwidth=1,
                                 font=font_small, relief='solid',)
GUI_HeaterPower_Label.place(relx=0.5, rely=0.7, relwidth=0.5, relheight=0.15)
# Heater temperature sensor
GUI_HeaterTemp_Label = tk.Label(GUI_Temperature_Frame, text='Heater temp',
                                bg=RGB_Sections_bg, fg='black',
                                font=font_small, anchor='w')
GUI_HeaterTemp_Label.place(relx=0.5, rely=0.85, relwidth=0.5, relheight=0.1)
# PID button
GUI_Pid_Button = tk.Button(GUI_Temperature_Frame, text='PID',
                           bg=RGB_Graph_b1,
                           font=font_small, command=PidTunningButton)
GUI_Pid_Button.place(relx=0.01, rely=1 - 0.15, relwidth=0.2, relheight=0.14)

# ------- STIRRING FRAME -----------------------------
# Frame
GUI_Stirring_Frame = tk.Frame(GUI_Reactor_Frame,
                              bg=RGB_Sections_bg, bd=2, padx=5, pady=5,
                              relief='solid')
GUI_Stirring_Frame.place(relx=1/3, rely=0.12,
                         relwidth=1 / 3, relheight=0.88)
# Stirring Label
GUI_Stirr_Label = tk.Label(GUI_Stirring_Frame, text='Stirring',
                           bg=RGB_Stirring_title, fg='white',
                           font=font_medium, anchor='w')
GUI_Stirr_Label.place(relx=0, rely=0,
                      relwidth=1, relheight=0.14)
# Duration label
GUI_Duration_Label = tk.Label(GUI_Stirring_Frame, text='Inteval duration (min)',
                              bg=RGB_Sections_bg, fg='black',
                              font=font_small_bold, anchor='w')
GUI_Duration_Label.place(relx=0, rely=0.15, relwidth=0.5, relheight=0.15)
# On time label
GUI_On_Label = tk.Label(GUI_Stirring_Frame, text='ON ',
                        bg=RGB_Sections_bg, fg='black',
                        font=font_small, anchor='e')
GUI_On_Label.place(relx=0, rely=0.3, relwidth=0.2, relheight=0.15)
# On time Value
GUI_On_Value = tk.Spinbox(GUI_Stirring_Frame, from_=1, to=60,
                          font=font_small,  relief='solid',
                          command=OnTimeChange)
GUI_On_Value.place(relx=0.2, rely=0.3, relwidth=0.2, relheight=0.15)
# Off time label
GUI_Off_Label = tk.Label(GUI_Stirring_Frame, text='OFF ',
                         bg=RGB_Sections_bg, fg='black',
                         font=font_small, anchor='e')
GUI_Off_Label.place(relx=0, rely=0.5, relwidth=0.2, relheight=0.15)
# Off time Value
GUI_Off_Value = tk.Spinbox(GUI_Stirring_Frame, from_=1, to=60,
                           font=font_small, relief='solid',
                           command=OffTimeChange)
GUI_Off_Value.place(relx=0.2, rely=0.5, relwidth=0.2, relheight=0.15)
#  Stirring Label
GUI_Rpm_Label = tk.Label(GUI_Stirring_Frame, text='RPM ',
                         bg=RGB_Sections_bg,
                         font=font_small, anchor='e')
GUI_Rpm_Label.place(relx=0.5, rely=0.3, relwidth=0.2, relheight=0.15)
# RPM Spinbox
GUI_Rpm_Value = tk.Spinbox(GUI_Stirring_Frame, values=(60, 100, 200),
                           font=font_small, relief='solid',
                           command=StirrRpmChange)
GUI_Rpm_Value.place(relx=0.7, rely=0.3, relwidth=0.2, relheight=0.15)
# Stirring State
GUI_StirrState_Label = tk.Label(GUI_Stirring_Frame, text='ON/OFF',
                                borderwidth=1, font=font_medium, relief='solid')
GUI_StirrState_Label.place(relx=0.25, rely=0.7, relwidth=0.55, relheight=0.2)
# Time counter
GUI_StirrTime_Label = tk.Label(GUI_Stirring_Frame, text='Time: 00.00.00',
                               bg=RGB_Sections_bg,
                               font=font_small, anchor='nw')
GUI_StirrTime_Label.place(relx=0.6, rely=0.9, relwidth=0.4, relheight=0.1)
#

# ------- Feeding Material FRAME -----------------------------
# Frame
GUI_FeedMat_Frame = tk.Frame(GUI_Reactor_Frame,
                             bg=RGB_Sections_bg, bd=2, padx=5, pady=5,
                             relief='solid')
GUI_FeedMat_Frame.place(relx=2/3, rely=0.12,
                        relwidth=1 / 3, relheight=0.88)

# Feed material Label
GUI_FeedMat_Label = tk.Label(GUI_FeedMat_Frame, text='Feeding Material',
                             bg=RGB_Feeding_title, fg='white',
                             font=font_medium, anchor='w')
GUI_FeedMat_Label.place(relx=0, rely=0,
                        relwidth=1, relheight=0.14)
# Amount label
GUI_Qty_Label = tk.Label(GUI_FeedMat_Frame, text='Qty',
                         bg=RGB_Sections_bg,  fg='black',
                         font=font_small_bold, anchor='w')
GUI_Qty_Label.place(relx=0.1, rely=0.2,
                    relwidth=0.15, relheight=0.15)
# Amount  value
GUI_Qty_value = tk.Entry(GUI_FeedMat_Frame, font=font_small)
GUI_Qty_value.place(relx=0.1, rely=0.35,
                    relwidth=0.15, relheight=0.14)
# Unit label
GUI_Unit_Label = tk.Label(GUI_FeedMat_Frame, text='Unit',
                          bg=RGB_Sections_bg, fg='black',
                          font=font_small_bold, anchor='w')
GUI_Unit_Label.place(relx=0.27, rely=0.2,
                     relwidth=0.2, relheight=0.15)
# Unit value
GUI_Unit_value = tk.Entry(GUI_FeedMat_Frame, font=font_small)
GUI_Unit_value.place(relx=0.27, rely=0.35,
                     relwidth=0.2, relheight=0.14)
# # - Feed material
GUI_Material_Label = tk.Label(GUI_FeedMat_Frame, text='Material',
                              fg='black', bg=RGB_Sections_bg,
                              font=font_small_bold, anchor='w')
GUI_Material_Label.place(relx=0.48, rely=0.2,
                         relwidth=0.4, relheight=0.15)
GUI_Material_value = tk.Entry(GUI_FeedMat_Frame, font=font_small)
GUI_Material_value.place(relx=0.48, rely=0.35,
                         relwidth=0.4, relheight=0.14)
# Enter button
GUI_Feed_button = tk.Button(GUI_FeedMat_Frame, text='Enter',
                            font=font_small, command=FeedMaterialEnter)
GUI_Feed_button.place(relx=0.1, rely=0.55,
                      relwidth=1 - 0.2, relheight=0.14)
#


# ------ Graphs Frame -----------------------------------------
# Frame
GUI_Graph_Frame = tk.Frame(GUI_Display_Area,
                           bg='white', bd=1, padx=0, pady=0,
                           relief='solid')
GUI_Graph_Frame.place(relx=0.0, rely=0.45,
                      relwidth=1, relheight=0.5)
# Plot Area
fig = plt.Figure(figsize=(3, 4), dpi=80 * z)  # figure to hold plot
ax = fig.add_subplot(111)
graph = FigureCanvasTkAgg(fig, master=GUI_Graph_Frame)
graph.get_tk_widget().place(relx=0, rely=0.05,
                            relwidth=0.9, relheight=0.95)
# Hour button
GUI_24HourButton = tk.Button(GUI_Graph_Frame, text='DAY',
                             bg=RGB_Graph_b1, font=font_medium,
                             command=partial(UpdatePlot, days=1, ax=ax))
GUI_24HourButton.place(relx=1 - 0.15, rely=1 * (1 / 6),
                       relwidth=0.15, relheight=(1 / 6))
# Week button
GUI_WeekButton = tk.Button(GUI_Graph_Frame, text='Week',
                           bg=RGB_Graph_b1, font=font_medium,
                           command=partial(UpdatePlot, days=7, ax=ax))
GUI_WeekButton.place(relx=1 - 0.15, rely=2 * (1 / 6),
                     relwidth=0.15, relheight=(1 / 6))
# Month button
GUI_MonthButton = tk.Button(GUI_Graph_Frame, text='Month',
                            bg=RGB_Graph_b1, font=font_medium,
                            command=partial(UpdatePlot, days=32, ax=ax))
GUI_MonthButton.place(relx=1 - 0.15, rely=3 * (1 / 6),
                      relwidth=0.15, relheight=(1 / 6))
#  Update button
GUI_UpdateButton = tk.Button(GUI_Graph_Frame, text='Update plot',
                             bg=RGB_Graph_b1,
                             font=font_medium,
                             command=partial(UpdatePlot, days=0, ax=ax))
GUI_UpdateButton.place(relx=1 - 0.15, rely=5 * (1 / 6),
                       relwidth=0.15, relheight=(1 / 6))
#

# ------ Status Bar ---------------------------------------------------
GUI_Status_Bar = tk.Frame(GUI_Main_Window,
                          bg='GRAY86', bd=1, padx=0, pady=0,
                          relief='solid')
GUI_Status_Bar.place(relx=0, rely=1 - 0.04,
                     relwidth=1, relheight=0.04)
# Serial port

GUI_SerialPortLabel = tk.Label(GUI_Status_Bar, text='PORT ',
                               bg='GRAY72', bd=1, padx=0, pady=0,
                               font=font_small, anchor='w', relief='groove')
GUI_SerialPortLabel.place(relx=0, rely=0, relwidth=0.3, relheight=1)
# Serial port selection
GUI_SerialPortValue = ttk.Combobox(GUI_SerialPortLabel, values=serial_ports,
                                   font=font_small)
GUI_SerialPortValue.bind("<<ComboboxSelected>>", SerialPortChange)  # on select, call function)
GUI_SerialPortValue.place(relx=0.15, rely=0, relwidth=0.4, relheight=1)

#  Connection state
GUI_StateInfo = tk.Label(GUI_SerialPortLabel, text='connection?',
                         bg='GRAY72',
                         font=font_small_bold)
GUI_StateInfo.place(relx=0.55, rely=0, relwidth=0.45, relheight=1)
# Thermal protection state
GUI_ThermalProtectLabel = tk.Label(GUI_Status_Bar, text='Therm. protect:',
                                   bg='GRAY72',
                                   font=font_small, anchor='w', relief='groove')
GUI_ThermalProtectLabel.place(relx=0.45, rely=0,
                              relwidth=0.55, relheight=1)
GUI_ErrorInfo = [0] * 6
for i in range(6):
    GUI_ErrorInfo[i] = tk.Label(GUI_ThermalProtectLabel,
                                text='{} {}'.format('Reactor ', i + 1),
                                font=font_small, relief='flat')
    GUI_ErrorInfo[i].place(relx=(3 / 15) + (i * 2 / 15),
                           rely=0, relwidth=(2 / 15), relheight=1)
# -----------------------------------------------------------------------
# ==== GUI SECTION (END)=======================================================


# ---- Object and Timer initialization ----------
UpdatePlot(selRange, ax)
StirrOnOff()
UpdateStatus()
DataLogger()
GUI_EntriesUpdate()
GuiOutputUpdate()
GUI_Main_Window.mainloop()
# ------------------------------------------------


# ---- Code to finish the apllication ----------------

# TURN HEATERS OFF
op = [0]*6  # 0% heater power
ard.ControlHeaters(A, op, Reactor.Enable)
#

# Set changes in Memory csv file
CSV.Memory_set(f=CSV.MemoryFile,
               DesiredTemp=Reactor.DesiredTemp,
               TimeOn=Reactor.TimeOn,
               TimeOff=Reactor.TimeOff,
               RPM=Reactor.RPM,
               Kp=Reactor.Kp,
               Ki=Reactor.Ki,
               Kd=Reactor.Kd,
               COM=com,
               Enable=Reactor.Enable)

print('--> APP Finished... OK')
sys.exit()
# --------------------------------------------------------
