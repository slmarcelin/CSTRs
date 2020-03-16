# !/usr/bin/python3
from simple_pid import PID
import Panda_funct as Panda
import ArdFunct as ard
import CsvFunct as CSV
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

import sys
from datetime import datetime, timedelta
from functools import partial
from threading import Timer
from PIL import ImageTk, Image
import tkinter as tk
# from tkinter import (Tk, Frame, Button, Entry, Canvas, Label,
# Spinbox, messagebox, Toplevel)


no_reactors = 6  # Number of reactors
rng = range(no_reactors)  # index of reactores


# --- Definition of _Reactor class and object creation -------------------
class Reactor(object):

    def __init__(self, Name):
        self.Name = Name  # Name of reactor
        self.Enable = CSV.Enable  # Enable/Disable of reactor

        # Temperature Control part
        self.SP = CSV.SP  # Desired temperature in °C
        self.PV = [0] * no_reactors  # Actual temperature in °C
        self.prevTemp = [0] * no_reactors  # Previous heater temperature
        self.HeaterTemp = [0] * no_reactors  # Heater temeperature read in °C
        self.OP = [0] * no_reactors  # power of Heater (0-100% )
        self.Kp = list(CSV.Kp)

        self.Ki = CSV.Ki
        self.Kd = CSV.Kd   # PID parameters
        self.ThermalProtect = [0] * no_reactors  # Thermal protection alert

        # Stirring Control part
        self.TimeOn = CSV.TimeOn    # Stirring duration in ON state
        self.TimeOff = CSV.TimeOff  # Stirring duration in OFF state
        self.StateTime = [datetime.now()] * no_reactors  # Time when state changed
        self.RPM = CSV.RPM  # Speed of stirring
        self.StirrState = [True]*no_reactors  # Stirring state (On/Off)


# Create a _Reactor class object
Reactor = Reactor(
    Name=['Reactor1', 'Reactor2', 'Reactor3',
          'Reactor4', 'Reactor5', 'Reactor6']
)


# Definition of PID for every reactor
pid1 = PID(Reactor.Kp[0], Reactor.Ki[0], Reactor.Kd[0], Reactor.SP[0])
pid2 = PID(Reactor.Kp[1], Reactor.Ki[1], Reactor.Kd[1], Reactor.SP[1])
pid3 = PID(Reactor.Kp[2], Reactor.Ki[2], Reactor.Kd[2], Reactor.SP[2])
pid4 = PID(Reactor.Kp[3], Reactor.Ki[3], Reactor.Kd[3], Reactor.SP[3])
pid5 = PID(Reactor.Kp[4], Reactor.Ki[4], Reactor.Kd[4], Reactor.SP[4])
pid6 = PID(Reactor.Kp[5], Reactor.Ki[5], Reactor.Kd[5], Reactor.SP[5])

pid1.output_limits = (0, 100)
pid2.output_limits = (0, 100)
pid3.output_limits = (0, 100)
pid4.output_limits = (0, 100)
pid5.output_limits = (0, 100)
pid6.output_limits = (0, 100)
# -----------------------------------------------------------------------------


# ==== Arduino Serial communication port======================================
# Port in which Arduino is connected
serial_ports = ['dev/ttyUSB0',
                'dev/ttyUSB1',
                'dev/ttyUSB2',
                'dev/ttyUSB3']  # List of communication ports(RaspberyPi)
serial_ports = ['COM10', 'COM15']  # List of communication ports(Windows)

com = CSV.COM  # Communication port to initialize GUI()
# ===========================================================================


# ==== Application functions =================================================

# --- Stirring control by timmer ---------------------------------------------
# In this function, the stirring state is going to be managed...
#
# A stirring state(On/Off) is going to change untill the curent time is equal
# to the time when the state started(StateTime), plus the duration of
# the state(TimeOn or TimeOff)
#
# If an Arduino connection is not established or the current reactor
# is 'disabled', the stirring state is going to remain same
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
        ard.StepperMotorReconfig(A, Reactor.RPM, Reactor.StirrState, Reactor.OP)

    # --- Loop this function on a timer threading ----
    StirrOnOffTimer = Timer(1, StirrOnOff)
    StirrOnOffTimer.daemon = True
    StirrOnOffTimer.start()
# ----------------------------------------------------------------------------


