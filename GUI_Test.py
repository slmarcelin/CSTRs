import tkinter as tk
from tkinter import StringVar, IntVar, BooleanVar
import random
import Ard_CMDS as ard
import datetime
import time
from time import strftime,gmtime
from threading import Timer
import csv
import sys



## VARIABLES
#
ReactorName = ['Reactor 1', 'Reactor 2', 'Reactor 3', 'Reactor 4', 'Reactor 5', 'Reactor 6']
ReactorEnable = [1,1,1,1,1,1] # Reactor enabled/disabled
# Temperature
SP = [30,31,32,33,34,35]    # Desired temperature in °C
PV = [30,31,32,33,34,35]    # Sensor readding in °C
OP = [0,0,0,0,0,0]          # 0-100%
# Stirring 
TOn = [10,10,10,10,10,10]   # On time in segs
TOff = [5,5,5,5,5,5]  # Off time in segs
ActivTime=[0,0,0,0,0,0]    # Time when status changed
StirrStat = [0,0,0,1,1,1] # Status of stirring motor (ON/OFF)

LoopTimer = [0]



class Reactor(object):
    def __init__(self, Name, SP, TimeOn):
        self.Name = Name
        self.SP = SP
        self.PV = 0
        self.OP = 0
        self.TimeOn = TimeOn
        self.TimeOff = 10
        self.ActiveTime = 0
        self.StirrStat = False

Reactor = [Reactor(Name="Reactor 1", SP=35, TimeOn=10),
           Reactor(Name="Reactor 2", SP=36, TimeOn=10),
           Reactor(Name="Reactor 3", SP=37, TimeOn=10),
           Reactor(Name="Reactor 4", SP=38, TimeOn=10),
           Reactor(Name="Reactor 5", SP=39, TimeOn=10),
           Reactor(Name="Reactor 6", SP=40, TimeOn=10)]



SPP=[]
for i in range(0,6):
    SPP.append (Reactor[i].SP)
print (SPP)




# Arduino PINS

run=0
######################################


def ToggleStirr():

    for i in range(0,6):
        if StirrStat[i]: #Stirring is on
            if (Reactor[i].ActiveTime + Reactor[i].TimeOn <= time.time()): # if it is time to turn off then                
                Reactor[i].StirrStat= not Reactor[i].StirrStat# turn off

                 Reactor[i].ActiveTime= time.time()# Save current time
        else: # stirr is off
            if ( Reactor[i].ActiveTime[i]+  Reactor[i].TimeOff <= time.time()):# if it is time to turn on then
                 Reactor[i].StirrStat= not  Reactor[i].StirrStat# turn on
                 Reactor[i].ActiveTime= time.time()# save current time

def UpdateLabels():
    global LoopTimer
    UpdateLabelsTimer=Timer(1,UpdateLabels)
    UpdateLabelsTimer.start()

    for i in range(0,6):
        TextVarPV[i].set( Reactor[i].PV)
        TextVarSP[i].set( Reactor[i].SP)
        TextVarOP[i].set( Reactor[i].OP)
        TextVarOP[i].set('Heating {:0.00f} %'.format( Reactor[i].OP))


        TextVarOnT[i].set( Reactor[i].TOn)
        TextVarOff[i].set( Reactor[i].TOff)
        TextVarStat[i].set(BoolToText( Reactor[i].StirrStat,'ON','OFF'))

        TextVarTime[i].set('{:00.0f}'.format(time.time()-  Reactor[i].ActiveTime))
        TextVarTime[i].set(strftime("%H:%M:%S", gmtime(time.time()-  Reactor[i].ActiveTime)))
     


