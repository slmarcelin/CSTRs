import tkinter as tk
from tkinter import StringVar
import Ard_CMDS as ard
from threading import Timer
from time import strftime, gmtime
import random
import datetime
import time

import csv
import sys


#### VARIABLES
class Reactor(object):
    def __init__(self, Name, SP, TimeOn):
        self.Name = Name
        self.Enable = False
        # Temperature
        self.SP = SP            # Desired temperature in °C
        self.PV = 0             # Sensor readding in °C
        self.OP = 0             # 0-100%
        # Stirring
        self.TimeOn = TimeOn    # On time in segs
        self.TimeOff = 10       # Off time in segs
        self.ActiveTime = time.time()  # Time when status changed
        self.StirrStatus = False  

Reactor = [Reactor(Name="Reactor 1", SP=35, TimeOn=10),
           Reactor(Name="Reactor 2", SP=36, TimeOn=10),
           Reactor(Name="Reactor 3", SP=37, TimeOn=10),
           Reactor(Name="Reactor 4", SP=38, TimeOn=10),
           Reactor(Name="Reactor 5", SP=39, TimeOn=10),
           Reactor(Name="Reactor 6", SP=40, TimeOn=10)]
rng = range(0,6)

#### Arduino
com = 'COM15' # Port on which Arduino is connected
run=0
######################################



# This Function Changes the status of
# the stirring mechanism, according to
# the ON and OFF duration
def ToggleStirr():

    for i in rng:
        if Reactor[i].StirrStatus: #Stirring is on
            if (Reactor[i].ActiveTime + Reactor[i].TimeOn <= time.time()): # if it is time to turn off then                
                Reactor[i].StirrStatus= not Reactor[i].StirrStatus# turn off

                Reactor[i].ActiveTime= time.time()# Save current time
        else: # stirr is off
            if ( Reactor[i].ActiveTime +  Reactor[i].TimeOff <= time.time()):# if it is time to turn on then
                 Reactor[i].StirrStatus= not  Reactor[i].StirrStatus# turn on
                 Reactor[i].ActiveTime= time.time()# save current time

def UpdateLabels():
    global UpdateLabelsTimer
    UpdateLabelsTimer=Timer(1,UpdateLabels)
    UpdateLabelsTimer.start()

    for i in rng:
        Label[i].Change(Name = Reactor[i].Name,
                        SP = Reactor[i].SP,
                        PV = Reactor[i].PV,
                        OP = 'Heating {:0.00f} %'.format(Reactor[i].OP),

                        TimeOn = Reactor[i].TimeOn,
                        TimeOff = Reactor[i].TimeOff,
                        StirrStatus = BoolToText( Reactor[i].StirrStatus,"ON", "OFF"),
                        CurrTime = strftime("%H:%M:%S", gmtime(time.time()-  Reactor[i].ActiveTime)) )
                        #CurrTime = strftime("%H:%M:%S", gmtime(time.time()-  Reactor[i].ActiveTime)) )
     
def SecLoop():
    global A, LoopTimer

    #Update PV,OP und Stirring motor status
    PV_temp = ard.GetTemperatures(A)
    if not PV_temp == -1 : #Arduino is connected
        for i in rng:
            Reactor[i].PV= PV_temp[i]
            Reactor[i].OP= PIDfunct( Reactor[i].SP,  Reactor[i].PV)
        ToggleStirr()
    else:   #Arduino is not conected
        for i in rng:
            Reactor[i].ActiveTime= time.time()
        A = ard.ArdConnect(com)
        ard.ArdSetup(A)

    ard.UpdateOutputs(A) #THIS IS TEMPORARY, MAKES LED BLINK
    LoopTimer=Timer(0.5, SecLoop)
    LoopTimer.start()

def PIDfunct(sp,pv):
    op=[]

    K=0.01
    P=1
    d=1

    op = (sp- pv) * K

    return op

def BoolToText(bool,T='True',F='False'):
    if bool: return T
    else: return F

def _spinSP():
    for i in rng:
        Reactor[i].SP=int(SpValue[i].get())
    print('SP changed')

def _spinOnt():
    for i in rng:
        Reactor[i].TimeOn= int(OnValue[i].get())
    print('TimerOn changed')

def _spinOfft():
    for i in rng:
        Reactor[i].TimeOff= int(OffValue[i].get())
    print('TimerOff changed')

def _NameChange(event=None):
    for i in rng:
        print(NameLabel[i].get())
        Reactor[i].Name= "NameLabel[i].get()"
    print('Name changed')