# Update apparence of Labels, Texts and Buttons from GUI
# Explain
# Explain
# Explain
def GuiOutputUpdate():

    global GuiUpdateOutputsTimer  # Timmer used to loop this function

    r = selReact  # Actual selected reactor(to be used as index)
    datenow = datetime.now()  # Current time

    # --- Left frame --------------------
    # date display
    dateStr = datenow.strftime('%d %b, %Y\n %H:%M:%S')
    GUI_Clock.configure(text=dateStr)

    # Reactor buttons
    for i in range(6):
        GUI_ReactorButtons[i].configure(bg=RGB_LeftBar_LightBlue,
                                        relief='raised')
    GUI_ReactorButtons[r].configure(bg=RGB_LeftBar_MidBlue, relief='sunken')
    # ------------------------------------

    # --- Reactor frame ------------------
    # reactor name
    GUI_Reactor_Name.configure(text=Reactor.Name[r])

    # Enable/Disable button configuration
    if Reactor.Enable[r] is True:
        GUI_Enable_Buttone.configure(text='Enabled',
                                     bg=RGB_Enable, fg='white')
    else:
        GUI_Enable_Buttone.configure(text='Disabled',
                                     bg=RGB_Disabled, fg='GRAY10')
    # ------------------------------------

    # --- Temperature frame --------------
    # Actual temperature
    GUI_ActualTemp_Value.configure(text='{}°C'.format(Reactor.PV[r]))
    # Heater power output
    GUI_HeaterPower_Label.configure(text='Heating power: {}% '. format(int(Reactor.OP[r])))
    # Heater temperature
    GUI_HeaterTemp_Label.configure(text='Heater: {}°C'.format(
        Reactor.HeaterTemp[r]))
    # ------------------------------------

    # --- Stirring frame -----------------
    # Stirring state
    if Reactor.StirrState[r] is True:
        GUI_StirrState_Label.configure(text='ON', bg=RGB_Stirring_ON)
    else:
        GUI_StirrState_Label.configure(text='OFF', bg=RGB_Stirring_OFF)
    # Duration of current status
    s = (datetime.now() - Reactor.StateTime[r]).total_seconds()
    time = 'Timer: {:02d}:{:02d}:{:02d}'.format(
        int(s // 3600),  # Hours
        int(s % 3600 // 60),  # Minutes
        int(s % 60))  # Seconds
    GUI_StirrTime_Label.configure(text=time)
    # ------------------------------------

    # --- Bottom state bar ---------------
    # Arduino connection State
    if ard.run is True:
        GUI_StateInfo.configure(text='Connected', fg='green4')
    else:
        GUI_StateInfo.configure(text='Connecting', fg='red')
    # Thermal protection
    for i in range(6):
        if Reactor.ThermalProtect[r]:
            GUI_ErrorInfo[r].configure(bg='red')
        else:
            GUI_ErrorInfo[r].configure(bg='GRAY84')
    # ------------------------------------

    # --- Loop this function on a timer threading ----
    GuiUpdateOutputsTimer = Timer(1, GuiOutputUpdate)
    GuiUpdateOutputsTimer.daemon = True
    GuiUpdateOutputsTimer.start()
# ----------------------------------------------------------------------------


# Update the Entry elements from the User interface
# Explain
# Explain
# Explain
def GUI_EntriesUpdate():

    r = selReact  # Actual selected reactor(to be used as index)

    # Desired temperature value
    GUI_TargetTemp_Value.configure(state='normal')
    GUI_TargetTemp_Value.delete(0, 'end')
    GUI_TargetTemp_Value.insert(0, str(Reactor.SP[r]))
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
# ----------------------------------------------------------------------------


# Get new temperature values from arduino and manipulate actuators
# Explain
# Explain
# Explain
def UpdateStatus():
    global A,        UpdateStatusTimer

    # Get Reactor temperatures
    Reactor.PV = ard.ReadReactorTemp(A, Reactor.Enable)
    # Calculate OP
    Reactor.OP = PIDfunct()
    # Get Heater temperatures
    Reactor.HeaterTemp = ard.ReadHeaterTemp(A, Reactor.Enable)

    # -- Thermal protection control -----------------------------------------------
    # if the temperature of a heater is not increasing when the power is abobe 10%
    # then the thermal protection is going to turn on and the reactor is going to
    # be desabled (when a reactor is desabled, the heater and motor are off)
    for i in range(6):
        # (If reactor is enabled
        # and prevTemp already changed from the start of program
        # and change in heater temperature is < 3°c
        # and the heater power is above 10%)
        # Activate thermal protect and disable Reactor
        if ((Reactor.Enable[i] is True)and
                (Reactor.prevTemp[i] != 0)and
                (Reactor.HeaterTemp[i] - Reactor.prevTemp[i] < 5)and
                (Reactor.OP[i] > 10)):
            Reactor.ThermalProtect[i] = True  # thermal protect activated
            Reactor.Enable[i] = False  # reactor is disabled
            msg = 'Heater from Reactor{} is not working'.format(i+1)
            messagebox.showwarning('Thermal protection', msg)
            print(msg)
        else:
            print('Heater', i+1, 'is working')

    # --------------------------------------------------------------------------

    # Control stirring motors
    # ard.StepperMotorReconfig(A, Reactor.RPM, Reactor.StirrState, Reactor.OP)

    # Control heatres
    ard.ControlHeaters(A, Reactor.OP, Reactor.Enable)

    if not(ard.run):
        A = ard.ArdConnect(com)
        if ard.run:
            ard.ArdSetup(A)

    Reactor.prevTemp = Reactor.PV  # Save the last temperture(used for thermal protection)

    UpdateStatusTimer = Timer(10, UpdateStatus)
    UpdateStatusTimer.daemon = True
    UpdateStatusTimer.start()
# ------------------------------------------------------------


# Save the current temperature values in the CSV file
def DataLogger():
    global MinuteLoopTimer

    if ard.run:
        date = datetime.strftime(datetime.now(), '%Y-%m-%d')

        for i in rng:
            if Reactor.Enable[i] and \
               Reactor.PV != 0 and \
               Reactor.HeaterTemp != 0:

                print('Saving logs from Reactor{}'.format(i + 1))

                # ------ Logging Reactor Temperature -------------------------
                path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                 CSV.TempReactorName[i])
                # Check if CSV file is older than 30 days or bigger than 10MB
                check = fileCheck(CSV.TempReactorName[i], path, i)

                if check:  # If yes,
                    # DETLETE OLD FILE
                    # code to delete fileNam
                    #

                    # Update the file name from the Setup file
                    CSV.TempReactorName[
                        i] = '{}-CSTR-{}-1.csv'.format(date, i + 1)
                    CSV.setup_CSVnames(f=CSV.SetupFile,
                                       trn=CSV.TempReactorName,
                                       thn=CSV.TempHeaterName,
                                       sin=CSV.StirringInfoName,
                                       fmn=CSV.FeedingMaterialName)
                    # Update path variable
                    path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                     CSV.TempReactorName[i])

                # Register temperature value
                CSV.LOG(f=path, header='Date,RPM,ON,OFF', v1=Reactor.PV[i])
                # ----------------------------------------------------------

                # ------ LOG HEATER TEMPERATURE ----------------------------
                path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder,
                                                 i + 1, CSV.TempHeaterName[i])

                # Check if CSV file is older than 30 days or bigger than 10MB
                check = fileCheck(CSV.TempHeaterName[i], path, i)

                if check:  # If yes,
                    # DETLETE OLD FILE
                    # code to delete fileNam
                    #

                    # Update the file name from the Setup file
                    CSV.TempReactorName[
                        i] = '{}-CSTR-{}-2.csv'.format(date, i + 1)
                    CSV.setup_CSVnames(f=CSV.SetupFile,
                                       trn=CSV.TempReactorName,
                                       thn=CSV.TempHeaterName,
                                       sin=CSV.StirringInfoName,
                                       fmn=CSV.FeedingMaterialName)
                    # Update path variable
                    path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                     CSV.TempHeaterName[i])
                # Register temperature value
                CSV.LOG(f=path, header='Date,Heater Temperature',
                        v1=Reactor.HeaterTemp[i])
                # ----------------------------------------------------------

                # ------ LOG Stirring info ---------------------------------
                path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder,
                                                 i + 1, CSV.StirringInfoName[i])
                # Check if CSV file is older than 30 days or bigger than 10MB
                check = fileCheck(CSV.StirringInfoName[i], path, i)

                if check:  # If yes,
                    # DETLETE OLD FILE
                    # code to delete fileNam
                    #

                    # Update the file name from the Setup file
                    CSV.StirringInfoName[
                        i] = '{}-CSTR-{}-3.csv'.format(date, i + 1)
                    CSV.setup_CSVnames(f=CSV.SetupFile,
                                       trn=CSV.TempReactorName,
                                       thn=CSV.TempHeaterName,
                                       sin=CSV.StirringInfoName,
                                       fmn=CSV.FeedingMaterialName)
                    # Update path variable
                    path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i + 1,
                                                     CSV.StirringInfoName[i])
                CSV.LOG(f=path, header='Date,RPM,ON,OFF', v1=Reactor.RPM[
                        i], v2=Reactor.TimeOn[i], v3=Reactor.TimeOff[i])
                # -----------------------------------------------------------

    MinuteLoopTimer = Timer(10, DataLogger)  # Save data every 30 mins
    MinuteLoopTimer.daemon = True
    MinuteLoopTimer.start()  # Restart Timer