def SecLoop():
    global A, PV,OP

    #Update PV,OP und Stirring motor status
    PV_temp = ard.GetTemperatures(A)
    if ard.run: #Arduino is connected
        PV=PV_temp
        for i in range(0,6)
            Reactor[i].PV= PV_temp[i]
            Reactor[i].OP= PIDfunct( Reactor[i].SP,  Reactor[i].PV)
        ToggleStirr()
    else:   #Arduino is not conected
        for i in range(0,6):
            Reactor[i].ActiveTime= time.time()
        A = ard.ArdConnect('COM10')
        ard.ArdSetup(A)

    ard.UpdateOutputs(A) #THIS IS TEMPORARY, MAKES LED BLINK
    LoopTimer=Timer(0.5, SecLoop)
    #LoopTimer.start()

def PIDfunct(sp,pv):
    op=[]

    K=0.01
    P=1
    d=1

    for i in range(0,6):
        op.append(  ((sp[i]-pv[i])*K)      )

    return op



def BoolToText(bool,T='True',F='False'):
    if bool: return T
    else: return F
def _spinSP():
    global SP
    for i in range(0,6):
        SP[i]=int(SpValue[i].get())
    print('SP: ',SP)
def _spinOnt():
    global TOn
    for i in range(0,6):
        TOn[i]=int(OnValue[i].get())
    print('TOn: ',TOn)
def _spinOfft():
    global TOff
    for i in range(0,6):
        TOff[i]=int(OffValue[i].get())
    print('TOff: ',TOff)
def _NameChange(event=None):
    global ReactorName
    for i in range(0,6):
        ReactorName[i]=label[i].get()
    print('Names: ',ReactorName)

def EnClick(r=1):
    print(r)


## INIT CODE

global A
A = ard.ArdConnect('COM10')
ard.ArdSetup(A)

LoopTimer=Timer(1, SecLoop)
#LoopTimer.start()

 # Stirring timers
for i in range(0, 6):
    ActivTime[i]=time.time();

#####################






### GUI CODE ###

# Main Window
root = tk.Tk()
root.geometry("1200x860")
root.resizable(0,0)

# Frame with the reactors
HEIGHT = 86
WIDTH = 155
z=1.5    #ZOOM


Space = tk.Canvas(root, bg="Blue",height='{:0.0f}m'.format(HEIGHT*z),width='{:0.0f}m'.format(WIDTH*z) )
Space.pack()

#Color constants
_LightBlue = '#b3b3ff'  # Temperature area background
_LightBlue = '#AAAEE8'  # Temperature area background
_DarkBlue = "DarkBlue"
_LightLila = '#e6ccff'  # Stirring area background
_DarkLila = '#400080'
_LightRed = 'Darkyellow'
_DarkRed = 'DarkRed'
_LightGreen = 'Green'
_DarkGreen = 'Darkgreen'

# Objects of in the frame
Loopframe = [0]*6
label = [0]*6
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

 # Variable labels
TextVarName = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()]
TextVarSP = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()]
TextVarPV = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()] 
TextVarOP = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()] 

TextVarOnT = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()] 
TextVarOff = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()] 

TextVarStat = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()] 
TextVarTime = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()] 


