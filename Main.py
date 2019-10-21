#!/usr/bin/python3
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
import CSV_funct as save
import ARD_funct as ard
from threading import Timer
from functools import partial
from time import strftime, gmtime
import random
import datetime
import time
import sys
from pathlib import Path
 


#### VARIABLES
class Reactor(object):
    def __init__(self, Name, SP, TimeOn,TimeOff, StirrStatus):
        self.Name = Name
        self.Enable = True
        # Temperature
        self.SP = SP            # Desired temperature in °C
        self.PV = 0             # Sensor readding in °C
        self.OP = 0             # 0-100%
        # Stirring
        self.TimeOn = TimeOn    # On time in segs
        self.TimeOff = TimeOff       # Off time in segs
        self.ActiveTime = time.time()  # Time when status changed
        self.StirrStatus = StirrStatus  

dir= '{}{}'.format(Path(__file__).parent.absolute(),'\SETUP_.csv')
save.config_read(dir) # GET VALUES FROM CSV
Reactor = [Reactor(Name="Reactor 1", SP=save.SP[0], TimeOn=save.TimeOn[0], TimeOff=save.TimeOff[0], StirrStatus=0),
           Reactor(Name="Reactor 2", SP=save.SP[1], TimeOn=save.TimeOn[1], TimeOff=save.TimeOff[1], StirrStatus=0),
           Reactor(Name="Reactor 3", SP=save.SP[2], TimeOn=save.TimeOn[2], TimeOff=save.TimeOff[2], StirrStatus=0),
           Reactor(Name="Reactor 4", SP=save.SP[3], TimeOn=save.TimeOn[3], TimeOff=save.TimeOff[3], StirrStatus=1),
           Reactor(Name="Reactor 5", SP=save.SP[4], TimeOn=save.TimeOn[4], TimeOff=save.TimeOff[4], StirrStatus=1),
           Reactor(Name="Reactor 6", SP=save.SP[5], TimeOn=save.TimeOn[5], TimeOff=save.TimeOff[5], StirrStatus=1)]


#### Arduino Serial port
com = save.COM # Port on which Arduino is connected
coms=[] #array of ports
coms.append(com)
# for Raspberry PI
coms.append('/dev/ttyACM1')
coms.append('/dev/ttyACM1')
coms.append('/dev/ttyACM2')
coms.append('/dev/ttyACM3')
coms.append('/dev/ttyUSB0')
coms.append('/dev/ttyUSB1')

rng = range(0,6)
run=0
######################################


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
def UpdateVarText():
    global UpdateVarTextTimer
    UpdateVarTextTimer=Timer(1,UpdateVarText)
    UpdateVarTextTimer.start()
    

    i = selReact
    TextVar.Name.set( Reactor[i].Name )
    TextVar.Enable.set( BoolToText(Reactor[selReact].Enable,'Enabled','Disabled'))
    TextVar.SP.set( Reactor[i].SP)
    TextVar.PV.set( '{} {}'.format(Reactor[i].PV, '°C') )
    TextVar.OP.set( 'Heating {:0.00f} %'.format(Reactor[i].OP) )

    TextVar.TimeOn.set( Reactor[i].TimeOn)
    TextVar.TimeOff.set( Reactor[i].TimeOff)

    TextVar.StirrStatus.set( BoolToText( Reactor[i].StirrStatus,"ON", "OFF") )
    TextVar.CurrTime.set( strftime("%H:%M:%S", gmtime(time.time()-  Reactor[i].ActiveTime)) )
    TextVar.InfoBar.set( BoolToText( ard.run,"ARDUINO IS CONNECTED", "NO CONNECTION") )
   
    #Color of ON/OFF stirring status
    if Reactor[selReact].StirrStatus:
        StirrStatLabel.configure(bg ='LightGreen')
    else:
        StirrStatLabel.configure(bg ='darkgreen')
    #Color of Enable button
    if Reactor[selReact].Enable:
        EnButton.configure(bg =Enabled_col)
    else:
        EnButton.configure(bg =Disabled_col)
def SecLoop():
    global A, LoopTimer

    #Update PV,OP und Stirring motor status

    PV_temp = ard.GetTemperatures(A)
    if not PV_temp == -1 : #Arduino is connected
        for i in rng:
            Reactor[i].PV= PV_temp[i]
            Reactor[i].OP= PIDfunct( int(Reactor[i].SP),  int(Reactor[i].PV))
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

    op = (sp- pv)

    return op
def BoolToText(bool,T='True',F='False'):
    if bool: return T
    else: return F
def _spinSP():
    Reactor[selReact].SP=int(SpValue.get())
    print('SP changed')