# ------------------------------------------------------------


# Check if the file is older than 30 days or bigger than 10 MB
# Return True when the file is older than 30 days OR bigger than 10 MB
def fileCheck(fileName, path, reactor):

    # get how old the file is
    date = fileName[0:10]  # CVS's date (dd-mm-yyyy)
    delta = datetime.now() - datetime.strptime(date, '%Y-%m-%d')
    age = delta.days

    # get size of file
    statinfo = os.stat(path)
    size = statinfo.st_size  # output in bytes

    # Condition evaluation
    if age > 30 or size > 30 * 1_000_000:
        return True
    else:
        return False
# ------------------------------------------------------------


# Get the OP value in (0-100%), input SP,PV
def PIDfunct():
    op = [0] * 6

    if Reactor.Enable[0] and ard.run is True:
        print('Controlling')
        op[0] = pid1(Reactor.PV[0])
    if Reactor.Enable[1]and ard.run is True:
        op[1] = pid2(Reactor.PV[1])
    if Reactor.Enable[2]and ard.run is True:
        op[2] = pid3(Reactor.PV[2])
    if Reactor.Enable[3]and ard.run is True:
        op[3] = pid4(Reactor.PV[3])
    if Reactor.Enable[4]and ard.run is True:
        op[4] = pid5(Reactor.PV[4])
    if Reactor.Enable[5]and ard.run is True:
        op[5] = pid6(Reactor.PV[5])
    return op
# ------------------------------------------------------------


# Returns a text from bool variable
def BoolToText(bool, T='True', F='False'):
    if bool:
        return T
    else:
        return F
# ------------------------------------------------------------


# ---- Function commands of GUI objects ------------------------------------
def _spinSP():
    Reactor.SP[selReact] = int(GUI_TargetTemp_Value.get())

    # Change setpoint of the corresponding PID
    if selReact == 0:
        pid1.setpoint = Reactor.SP[selReact]
    if selReact == 1:
        pid2.setpoint = Reactor.SP[selReact]
    if selReact == 2:
        pid2.setpoint = Reactor.SP[selReact]
    if selReact == 3:
        pid4.setpoint = Reactor.SP[selReact]
    if selReact == 4:
        pid5.setpoint = Reactor.SP[selReact]
    if selReact == 5:
        pid6.setpoint = Reactor.SP[selReact]

    print('Reactor{}, SP changed'.format(selReact))