def EnClick(r=1):
    print()


###### INIT CODE ########

global A
A = ard.ArdConnect(com)
ard.ArdSetup(A)

LoopTimer=Timer(1, SecLoop)
LoopTimer.start()

##############################



##### GUI CODE #####
# Frame with the reactors
HEIGHT = 86
WIDTH = 155
z=1.5    #ZOOM

# Main Window
root = tk.Tk()
root.geometry("1200x860")
root.resizable(0,0)

Space = tk.Canvas(root, bg="Blue",height='{:0.0f}m'.format(HEIGHT*z),width='{:0.0f}m'.format(WIDTH*z) )
Space.pack()

#Color constants
_LightBlue = '#AAAEE8'  # Temperature area background
_DarkBlue = "DarkBlue"
_LightLila = '#e6ccff'  # Stirring area background
_DarkLila = '#400080'
_LightRed = 'Darkyellow'
_DarkRed = 'DarkRed'
_LightGreen = 'pale green'
_DarkGreen = 'Darkgreen'

# Objects used in the window
Loopframe = [0]*6
NameLabel = [0]*6
EnButton = [0]*6
TemperatureFrame = [0]*6
TemperatureLabel = [0]*6
SpLabel = [0]*6
SpValue = [0]*6
PvLabel = [0]*6
PvValue = [0]*6
OpLabel = [0]*6
StirringFrame = [0]*6
StirringeLabel = [0]*6
DurationLabel = [0]*6
OnLabel = [0]*6
OnValue = [0]*6
OffLabel = [0]*6
OffValue = [0]*6
StirrStatLabel = [0]*6
TimeLeft = [0]*6

class VarLabel(object):
    def __init__(self):
        self.Name = StringVar()
        self.SP = StringVar()
        self.PV = StringVar()
        self.OP = StringVar()

        self.TimeOn = StringVar()
        self.TimeOff = StringVar()
        self.StirrStatus = StringVar()
        self.CurrTime = StringVar()

    def Change(self, Name=1, SP=1, PV=1, OP=1, TimeOn=1, TimeOff=1, StirrStatus=1, CurrTime=1):
        self.Name.set(Name)
        self.SP.set(SP)
        self.PV.set(PV)
        self.OP.set(OP)

        self.TimeOn.set( TimeOn)
        self.TimeOff.set(TimeOff)
        self.StirrStatus.set(StirrStatus)
        self.CurrTime.set(CurrTime)

Label = [ VarLabel(), VarLabel(), VarLabel(), VarLabel(), VarLabel(), VarLabel()]
UpdateLabels()