def _spinOnt():
    Reactor[selReact].TimeOn= int(OnValue.get())
    print('TimerOn changed')
def _spinOfft():
    Reactor[selReact].TimeOff= int(OffValue.get())
    print('TimerOff changed')
def _ChangeReactor(r=0):
    global selReact
    selReact = r

    print('Reactor {0} selected'.format(selReact+ 1) )

    for i in rng:
        SelButton[i].configure(bg= Unselected_col)
    SelButton[r].configure(bg= Selected_col)
    
    UpdateVarTextTimer.cancel()
    UpdateVarText()  
def _changeCom():
    global com
    com = TextVar.COM.get()
    print(com)
    print("COM CHANGED")
    return True
def _EnClick():
    toggle = not Reactor[selReact].Enable
    Reactor[selReact].Enable = toggle
    
    print('Reactor {} is {}'.format(selReact+1 ,BoolToText(toggle,"Enabled","Disabled")))
   
    UpdateVarTextTimer.cancel()
    UpdateVarText()



###### INIT CODE ########

global A
A = ard.ArdConnect(com)
ard.ArdSetup(A)

LoopTimer=Timer(1, SecLoop)
LoopTimer.start()

##############################



##### GUI CODE #####
#Color constants
Selected_col =  'steelblue'
Unselected_col = '#{:02X}{:02X}{:02X}'.format(180,200,220)  # Temperature area background
Enabled_col =  Selected_col 
Disabled_col = Unselected_col

# Frame with the reactors
z=1.6    #ZOOM
zl=1.6  *z #font zoom
HEIGHT = 100
WIDTH = 155

selReact = 0 # Selected reactor to be displayed

# Main Window
root = tk.Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("{}x{}".format(w, h))
root.configure(bg='black')
root.resizable(1,1)


class VarLabel(object):  #Variable text class
    def __init__(self):
        self.Name = StringVar()
        self.Enable = StringVar()
        self.SP = StringVar()
        self.PV = StringVar()
        self.OP = StringVar()

        self.TimeOn = StringVar()
        self.TimeOff = StringVar()
        self.StirrStatus = StringVar()
        self.CurrTime = StringVar()
        self.InfoBar = StringVar()
        self.COM =StringVar()

TextVar =  VarLabel() #Variable text object


# Space where the Reactor frame is
Space = tk.Canvas(root, bg="Blue",height='{}m'.format(int(HEIGHT*z)),width='{:0.0f}m'.format(WIDTH*z) )
Space.pack()


## Row of buttons
SelButton=[0]*6
for i in rng:
    SelButton[i]= tk.Button(Space, text= '{} {}'.format('Reactor ', i+1) , bg= Unselected_col, font=("Calibri", int(8*zl)),  command= partial(_ChangeReactor,i)) 
    SelButton[i].place(relx=i*(1/6), rely=0.0, relwidth=(1/6), relheight=0.15)
SelButton[selReact].configure(bg=Selected_col)
#

## Reactor Frame
Loopframe= tk.Frame(Space, bg='black', bd=2)
Loopframe.place(relx= 0, rely=0.15 ,relwidth=1 , relheight= 1- 0.05- (1/6))
# Reactor Label
NameLabel=tk.Label(Loopframe, textvariable=TextVar.Name ,width=10, font=("Calibri", int(10*zl)), anchor= 'w')
NameLabel.place(relx=0.0, rely=0.0, relwidth=1, relheight=0.1)
# ENABLE/DISABLE Reactor
EnButton= tk.Button(Loopframe, textvariable=TextVar.Enable, bd=1,bg='light blue', command= _EnClick, font=("Calibri", int(9*zl)), relief="solid")
EnButton.place(relx=0.8, rely=0.0, relwidth=0.2, relheight=0.1)