def _spinOn():
    Reactor.TimeOn[selReact] = int(GUI_On_Value.get())
    print('Reactor{}, TimerOn changed', format(selReact))


def _spinOff():
    Reactor.TimeOff[selReact] = int(GUI_Off_Value.get())
    print('Reactor{}, TimerOff changed', format(selReact))


def _spinRPM():

    Reactor.RPM[selReact] = GUI_Rpm_Value.get()
    print('Reactor', selReact + 1, 'changed to', Reactor.RPM[selReact], 'RPMs')


def _SerialPortChange():
    global com
    com = GUI_SerialPortValue.get()
    print('Serial Port changed')

    return True

# When the Enable/Disable button is pressed


def _EnableClick():

    # (Enable/Disable) Reactor
    Reactor.Enable[selReact] = not Reactor.Enable[selReact]
    print('Reactor,', selReact + 1, 'is', Reactor.Enable[selReact])

    # When Reactor changed from 'Disabled' to 'Enabled':
    if Reactor.Enable[selReact] is True:
        Reactor.ThermalProtect[selReact] = False  # Deactivate thermal alarm

    GUI_EntriesUpdate()  # update input elements in GUI
    GuiOutputUpdate()  # update labels in GUI

# -----------------------------------------------------------------------------


def _FeedMaterial():
    date = datetime.strftime(datetime.now(), '%Y-%m-%d')

    Amount = GUI_Qty_value.get()
    Unit = GUI_Unit_value.get()
    Material = GUI_Material_value.get()

    # if all the elements are filled in , then the feed material is going to be saved
    if (Amount is not '' and Unit is not '' and Material is not ''):

        # -- LOG Feed Material ----------------------------------------------------
        # Get pat of Feerinf material CSV file
        path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder,
                                         selReact + 1, CSV.FeedingMaterialName[selReact])

        # - Verify if CSV file is older than 30 days or bigger than 10MB
        check = fileCheck(CSV.FeedingMaterialName[selReact], path, selReact)
        if check:  # if the file is older or longer than 10MB,

            # DETLETE OLD FILE

            # Create name for new file
            CSV.FeedingMaterialName[
                selReact] = '{}-CSTR-{}-4.csv'.format(date, selReact + 1)

            # Update the name in the Setup.csv file
            CSV.setup_CSVnames(f=CSV.SetupFile, trn=CSV.TempReactorName, thn=CSV.TempHeaterName,
                               sin=CSV.StirringInfoName, fmn=CSV.FeedingMaterialName)
            # Update path
            path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder,
                                             selReact + 1, CSV.StirringInfoName[selReact])

        # Save data in CSV file
        CSV.LOG(f=path, header='Date,Qty,Unit,Material',
                v1=GUI_Qty_value.get(),
                v2=GUI_Unit_value.get(),
                v3=GUI_Material_value.get())
        # --------------------------------------------------------------------------

        # Display confirmation message and clear feed material objects
        messagebox.showinfo(title='Feeding material', message='Feed material entered')
    else:
        messagebox.showerror(title='Feeding material', message='The information is not complete')
    GUI_Qty_value.delete(0, 'end')
    GUI_Unit_value.delete(0, 'end')
    GUI_Material_value.delete(0, 'end')
    print('Material fed')


def _PIDWindow():
    print('PID CONFIG')
    print(' ')

    top = Toplevel()

    top.title('PID Parameters Reactor ' + str(selReact + 1))
    top.geometry('{}x{}+{}+{}'.format(int(w/2), int(h/1.4), GUI_Main_Window.winfo_x() + int(w / 2),
                                      GUI_Main_Window.winfo_y() + int(h/2)))

    label = Label(top, text='PID \n TUNNING PARAMETERS', bg='DarkBlue', fg='white', font=('Calibri', 15),
                  justify='center', bd='2')
    label.place(relx=0.115, rely=0.1, relwidth=0.81, relheight=0.2)

    GUI_Pid_ButtonFrame = Frame(top, bg='black', bd=2)
    GUI_Pid_ButtonFrame.place(relx=0.115, rely=0.32, relwidth=0.397, relheight=0.3)

    GUI_Pid_ButtonFrame1 = Frame(top, bg='black', bd=2)
    GUI_Pid_ButtonFrame1.place(relx=0.53, rely=0.32, relwidth=0.397, relheight=0.3)

    img = Imagetk.PhotoImage(Image.open('pid.jpg'))
    panel = Label(GUI_Pid_ButtonFrame1, image=img)
    panel.pack(side='bottom', fill='both')

    GUI_Pid_ButtonFrame2 = Frame(top, bg='black', bd=2)
    GUI_Pid_ButtonFrame2.place(relx=0.115, rely=0.65, relwidth=0.81, relheight=0.3)

    # P value
    label1 = Label(GUI_Pid_ButtonFrame, text='Kp', bg='grey')
    label1.place(relx=0.05, rely=0.1, relwidth=0.2, relheight=0.2)
    PID_PValue = Entry(GUI_Pid_ButtonFrame, fg='green')
    PID_PValue.place(relx=0.29, rely=0.1, relwidth=0.45, relheight=0.2)
    PID_PValue.insert(0, Reactor.Kp[selReact])

    # I value
    label2 = Label(GUI_Pid_ButtonFrame, text='Ki', bg='grey')
    label2.place(relx=0.05, rely=0.35, relwidth=0.2, relheight=0.2)
    PID_IValue = Entry(GUI_Pid_ButtonFrame, fg='green')
    PID_IValue.place(relx=0.29, rely=0.35, relwidth=0.45, relheight=0.2)
    PID_IValue.insert(0, Reactor.Ki[selReact])

    # D value
    label3 = Label(GUI_Pid_ButtonFrame, text='Kd', bg='grey')
    label3.place(relx=0.05, rely=0.6, relwidth=0.2, relheight=0.2)
    PID_DValue = Entry(GUI_Pid_ButtonFrame, text=Reactor.Kd[selReact], fg='green')
    PID_DValue.insert(0, Reactor.Kd[selReact])
    PID_DValue.place(relx=0.29, rely=0.6, relwidth=0.45, relheight=0.2)

    def enter_btn():
        Reactor.Kp[selReact] = PID_PValue.get()
        Reactor.Ki[selReact] = PID_IValue.get()
        Reactor.Kd[selReact] = PID_DValue.get()
        print('PID PARAMETERS CHANGED')
        top.destroy()
        top.update()

    # Enter button
    PID_EnterButton = Button(GUI_Pid_ButtonFrame, text='Enter', command=enter_btn)
    PID_EnterButton.pack(side='right')

    figure1 = plt.Figure(figsize=(5, 2), dpi=80)
    figure1.add_subplot(111).plot(Reactor.SP[i], 'r--', linewidth=2, label='Set Point')
    canvas = FigureCanvasTkAgg(figure1, GUI_Pid_ButtonFrame2)
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    top.mainloop()