i=0 # INDEX
for row in range(0, 3):  # 3 rows
    for col in range(0, 2):  # 2columns
        
        ## Reactor Frame
        Loopframe[i]= tk.Frame(Space, bg='Black', bd=2)
        Loopframe[i].place(relx=(col*(1/2)), rely=row*(1/3),relwidth=(1/2), relheight=(1/3))


        # Reactor Label
        label[i]=tk.Entry(Loopframe[i], textvariable=TextVarName[i], validate="focusout", validatecommand= _NameChange ,width=10, font=("Calibri", int(10*z)))
        label[i].insert(0, ReactorName[i])
        label[i].place(relx=0.0, rely=0.0, relwidth=1, relheight=0.15)
        # ENABLE/DISABLE Reactor
        EnButton[i]= tk.Button(Loopframe[i], text=BoolToText(ReactorEnable[i],'Enable','disable'), bd=1,bg='#9999ff', command=EnClick(i), font=("Calibri", int(9*z)), relief="solid")
        EnButton[i].place(relx=0.8, rely=0.0, relwidth=0.2, relheight=0.15)


        # Temperature FRAME
        TemperatureFrame[i]=tk.Frame(Loopframe[i], bg=_LightBlue)
        TemperatureFrame[i].place(relx=0, rely=0.15+0.01, relwidth=0.499, relheight=1-0.15-0.01)
        
        # Temperature label
        TemperatureLabel[i]=tk.Label(TemperatureFrame[i], text="Temperature", bg=_DarkBlue, fg="white", font=("Calibri", int(11*z),'bold'), anchor="w")
        TemperatureLabel[i].place(relx=0, rely=0, relwidth=1, relheight=0.14)
       
        #  SP Label
        SpLabel[i]= tk.Label(TemperatureFrame[i], text="SP", fg="black",bg=_LightBlue,  font=("Calibri", int(10*z), "bold"), anchor="w")
        SpLabel[i].place(relx=0, rely=0.15, relwidth=0.15, relheight=0.15)
        SpValue[i]=tk.Spinbox(TemperatureFrame[i], from_=25, to=50, textvariable=TextVarSP[i], fg="green", command= _spinSP, font=("Calibri", int(15*z)), relief="solid")
        SpValue[i].place(relx=0.02, rely=0.35, relwidth=0.3, relheight=0.4)
        
        # Pv
        PvLabel[i]=tk.Label(TemperatureFrame[i], text='PV',  fg="black",bg=_LightBlue,  font=("Calibri", int(10*z), "bold"), anchor="w")
        PvLabel[i].place(relx=0.4, rely=0.15, relwidth=0.15, relheight=0.15)
        PvValue[i]=tk.Label(TemperatureFrame[i], textvariable=TextVarPV[i], fg=_DarkBlue ,bg=_LightBlue,  font=("Calibri", int(28*z), "bold"), anchor="w")
        PvValue[i].place(relx=0.5, rely=0.3, relwidth=0.6, relheight=0.4)
        
        # Heating Status
        OpLabel[i]=tk.Label(TemperatureFrame[i], textvariable= TextVarOP[i],   fg="red", font=("Calibri", int(10*z)))
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
        OnValue[i]=tk.Spinbox(StirringFrame[i], from_=1, to=60, textvariable=TextVarOnT[i], fg="black", command= _spinOnt, font=("Calibri", int(13*z)), relief="solid")
        OnValue[i].place(relx=0.2, rely=0.3, relwidth=0.25, relheight=0.3)

        # Off time label
        OffLabel[i]=tk.Label(StirringFrame[i], text="OFF",  fg="black", bg=_LightLila,  font=("Calibri", int(9*z), "bold"), anchor="w")
        OffLabel[i].place(relx=0.0, rely=0.35+0.3, relwidth=0.2, relheight=0.3)
        OffValue[i]=tk.Spinbox(StirringFrame[i], textvariable= TextVarOff[i], values=(1, 5, 10, 15, 30, 60),command=_spinOfft, fg="black",  font=("Calibri", int(13*z)), relief="solid")
        OffValue[i].place(relx=0.2, rely=0.35+0.3, relwidth=0.2, relheight=0.3)

        # Stirring Status
        StirrStatLabel[i]=tk.Label(StirringFrame[i], textvariable=TextVarStat[i], fg='#009900', bg='#66ff66', font=("Calibri", int(15*z), "bold"))
        StirrStatLabel[i].place(relx=0.55, rely=0.4, relwidth=0.35, relheight=0.35)

        TimeLeft[i]=tk.Label(StirringFrame[i], textvariable=TextVarTime[i],  fg='black', bg=_LightLila, font=("Calibri", int(9*z), "bold"),anchor='w')
        TimeLeft[i].place(relx=0.55, rely=0.8, relwidth=0.45, relheight=0.15)
        

        i=i+1
        if i==5:
            UpdateLabels()

root.mainloop()


#End timmers
UpdateLabelsTimer.cancel()






sys.exit()