## Temperature FRAME
TemperatureFrame=tk.Frame(Loopframe, bg= 'lightsteelblue')
TemperatureFrame.place(relx=0, rely=0.11 , relwidth=0.599, relheight=1-0.15-0.01)
# Temperature label
TemperatureLabel=tk.Label(TemperatureFrame, text="Temperature", bg='DarkBlue', fg="white", font=("Calibri", int(11*zl),'bold'), anchor="w")
TemperatureLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# SP Label
SpLabel= tk.Label(TemperatureFrame, text="SP", fg="black",bg='lightsteelblue',  font=("Calibri", int(10*zl), "bold"), anchor="w")
SpLabel.place(relx=0, rely=0.15, relwidth=0.15, relheight=0.15)
SpValue=tk.Spinbox(TemperatureFrame, from_=25, to=50, textvariable=TextVar.SP, fg="green", command= _spinSP, font=("Calibri", int(25*zl)), relief="solid")
SpValue.place(relx=0.02, rely=0.35, relwidth=0.3, relheight=0.4)
# Pv
PvLabel=tk.Label(TemperatureFrame, text='PV',  fg="black",bg='lightsteelblue',  font=("Calibri", int(10*zl), "bold"), anchor="w")
PvLabel.place(relx=0.5, rely=0.15, relwidth=0.15, relheight=0.15)
PvValue=tk.Label(TemperatureFrame, textvariable=TextVar.PV,bg='lightsteelblue', fg='DarkBlue' ,  font=("Calibri", int(30*zl), "bold"), anchor="w")
PvValue.place(relx=0.5, rely=0.3, relwidth=0.6, relheight=0.25)
# OP Status
OpLabel=tk.Label(TemperatureFrame, textvariable= TextVar.OP,   fg="red", font=("Calibri", int(10*zl)))
OpLabel.place(relx=0.4, rely=0.6, relwidth=0.55, relheight=0.2)


## Stirring FRAME
StirringFrame=tk.Frame(Loopframe, bg= 'azure')
StirringFrame.place(relx=0.6,rely=0.11, relwidth=0.4, relheight=1-0.16)
# Stirring Label
StirringeLabel=tk.Label(StirringFrame, text="Stirring", bg='teal', fg="white", font=("Calibri", int(11*zl),'bold'), anchor="w")
StirringeLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# Duration label
DurationLabel=tk.Label(StirringFrame, text="Duration", fg="black",bg='azure',  font=("Calibri", int(10*zl), "bold"), anchor="w")
DurationLabel.place(relx=0, rely=0.15, relwidth=0.5, relheight=0.15)
# On time label
OnLabel=tk.Label(StirringFrame, text="ON" , fg="black" , bg='azure',  font=("Calibri", int(9*zl), "bold"), anchor="w")
OnLabel.place(relx=0.0, rely=0.3, relwidth=0.2, relheight=0.15)
OnValue=tk.Spinbox(StirringFrame, from_=1, to=60, textvariable=TextVar.TimeOn, fg="black", command= _spinOnt, font=("Calibri", int(15*zl)), relief="solid")
OnValue.place(relx=0.15, rely=0.3, relwidth=0.28, relheight=0.2)
# Off time label
OffLabel=tk.Label(StirringFrame, text="OFF", bg= 'azure' ,  font=("Calibri", int(9*zl), "bold"), anchor="w")
OffLabel.place(relx=0.4 +0.15, rely=0.3, relwidth=0.2, relheight=0.15)
OffValue=tk.Spinbox(StirringFrame, textvariable= TextVar.TimeOff, values=(1, 5, 10, 15, 30, 60),command=_spinOfft, bg= 'white', fg="black",  font=("Calibri", int(13*zl)), relief="solid")
OffValue.place(relx=0.4+ 0.3, rely=0.3, relwidth=0.28, relheight=0.2)
# Stirring Status
StirrStatLabel=tk.Label(StirringFrame, textvariable=TextVar.StirrStatus, bg= 'LightGreen', font=("Calibri", int(15*zl), "bold"))
StirrStatLabel.place(relx=0.25, rely=0.6, relwidth=0.55, relheight=0.2)
# Time counter
TimeLeft=tk.Label(StirringFrame, textvariable=TextVar.CurrTime, bg= 'azure', font=("Calibri", int(9*zl), "bold"),anchor='w')
TimeLeft.place(relx=0.55, rely=0.8, relwidth=0.45, relheight=0.15)


## Status Bar
InfoBarLabel=tk.Label(Space, textvariable=TextVar.InfoBar ,bg= 'DarkGray' , font=('Calibri ',int(8*zl)), anchor='e'  )
InfoBarLabel.place(relx=0.1, rely=1-0.07, relwidth=1- 0.1, relheight=0.07)
#SERIAL PORT
ComControl = tk.Spinbox(Space,textvariable=TextVar.COM, values=coms, bg= 'white', font=('Calibri ',int(5*zl)), command= _changeCom)
ComControl.place(relx=0.0, rely=1-0.07, relwidth=0.2, relheight=0.07)

UpdateVarText()

root.mainloop()


#### CODE TO FINISH THE PROGRAM ####

#End timmers
LoopTimer.cancel()
UpdateVarTextTimer.cancel()

#Save changes in Setup csv file
for i in rng:
    save.SP[i] = Reactor[i].SP
    save.TimeOn[i] = Reactor[i].TimeOn
    save.TimeOff[i] = Reactor[i].TimeOff
save.config_save(f=dir, SP=save.SP, TimeOn=save.TimeOn ,TimeOff=save.TimeOff, COM=com)

sys.exit()