def _ChangeReactor(r=0):
    global selReact
    selReact = r

    print('Reactor {0} selected'.format(selReact + 1))

    GUI_EntriesUpdate()
    GuiOutputUpdate()
    UpdatePlot(days=selRange, ax=ax)


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

        GUI_24HourButton.configure(bg=RGB_Graph_b1, relief='sunken')
        GUI_WeekButton.configure(bg=RGB_Graph_b2, relief='raised')
        GUI_MonthButton.configure(bg=RGB_Graph_b2, relief='raised')
        GraphTitle = 'Hour Rate'  # Title of the graph
        xlabel = 'Last 24 hours'  # set the x axis label
        rate = '360min'
        rate = '1min'

    if selRange == 7:
        # desiredRange=datetime.timedelta(days=7) #obtain date for last 24 hrs

        GUI_24HourButton.configure(bg=RGB_Graph_b2, relief='raised')
        GUI_WeekButton.configure(bg=RGB_Graph_b1, relief='sunken')
        GUI_MonthButton.configure(bg=RGB_Graph_b2, relief='raised')
        GraphTitle = 'Week Rate'  # Title of the graph
        xlabel = 'Last 7 days'  # set the x axis label
        rate = '12h'

    if selRange == 32:
        # desiredRange=datetime.timedelta(days=32) #obtain date for last 24 hrs

        GUI_24HourButton.configure(bg=RGB_Graph_b2, relief='raised')
        GUI_WeekButton.configure(bg=RGB_Graph_b2, relief='groove')
        GUI_MonthButton.configure(bg=RGB_Graph_b1, relief='raised')
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
# ----------------------------------------------------------------------------


# ----- INITIAL CODE --------------------------------------------------------
A = ard.ArdConnect(com)
if ard.run:
    ard.ArdSetup(A)
# ---------------------------------------------------------------------------


# ---- GUI CODE ------------------------------------------------------------

# Selected reactor to be displayed
selReact = 0
# Selected range to be ploted
selRange = 1

# Color formats
RGB_LeftBar_DarkBlue = '#{:02X}{:02X}{:02X}'.format(0, 0, 140)
RGB_LeftBar_MidBlue = '#{:02X}{:02X}{:02X}'.format(82, 136, 174)
RGB_LeftBar_LightBlue = '#{:02X}{:02X}{:02X}'.format(199, 214, 221)
#
RGB_Temperature_title = '#{:02X}{:02X}{:02X}'.format(27, 61, 88)
RGB_Stirring_title = '#{:02X}{:02X}{:02X}'.format(27, 124, 41)
RGB_Feeding_title = '#{:02X}{:02X}{:02X}'.format(242, 208, 1)
RGB_Enable = '#{:02X}{:02X}{:02X}'.format(41, 75, 187)
RGB_Disabled = '#{:02X}{:02X}{:02X}'.format(198, 198, 198)
#
RGB_Sections_bg = '#{:02X}{:02X}{:02X}'.format(235, 236, 232)
RGB_Sections_bg = '#{:02X}{:02X}{:02X}'.format(230, 230, 230)
#
RGB_Stirring_ON = '#{:02X}{:02X}{:02X}'.format(60, 255, 108)
RGB_Stirring_OFF = '#{:02X}{:02X}{:02X}'.format(0, 85, 15)
#
RGB_Graph_b1 = '#{:02X}{:02X}{:02X}'.format(181, 197, 196)
RGB_Graph_b2 = '#{:02X}{:02X}{:02X}'.format(237, 241, 244)


# Main Window
GUI_Main_Window = tk.Tk()

# get screen width and height
sw = GUI_Main_Window.winfo_screenwidth()  # width of the screen
sh = GUI_Main_Window.winfo_screenheight()  # height of the screen
GUI_Main_Window.title('CSRT Reactors control')
# GUI_Main_Window.iconbitmap()