i=0 # INDEX
for row in range(0, 3):  # 3 rows
    for col in range(0, 2):  # 2columns
        
        ## Reactor Frame
        Loopframe[i]= tk.Frame(Space, bg='black', bd=2)
        Loopframe[i].place(relx=(col*(1/2)), rely=row*(1/3),relwidth=(1/2), relheight=(1/3))

        # Reactor Label
        NameLabel[i]=tk.Entry(Loopframe[i], validate="focusout", validatecommand= _NameChange ,width=10, font=("Calibri", int(10*z)))
        NameLabel[i].insert(0, Reactor[i].Name )
        NameLabel[i].place(relx=0.0, rely=0.0, relwidth=1, relheight=0.15)
        # ENABLE/DISABLE Reactor
        EnButton[i]= tk.Button(Loopframe[i], text=BoolToText(Reactor[i].Enable,'Enable','disable'), bd=1,bg='#9999ff', command=EnClick(i), font=("Calibri", int(9*z)), relief="solid")
        #EnButton[i].place(relx=0.8, rely=0.0, relwidth=0.2, relheight=0.15)


        # Temperature FRAME
        TemperatureFrame[i]=tk.Frame(Loopframe[i], bg=_LightBlue)
        TemperatureFrame[i].place(relx=0, rely=0.15+0.01, relwidth=0.499, relheight=1-0.15-0.01)
        
        # Temperature label
        TemperatureLabel[i]=tk.Label(TemperatureFrame[i], text="Temperature", bg=_DarkBlue, fg="white", font=("Calibri", int(11*z),'bold'), anchor="w")
        TemperatureLabel[i].place(relx=0, rely=0, relwidth=1, relheight=0.14)
       
        #  SP Label
        SpLabel[i]= tk.Label(TemperatureFrame[i], text="SP", fg="black",bg=_LightBlue,  font=("Calibri", int(10*z), "bold"), anchor="w")
        SpLabel[i].place(relx=0, rely=0.15, relwidth=0.15, relheight=0.15)
        SpValue[i]=tk.Spinbox(TemperatureFrame[i], from_=25, to=50, textvariable=Label[i].SP, fg="green", command= _spinSP, font=("Calibri", int(15*z)), relief="solid")
        SpValue[i].place(relx=0.02, rely=0.35, relwidth=0.3, relheight=0.4)
        
        # Pv
        PvLabel[i]=tk.Label(TemperatureFrame[i], text='PV',  fg="black",bg=_LightBlue,  font=("Calibri", int(10*z), "bold"), anchor="w")
        PvLabel[i].place(relx=0.4, rely=0.15, relwidth=0.15, relheight=0.15)
        PvValue[i]=tk.Label(TemperatureFrame[i], textvariable=Label[i].PV, fg=_DarkBlue ,bg=_LightBlue,  font=("Calibri", int(28*z), "bold"), anchor="w")
        PvValue[i].place(relx=0.5, rely=0.3, relwidth=0.6, relheight=0.4)
        
        # Heating Status
        OpLabel[i]=tk.Label(TemperatureFrame[i], textvariable= Label[i].OP,   fg="red", font=("Calibri", int(10*z)))
        OpLabel[i].place(relx=0.4, rely=0.7, relwidth=0.55, relheight=0.2)


        # Stirring FRAME
        StirringFrame[i]=tk.Frame(Loopframe[i], bg=_LightLila)
        StirringFrame[i].place(relx=0.5,rely=0.15+0.01, relwidth=0.5, relheight=1-0.16)
        
        # Stirring Label
        StirringeLabel[i]=tk.Label(StirringFrame[i], text="Stirring", bg=_DarkLila, fg="white", font=("Calibri", int(11*z),'bold'), anchor="w")
        StirringeLabel[i].place(relx=0, rely=0, relwidth=1, relheight=0.14)
        
        # Duration label
        DurationLabel[i]=tk.Label(StirringFrame[i], text="Duration", fg="black",bg=_LightLila,  font=("Calibri", int(10*z), "bold"), anchor="w")
        DurationLabel[i].place(relx=0, rely=0.15, relwidth=0.5, relheight=0.15)

        # On time label
        OnLabel[i]=tk.Label(StirringFrame[i], text="ON" , fg="black" , bg=_LightLila,  font=("Calibri", int(9*z), "bold"), anchor="w")
        OnLabel[i].place(relx=0.0, rely=0.3, relwidth=0.2, relheight=0.3)
        OnValue[i]=tk.Spinbox(StirringFrame[i], from_=1, to=60, textvariable=Label[i].TimeOn, fg="black", command= _spinOnt, font=("Calibri", int(13*z)), relief="solid")
        OnValue[i].place(relx=0.2, rely=0.3, relwidth=0.25, relheight=0.3)

        # Off time label
        OffLabel[i]=tk.Label(StirringFrame[i], text="OFF",  fg="black", bg=_LightLila,  font=("Calibri", int(9*z), "bold"), anchor="w")
        OffLabel[i].place(relx=0.0, rely=0.35+0.3, relwidth=0.2, relheight=0.3)
        OffValue[i]=tk.Spinbox(StirringFrame[i], textvariable= Label[i].TimeOff, values=(1, 5, 10, 15, 30, 60),command=_spinOfft, fg="black",  font=("Calibri", int(13*z)), relief="solid")
        OffValue[i].place(relx=0.2, rely=0.35+0.3, relwidth=0.25, relheight=0.3)

        # Stirring Status
        StirrStatLabel[i]=tk.Label(StirringFrame[i], textvariable=Label[i].StirrStatus, fg=_DarkGreen, bg=_LightGreen, font=("Calibri", int(15*z), "bold"))
        StirrStatLabel[i].place(relx=0.55, rely=0.4, relwidth=0.35, relheight=0.35)

        TimeLeft[i]=tk.Label(StirringFrame[i], textvariable=Label[i].CurrTime,  fg='black', bg=_LightLila, font=("Calibri", int(9*z), "bold"),anchor='w')
        TimeLeft[i].place(relx=0.55, rely=0.8, relwidth=0.45, relheight=0.15)
        i=i+1
root.mainloop()


#End timmers
LoopTimer.cancel()
UpdateLabelsTimer.cancel()
sys.exit()