# Main window size and zoom
z = 1   # Main window zoom
w = int(sw * z) - 70  # width for the Tk root
h = int(sh * z) - 70  # height for the Tk root
zl = 1.5 * z  # Font zoom

# Font config
font_name = 'calibri'
font_small = (font_name, int(10 * zl))   			# Small
font_small_bold = (font_name, int(10 * zl), 'bold')   # Smallbold
font_medium = (font_name, int(12 * zl))				# medium
font_big = (font_name, int(32 * zl))  # big


# Calculate x and y coordinates to center the Main window
x = (sw / 2) - (w / 2)
y = (sh / 2) - (h / 2)
# Configurate size and position of Main window
# GUI_Main_Window.geometry('%dx%d+%d+%d' % (w, h, x, 0))
# GUI_Main_Window.configure(bg='RED')
GUI_Main_Window.resizable(0, 0)
GUI_Main_Window.state('zoomed')


# ----- Left section of GUI  -------------------------------
GUI_Selection_Area = tk.Canvas(GUI_Main_Window,
                               bg=RGB_LeftBar_DarkBlue, highlightthickness=0)
GUI_Selection_Area.place(relx=0, rely=0, relwidth=0.2, relheight=1)
# Date info
GUI_Clock = tk.Label(GUI_Selection_Area,
                     bg='blue', fg='white',
                     font=font_small_bold)
GUI_Clock.place(relx=0.01, rely=0.03, relwidth=1 - 0.02, relheight=0.065)
# # -- Column of buttons
GUI_ReactorButtons = [0] * no_reactors
for i in rng:
    GUI_ReactorButtons[i] = tk.Button(GUI_Selection_Area,
                                      text=Reactor.Name[i],
                                      bg=RGB_LeftBar_LightBlue,
                                      font=font_medium,
                                      command=partial(_ChangeReactor, i))
    GUI_ReactorButtons[i].place(relx=0, rely=(4+i)*(1/15),
                                relwidth=1, relheight=1/15)
#GUI_ReactorButtons[selReact].configure(bg=RGB_LeftBar_MidBlue, relief='sunken')
# --------------------------------------------------------------


# ----- Right main display Area -------------------------------
GUI_Display_Area = tk.Frame(GUI_Main_Window, bg='white', bd=2)
GUI_Display_Area.place(relx=0.2, rely=0,
                       relwidth=0.8, relheight=1)
#

# ------- Reactor frame --------------
GUI_Reactor_Frame = tk.Frame(GUI_Display_Area,
                             bg='white', bd=2, padx=5, pady=5,
                             relief='solid')
GUI_Reactor_Frame.place(relx=0.0, rely=0.025,
                        relwidth=1, relheight=0.4)


GUI_Reactor_Name = tk.Label(GUI_Reactor_Frame, text='Name',
                            bg='white', fg='black',
                            font=font_medium, anchor='w')
GUI_Reactor_Name.place(relx=0.0, rely=0.0,
                       relwidth=1, relheight=0.1)

GUI_Enable_Buttone = tk.Button(GUI_Reactor_Frame, text='EN/DIS',
                               bg='light blue', bd=1,
                               font=font_medium, command=_EnableClick)
GUI_Enable_Buttone.place(relx=0.8, rely=0.0,
                         relwidth=0.2, relheight=0.1)

# ------- TEMPERATURE FRAME -----------------------------
# Frame
GUI_Temperature_Frame = tk.Frame(GUI_Reactor_Frame,
                                 bg=RGB_Sections_bg, bd=2, padx=5, pady=5,
                                 relief='solid')
GUI_Temperature_Frame.place(relx=0, rely=0.1,
                            relwidth=1 / 3, relheight=0.9)
# Temperature label
GUI_TempLabel = tk.Label(GUI_Temperature_Frame, text='Temperature',
                         bg=RGB_Temperature_title, fg='white',
                         font=font_medium, anchor='w')
GUI_TempLabel.place(relx=0, rely=0,
                    relwidth=1, relheight=0.14)
# Target temp. label
GUI_TargetTemp_Label = tk.Label(GUI_Temperature_Frame, text='Target',
                                bg=RGB_Sections_bg, fg='black',
                                font=font_small_bold, anchor='w', relief='groove')
GUI_TargetTemp_Label.place(relx=0, rely=0.15,
                           relwidth=0.5, relheight=0.15)
# Target temp. value
GUI_TargetTemp_Value = tk.Spinbox(GUI_Temperature_Frame, from_=20, to=50,
                                  fg='green', command=_spinSP, state='readonly',
                                  font=font_big, relief='solid')
GUI_TargetTemp_Value.place(relx=0, rely=0.3,
                           relwidth=0.3, relheight=0.25)
# Actual temp. label
GUI_ActualTemp_Label = tk.Label(GUI_Temperature_Frame, text='Actual',
                                bg=RGB_Sections_bg, fg='black',
                                font=font_small_bold, anchor='w', relief='groove')
GUI_ActualTemp_Label.place(relx=0.5, rely=0.15,
                           relwidth=0.5, relheight=0.15)
GUI_ActualTemp_Value = tk.Label(GUI_Temperature_Frame, text='x °C',
                                bg=RGB_Sections_bg, fg=RGB_Temperature_title,
                                font=font_big, anchor='w', relief='groove')
GUI_ActualTemp_Value.place(relx=0.5, rely=0.3,
                           relwidth=0.5, relheight=0.25)
# Heater power level
GUI_HeaterPower_Label = tk.Label(GUI_Temperature_Frame, text='Heating...',
                                 bg='white', fg='red', borderwidth=2,
                                 font=font_small, relief='groove',)
GUI_HeaterPower_Label.place(relx=0.45, rely=0.6, relwidth=0.5, relheight=0.15)
# Heater temperature sensor
GUI_HeaterTemp_Label = tk.Label(GUI_Temperature_Frame, text='Heater x°C',
                                bg=RGB_Sections_bg, fg='black',
                                font=font_small, anchor='w', relief='groove')
GUI_HeaterTemp_Label.place(relx=0.45, rely=0.85, relwidth=0.5, relheight=0.1)
# PID button
GUI_Pid_Button = tk.Button(GUI_Temperature_Frame, text='PID',
                           bg=RGB_Graph_b2,
                           font=font_small, command=_PIDWindow)
GUI_Pid_Button.place(relx=0.01, rely=1 - 0.15, relwidth=0.2, relheight=0.14)

# ------- STIRRING FRAME -----------------------------
# Frame
GUI_Stirring_Frame = tk.Frame(GUI_Reactor_Frame,
                              bg=RGB_Sections_bg, bd=2, padx=5, pady=5,
                              relief='solid')
GUI_Stirring_Frame.place(relx=1/3, rely=0.1,
                         relwidth=1 / 3, relheight=0.9)
# Stirring Label
GUI_Stirr_Label = tk.Label(GUI_Stirring_Frame, text='Stirring',
                           bg=RGB_Stirring_title, fg='white',
                           font=font_medium, anchor='w')
GUI_Stirr_Label.place(relx=0, rely=0,
                      relwidth=1, relheight=0.14)
# Duration label
GUI_Duration_Label = tk.Label(GUI_Stirring_Frame, text='Inteval duration (min)',
                              bg=RGB_Sections_bg, fg='black',
                              font=font_small_bold, anchor='w', relief='groove')
GUI_Duration_Label.place(relx=0, rely=0.15, relwidth=0.5, relheight=0.15)
# On time label
GUI_On_Label = tk.Label(GUI_Stirring_Frame, text='ON ',
                        bg=RGB_Sections_bg, fg='black',
                        font=font_small, anchor='e', relief='groove')
GUI_On_Label.place(relx=0, rely=0.3, relwidth=0.2, relheight=0.15)
# On time Value
GUI_On_Value = tk.Spinbox(GUI_Stirring_Frame, from_=1, to=60,
                          font=font_small, relief='solid')
GUI_On_Value.place(relx=0.2, rely=0.3, relwidth=0.2, relheight=0.15)
# Off time label
GUI_Off_Label = tk.Label(GUI_Stirring_Frame, text='OFF ',
                         bg=RGB_Sections_bg, fg='black',
                         font=font_small, anchor='e', relief='groove')
GUI_Off_Label.place(relx=0, rely=0.5, relwidth=0.2, relheight=0.15)
# Off time Value
GUI_Off_Value = tk.Spinbox(GUI_Stirring_Frame, from_=1, to=60,
                           font=font_small, state='readonly', relief='solid',
                           command=_spinOff)
GUI_Off_Value.place(relx=0.2, rely=0.5, relwidth=0.2, relheight=0.15)
#  Stirring Label
GUI_Rpm_Label = tk.Label(GUI_Stirring_Frame, text='RPM ',
                         bg=RGB_Sections_bg,
                         font=font_small, anchor='e', relief='groove')
GUI_Rpm_Label.place(relx=0.5, rely=0.3, relwidth=0.2, relheight=0.15)
# RPM Spinbox
GUI_Rpm_Value = tk.Spinbox(GUI_Stirring_Frame, values=(10, 20, 60),
                           font=font_small, state='readonly', relief='solid',
                           command=_spinRPM)
GUI_Rpm_Value.place(relx=0.7, rely=0.3, relwidth=0.2, relheight=0.15)
# Stirring State
GUI_StirrState_Label = tk.Label(GUI_Stirring_Frame, text='ON/OFF',
                                bg=RGB_Stirring_ON,
                                font=font_medium, relief='groove')
GUI_StirrState_Label.place(relx=0.25, rely=0.7, relwidth=0.55, relheight=0.2)
# Time counter
GUI_StirrTime_Label = tk.Label(GUI_Stirring_Frame, text='Time: 00.00.00',
                               bg=RGB_Sections_bg,
                               font=font_small, anchor='nw', relief='groove')
GUI_StirrTime_Label.place(relx=0.6, rely=0.9, relwidth=0.4, relheight=0.1)
#

# ------- Feeding Material FRAME -----------------------------
# Frame
GUI_FeedMat_Frame = tk.Frame(GUI_Reactor_Frame,
                             bg=RGB_Sections_bg, bd=2, padx=5, pady=5,
                             relief='solid')
GUI_FeedMat_Frame.place(relx=2/3, rely=0.1,
                        relwidth=1 / 3, relheight=0.9)

# Feed material Label
GUI_FeedMat_Label = tk.Label(GUI_FeedMat_Frame, text='Feeding Material',
                             bg=RGB_Feeding_title, fg='white',
                             font=font_medium, anchor='w')
GUI_FeedMat_Label.place(relx=0, rely=0,
                        relwidth=1, relheight=0.14)
# Amount label
GUI_Qty_Label = tk.Label(GUI_FeedMat_Frame, text='Qty',
                         bg=RGB_Sections_bg,  fg='black',
                         font=font_small_bold, anchor='w', relief='groove')
GUI_Qty_Label.place(relx=0.1, rely=0.2,
                    relwidth=0.15, relheight=0.15)
# Amount  value
GUI_Qty_value = tk.Entry(GUI_FeedMat_Frame, font=font_small)
GUI_Qty_value.place(relx=0.1, rely=0.35,
                    relwidth=0.15, relheight=0.14)
# Unit label
GUI_Unit_Label = tk.Label(GUI_FeedMat_Frame, text='Unit',
                          bg=RGB_Sections_bg, fg='black',
                          font=font_small_bold, anchor='w', relief='groove')
GUI_Unit_Label.place(relx=0.27, rely=0.2,
                     relwidth=0.2, relheight=0.15)
# Unit value
GUI_Unit_value = tk.Entry(GUI_FeedMat_Frame, font=font_small)
GUI_Unit_value.place(relx=0.27, rely=0.35,
                     relwidth=0.2, relheight=0.14)
# # - Feed material
GUI_Material_Label = tk.Label(GUI_FeedMat_Frame, text='Material',
                              fg='black', bg=RGB_Sections_bg,
                              font=font_small_bold, anchor='w', relief='groove')
GUI_Material_Label.place(relx=0.48, rely=0.2,
                         relwidth=0.4, relheight=0.15)
GUI_Material_value = tk.Entry(GUI_FeedMat_Frame, font=font_small)
GUI_Material_value.place(relx=0.48, rely=0.35,
                         relwidth=0.4, relheight=0.14)
# Enter button
GUI_Feed_button = tk.Button(GUI_FeedMat_Frame, text='Enter',
                            font=font_small, command=_FeedMaterial)
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
                           bg=RGB_Graph_b2, font=font_medium,
                           command=partial(UpdatePlot, days=7, ax=ax))
GUI_WeekButton.place(relx=1 - 0.15, rely=2 * (1 / 6),
                     relwidth=0.15, relheight=(1 / 6))
# Month button
GUI_MonthButton = tk.Button(GUI_Graph_Frame, text='Month',
                            bg=RGB_Graph_b2, font=font_medium,
                            command=partial(UpdatePlot, days=32, ax=ax))
GUI_MonthButton.place(relx=1 - 0.15, rely=3 * (1 / 6),
                      relwidth=0.15, relheight=(1 / 6))
#  Update button
GUI_UpdateButton = tk.Button(GUI_Graph_Frame, text='Update plot',
                             bg=RGB_Graph_b2,
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
                               font=font_small, anchor='w', relief='solid')
GUI_SerialPortLabel.place(relx=0, rely=0, relwidth=0.3, relheight=1)
# Serial port selection
GUI_SerialPortValue = tk.Spinbox(GUI_SerialPortLabel, values=serial_ports,
                                 bg='white', wrap=True,
                                 font=font_small, command=_SerialPortChange)
GUI_SerialPortValue.place(relx=0.15, rely=0, relwidth=0.4, relheight=1)
#  Connection state
GUI_StateInfo = tk.Label(GUI_SerialPortLabel, text='connection?',
                         bg='GRAY72',
                         font=font_small_bold)
GUI_StateInfo.place(relx=0.55, rely=0, relwidth=0.45, relheight=1)
# Thermal protection state
GUI_OverheatLabel = tk.Label(GUI_Status_Bar, text='Therm. protect:',
                             bg='GRAY72',
                             font=font_small, anchor='w', relief='solid')
GUI_OverheatLabel.place(relx=0.45, rely=0,
                        relwidth=0.55, relheight=1)
GUI_ErrorInfo = [0] * no_reactors
for i in rng:
    GUI_ErrorInfo[i] = tk.Label(GUI_OverheatLabel,
                                text='{} {}'.format('Reactor ', i + 1),
                                font=font_small, relief='groove')
    GUI_ErrorInfo[i].place(relx=(3 / 15) + (i * 2 / 15),
                           rely=0, relwidth=(2 / 15), relheight=1)
# # -----------------------------------------------------------------------


# ---- Object and Timer initialization ----------
UpdatePlot(selRange, ax)
StirrOnOff()
UpdateStatus()
DataLogger()
GUI_EntriesUpdate()
GuiOutputUpdate()
GUI_Main_Window.mainloop()
# ------------------------------------------------


# ---- CODE TO 'end' THE APPLICATION -------------------

# TURN MOTORS AND HEATERS OFF

# CSV changes in Setup csv file
for i in rng:
    CSV.SP[i] = Reactor.SP[i]
    CSV.TimeOn[i] = Reactor.TimeOn[i]
    CSV.TimeOff[i] = Reactor.TimeOff[i]
    CSV.RPM[i] = Reactor.RPM[i]
    CSV.Kp[i] = Reactor.Kp[i]
    CSV.Ki[i] = Reactor.Ki[i]
    CSV.Kd[i] = Reactor.Kd[i]
    CSV.Enable[i] = Reactor.Enable[i]
CSV.setup_set(f=CSV.SetupFile,
              SP=CSV.SP,
              TimeOn=CSV.TimeOn,
              TimeOff=CSV.TimeOff,
              RPM=CSV.RPM,
              Kp=CSV.Kp,
              Ki=CSV.Ki,
              Kd=CSV.Kd,
              COM=com,
              Enable=CSV.Enable)
# End python programm
print('APP CLOSED')
sys.exit()
# --------------------------------------------------------
