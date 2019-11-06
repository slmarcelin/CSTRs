#!/usr/bin/python3
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
import CSV_funct as CSV
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
    def __init__(self, Name, SP, TimeOn,TimeOff, StirrStatus,HeaterTemp):
        self.Name = Name
        self.Enable = True
        # Temperature
        self.SP = SP            # Desired temperature in °C
        self.PV = 0             # Sensor readding in °C
        self.OP = 0             # 0-100%
        self.HeaterTemp= HeaterTemp
        # Stirring
        self.TimeOn = TimeOn    # On time in segs
        self.TimeOff = TimeOff       # Off time in segs
        self.ActiveTime = time.time()  # Time when status changed
        self.StirrStatus = StirrStatus  



dir= '{}\{}'.format(Path(__file__).parent.absolute(),'SETUP_.csv')

CSV.config_read(dir) # GET VALUES FROM CSV
Reactor = [Reactor(Name="Reactor 1", SP=CSV.SP[0], TimeOn=CSV.TimeOn[0], TimeOff=CSV.TimeOff[0], StirrStatus=0, HeaterTemp=0),
           Reactor(Name="Reactor 2", SP=CSV.SP[1], TimeOn=CSV.TimeOn[1], TimeOff=CSV.TimeOff[1], StirrStatus=0, HeaterTemp=0),
           Reactor(Name="Reactor 3", SP=CSV.SP[2], TimeOn=CSV.TimeOn[2], TimeOff=CSV.TimeOff[2], StirrStatus=0, HeaterTemp=0),
           Reactor(Name="Reactor 4", SP=CSV.SP[3], TimeOn=CSV.TimeOn[3], TimeOff=CSV.TimeOff[3], StirrStatus=1, HeaterTemp=0),
           Reactor(Name="Reactor 5", SP=CSV.SP[4], TimeOn=CSV.TimeOn[4], TimeOff=CSV.TimeOff[4], StirrStatus=1, HeaterTemp=0),
           Reactor(Name="Reactor 6", SP=CSV.SP[5], TimeOn=CSV.TimeOn[5], TimeOff=CSV.TimeOff[5], StirrStatus=1, HeaterTemp=0)]

Reactor[0].Name

#### Arduino Serial port
com = CSV.COM # Port on which Arduino is connected
coms=[] #array of ports
coms.append(com)
# for Raspberry PI
coms.append('COM13')
coms.append('/dev/ttyACM1')
coms.append('/dev/ttyACM1')
coms.append('/dev/ttyACM2')
coms.append('/dev/ttyACM3')
coms.append('/dev/ttyUSB0')
coms.append('/dev/ttyUSB1')

rng = range(0,6)
run=0
######################################


def StirrOnOff():

    for i in rng:
        if Reactor[i].StirrStatus: #Stirring is on
            if (Reactor[i].ActiveTime + Reactor[i].TimeOn <= time.time()): # if it is time to turn off then                
                Reactor[i].StirrStatus= not Reactor[i].StirrStatus# turn off
                Reactor[i].ActiveTime= time.time()# CSV current time
        else: # stirr is off
            if ( Reactor[i].ActiveTime +  Reactor[i].TimeOff <= time.time()):# if it is time to turn on then
                 Reactor[i].StirrStatus= not  Reactor[i].StirrStatus# turn on
                 Reactor[i].ActiveTime= time.time()# CSV current time
        


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
    TextVar.HeaterTemp.set( 'Temp: {:0.00f} °C'.format(Reactor[i].HeaterTemp) )

    TextVar.TimeOn.set( Reactor[i].TimeOn)
    TextVar.TimeOff.set( Reactor[i].TimeOff)

    TextVar.StirrStatus.set( BoolToText( Reactor[i].StirrStatus,"ON", "OFF") )
    TextVar.CurrTime.set( strftime("%H:%M:%S", gmtime(time.time()-  Reactor[i].ActiveTime)) )
    TextVar.InfoBar.set( BoolToText( ard.run,"ARDUINO IS CONNECTED", "NO CONNECTION") )
   
    #Color of ON/OFF stirring status
    if Reactor[selReact].StirrStatus:
        GUI_StirrStatus.configure(bg =Stirring_on)
    else:
        GUI_StirrStatus.configure(bg =Stirring_off)
    #Color of Enable button
    if Reactor[selReact].Enable:
        GUI_ReactorEnable.configure(bg =Enabled_color)
    else:
        GUI_ReactorEnable.configure(bg =Disabled_color)

def SecondLoop():
    global A, SecondLoopTimer
    #Update PV,OP und Stirring motor status

    PV_temp = ard.ReadReactorTemp(A)
    if not PV_temp == -1 : #Arduino is connected
        for i in rng:
            Reactor[i].PV= PV_temp[i]
            Reactor[i].OP= PIDfunct( int(Reactor[i].SP),  int(Reactor[i].PV))
        #StirrOnOff()


    else:   #Arduino is not conected
        for i in rng:
            Reactor[i].ActiveTime= time.time()
        A = ard.ArdConnect(com)
        ard.ArdSetup(A)

    StirrOnOff()
    ##ard.UpdateOutputs(A) #THIS IS TEMPORARY, MAKES LED BLINK
    SecondLoopTimer=Timer(1, SecondLoop)
    SecondLoopTimer.start()

def MinuteLoop():
    global MinuteLoopTimer
    date = time.strftime("%Y-%m-%d", time.gmtime(time.time()))
    for i in rng:    
        ### LOG REACTOR TEMPERATURE
        csv_path= '{}\CSV\TEMPERATURE_REACTOR\LOG_{}.csv'.format(Path(__file__).parent.absolute(),i+1)
        CSV.LOG(csv_path , 'Date,Temperature', date, Reactor[i].PV )
       
        ### LOG HEATER TEMPERATURE
        csv_path= '{}\CSV\TEMPERATURE_HEATER\LOG_{}.csv'.format(Path(__file__).parent.absolute(),i+1)
        CSV.LOG(csv_path , 'Date,Temperature',date, Reactor[i].HeaterTemp )
       
        ### FEEDING METERIAL
        csv_path= '{}\CSV\FEEDING_MATERIAL\LOG_{}.csv'.format(Path(__file__).parent.absolute(),i+1)
        CSV.LOG(csv_path , 'Date,Qty,Unit,Material', date, i,i,i) 

    MinuteLoopTimer=Timer(2, MinuteLoop)
    MinuteLoopTimer.start()


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
    Reactor[selReact].SP=int(GUI_SpValue.get())
    print('SP changed')
def _spinOnt():
    Reactor[selReact].TimeOn= int(GUI_OnValue.get())
    print('TimerOn changed')
def _spinOfft():
    Reactor[selReact].TimeOff= int(GUI_OffValue.get())
    print('TimerOff changed')
def _ChangeReactor(r=0):
    global selReact
    selReact = r

    print('Reactor {0} selected'.format(selReact+ 1) )

    for i in rng:
        GUI_ReactorButtons[i].configure(bg= Unselected_color)
    GUI_ReactorButtons[r].configure(bg= Selected_color)
    
    UpdateVarTextTimer.cancel()
    UpdateVarText()  
def _changeCom():
    global com
    com = TextVar.COM.get()
    print(com)
    print("COM CHANGED")

    return True
def _EnableClick():
    toggle = not Reactor[selReact].Enable
    Reactor[selReact].Enable = toggle
    
    print('Reactor {} is {}'.format(selReact+1 ,BoolToText(toggle,"Enabled","Disabled")))
   
    UpdateVarTextTimer.cancel()
    UpdateVarText()
def _FeedMaterial():
    TextVar.FeedAmount.set('')
    TextVar.FeedMaterial.set('')
    TextVar.FeedUnit.set('')
    print('Material fed')
def _PIDConfig():
    print('PID CONFIG')



###### INIT CODE ########

global A
A = ard.ArdConnect(com)
ard.ArdSetup(A)

SecondLoopTimer=Timer(1, SecondLoop).start()
MinuteLoopTimer=Timer(1, MinuteLoop).start()




#################################################################################################
##### GUI CODE #####
#################################################################################################

#Color constants
Selected_color =  'steelblue'
Unselected_color = '#{:02X}{:02X}{:02X}'.format(180,200,220)  # Temperature area background
Enabled_color =  Selected_color 
Disabled_color = Unselected_color
Temperature_dark = 'DarkBlue'
Temperature_light = 'lightsteelblue'
Stirring_dark = 'teal'
Stirring_light = 'azure'
Stirring_on = 'LightGreen'
Stirring_off = 'DarkGreen'
Feeding_dark = 'gold'
Feeding_light = 'khaki'




# Main window size and zoom(temporary)
z=1    #ZOOM
zl=1.6  *z #font zoom
HEIGHT = 100
WIDTH = 200

selReact = 0 # Selected reactor to be displayed


# Main Window
GUI_window = tk.Tk()
w, h = GUI_window.winfo_screenwidth(), GUI_window.winfo_screenheight()
GUI_window.geometry('{}x{}'.format(w//2,h//2))
GUI_window.state("zoomed")
GUI_window.configure(bg='white')
GUI_window.resizable(1,1)

#This class contains all the variable texts used in the GUI objects
class VarLabel(object):  #Variable text class
    def __init__(self):
        self.Name = StringVar()
        self.Enable = StringVar()
        #Temperature Frame
        self.SP = StringVar()
        self.PV = StringVar()
        self.OP = StringVar()
        self.HeaterTemp = StringVar()
        #Stirring Frame
        self.TimeOn = StringVar()
        self.TimeOff = StringVar()
        self.StirrStatus = StringVar()
        self.CurrTime = StringVar()
        #Feeding Frame
        self.FeedAmount = StringVar()
        self.FeedMaterial = StringVar()
        self.FeedUnit = StringVar()
        #Bottom bar
        self.InfoBar = StringVar()
        self.COM =StringVar()
TextVar =  VarLabel() #Variable text object



# LEFT BAR with the reactor buttons
GUI_LeftPanelLeftBar = tk.Canvas(GUI_window, bg="blue4", height=(h//0.9), width=(w//10) )
GUI_LeftPanelLeftBar.pack(side=LEFT)



# Column of buttons
GUI_ReactorButtons=[0]*6
for i in rng:
    GUI_ReactorButtons[i]= tk.Button(GUI_LeftPanelLeftBar, text= '{} {}'.format('Reactor ', i+1) , bg= Unselected_color, font=("Calibri", int(8*zl))
                            ,relief=FLAT,command= partial(_ChangeReactor,i)) 
    GUI_ReactorButtons[i].place(x=0, y= (i*h/15)+(1*h/15) , relwidth=1, height= h/15  -5)
GUI_ReactorButtons[selReact].configure(bg=Selected_color)
#config button
GUI_ConfigButton= tk.Button(GUI_LeftPanelLeftBar, text= "Config" , bg= Unselected_color, font=("Calibri", int(8*zl))) 
GUI_ConfigButton.place(x=0, y=(9*h//15), relwidth=1, height= h//15 )



## Reactor Frame
GUI_ReactorFrame= tk.Frame(GUI_window, bg='black', bd=2)
GUI_ReactorFrame.place(x= (w//10)+20 ,y= (0*h//15)+20  ,width= 8*(w//10) , height= (h//3))
# Reactor Label
GUI_ReactorName=tk.Label(GUI_ReactorFrame, textvariable=TextVar.Name ,width=10, font=("Calibri", int(10*zl)), anchor= 'w')
GUI_ReactorName.place(relx=0.0, rely=0.0, relwidth=1, relheight=0.1)
# ENABLE/DISABLE Reactor
GUI_ReactorEnable= tk.Button(GUI_ReactorFrame, textvariable=TextVar.Enable, bd=1,bg='light blue', command= _EnableClick, font=("Calibri", int(9*zl)), relief="solid")
GUI_ReactorEnable.place(relx=0.8, rely=0.0, relwidth=0.2, relheight=0.1)



## Temperature FRAME
GUI_TempFrame=tk.Frame(GUI_ReactorFrame, bg= Temperature_light)
GUI_TempFrame.place(relx=0, rely=0.11 , relwidth=1/3, relheight=1-0.15-0.01)
# Temperature label
GUI_TempLabel=tk.Label(GUI_TempFrame, text="Temperature", bg=Temperature_dark, fg="white", font=("Calibri", int(11*zl),'bold'), anchor="w")
GUI_TempLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# SP Label
GUI_SpLabel= tk.Label(GUI_TempFrame, text="SP", fg="black",bg=Temperature_light,  font=("Calibri", int(10*zl), "bold"), anchor="w")
GUI_SpLabel.place(relx=0, rely=0.15, relwidth=0.15, relheight=0.15)
GUI_SpValue=tk.Spinbox(GUI_TempFrame, from_=25, to=50, textvariable=TextVar.SP, fg="green", command= _spinSP, font=("Calibri", int(25*zl)), relief="solid")
GUI_SpValue.place(relx=0.02, rely=0.3, relwidth=0.3, relheight=0.3)
# Pv
GUI_PvLabel=tk.Label(GUI_TempFrame, text='PV',  fg="black",bg=Temperature_light ,  font=("Calibri", int(10*zl), "bold"), anchor="w")
GUI_PvLabel.place(relx=0.5, rely=0.15, relwidth=0.15, relheight=0.15)
GUI_PvValue=tk.Label(GUI_TempFrame, textvariable=TextVar.PV,bg=Temperature_light, fg='DarkBlue' ,  font=("Calibri", int(30*zl), "bold"), anchor="w")
GUI_PvValue.place(relx=0.5, rely=0.3, relwidth=0.6, relheight=0.25)
# OP Status
GUI_OpLabel=tk.Label(GUI_TempFrame, textvariable= TextVar.OP,   fg="red", font=("Calibri", int(10*zl)))
GUI_OpLabel.place(relx=0.4, rely=0.6, relwidth=0.5, relheight=0.15)
# Heater temperature sensor
GUI_HeaterTemp=tk.Label(GUI_TempFrame, textvariable= TextVar.HeaterTemp, bg=Temperature_light, fg="black", font=("Calibri", int(10*zl)),anchor='w')
GUI_HeaterTemp.place(relx=0.4, rely=0.8, relwidth=0.55, relheight=0.2)
# PID parameters button
GUI_PID = tk.Button(GUI_TempFrame, text= "PID" , bg= Unselected_color, command=_PIDConfig, font=("Calibri", int(8*zl))) 
GUI_PID.place(relx=0.01, rely=1-0.15, relwidth=0.2, relheight=0.14)




## Stirring FRAME
GUI_StirrFrame=tk.Frame(GUI_ReactorFrame, bg= Stirring_light)
GUI_StirrFrame.place(relx=1/3+0.005,rely=0.11, relwidth=1/3-0.01, relheight=1-0.16)
# Stirring Label
GUI_StirrLabel=tk.Label(GUI_StirrFrame, text="Stirring", bg=Stirring_dark, fg="white", font=("Calibri", int(11*zl),'bold'), anchor="w")
GUI_StirrLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# Duration label
GUI_DurationLabel=tk.Label(GUI_StirrFrame, text="Duration", fg="black",bg=Stirring_light,  font=("Calibri", int(10*zl), "bold"), anchor="w")
GUI_DurationLabel.place(relx=0, rely=0.14, relwidth=0.5, relheight=0.1)
# On time label
GUI_OnLabel=tk.Label(GUI_StirrFrame, text="ON" , fg="black" , bg=Stirring_light,  font=("Calibri", int(9*zl), "bold"), anchor="w")
GUI_OnLabel.place(relx=0.0, rely=0.25, relwidth=0.2, relheight=0.15)
GUI_OnValue=tk.Spinbox(GUI_StirrFrame, from_=1, to=60, textvariable=TextVar.TimeOn, fg="black", command= _spinOnt, font=("Calibri", int(15*zl)), relief="solid")
GUI_OnValue.place(relx=0.15, rely=0.25, relwidth=0.28, relheight=0.15)
# Off time label
GUI_OffLabel=tk.Label(GUI_StirrFrame, text="OFF", bg= Stirring_light ,  font=("Calibri", int(9*zl), "bold"), anchor="w")
GUI_OffLabel.place(relx=0.4 +0.15, rely=0.25, relwidth=0.2, relheight=0.15)
GUI_OffValue=tk.Spinbox(GUI_StirrFrame, textvariable= TextVar.TimeOff, values=(1, 5, 10, 15, 30, 60),command=_spinOfft, bg= 'white', fg="black",  font=("Calibri", int(13*zl)), relief="solid")
GUI_OffValue.place(relx=0.4+ 0.3, rely=0.25, relwidth=0.28, relheight=0.15)
# Stirring RPM
GUI_RpmLabel=tk.Label(GUI_StirrFrame, text="RPM", bg= Stirring_light ,  font=("Calibri", int(9*zl), "bold"), anchor="w")
GUI_RpmLabel.place(relx=0.0, rely=0.45, relwidth=0.2, relheight=0.15)
GUI_RpmValue=tk.Spinbox(GUI_StirrFrame, textvariable= TextVar.TimeOff, values=(1, 5, 10, 15, 30, 60),command=_spinOfft, bg= 'white', fg="black",  font=("Calibri", int(13*zl)), relief="solid")
GUI_RpmValue.place(relx=0.2, rely=0.45, relwidth=0.28, relheight=0.15)
# Stirring Status
GUI_StirrStatus=tk.Label(GUI_StirrFrame, textvariable=TextVar.StirrStatus, bg= Stirring_on, font=("Calibri", int(15*zl), "bold"))
GUI_StirrStatus.place(relx=0.25, rely=0.7, relwidth=0.55, relheight=0.2)
# Time counter
GUI_StirrTime=tk.Label(GUI_StirrFrame, textvariable=TextVar.CurrTime, bg= Stirring_light, font=("Calibri", int(9*zl), "bold"),anchor='nw')
GUI_StirrTime.place(relx=0.55, rely=0.9, relwidth=0.45, relheight=0.15)



## Feeding Material FRAME
GUI_FeedFrame=tk.Frame(GUI_ReactorFrame, bg= Feeding_light)
GUI_FeedFrame.place(relx=2/3, rely=0.11, relwidth=1/3, relheight=1-0.16)
# Feeding Label
GUI_FeedLabel=tk.Label(GUI_FeedFrame, text="Feeding Material", bg=Feeding_dark, fg="white", font=("Calibri", int(11*zl),'bold'), anchor="w")
GUI_FeedLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# Amount of material
GUI_FeedAmountLabel=tk.Label(GUI_FeedFrame, text='Qty',  fg="black",bg=Feeding_light,  font=("Calibri", int(10*zl), "bold"), anchor="w")
GUI_FeedAmountLabel.place(relx=0.1, rely=0.2, relwidth=0.15, relheight=0.15)
GUI_FeedAmount= tk.Entry(GUI_FeedFrame, textvariable=TextVar.FeedAmount, font=("Calibri", int(9*zl), "bold"))
GUI_FeedAmount.place(relx=0.1, rely=0.35, relwidth=0.15, relheight=0.14)
# Unit of material
GUI_FeedUnitLabel=tk.Label(GUI_FeedFrame, text='Unit',  fg="black",bg=Feeding_light,  font=("Calibri", int(10*zl), "bold"), anchor="w")
GUI_FeedUnitLabel.place(relx=0.27, rely=0.2, relwidth=0.2, relheight=0.15)
GUI_FeedUnit= tk.Spinbox(GUI_FeedFrame, textvariable=TextVar.FeedUnit, font=("Calibri", int(9*zl), "bold"))
GUI_FeedUnit.place(relx=0.27, rely=0.35, relwidth=0.2, relheight=0.14)
# Feed material
GUI_FeedMaterialLabel=tk.Label(GUI_FeedFrame, text='Material',  fg="black",bg=Feeding_light,  font=("Calibri", int(10*zl), "bold"), anchor="w")
GUI_FeedMaterialLabel.place(relx=0.48, rely=0.2, relwidth=0.4, relheight=0.15)
GUI_FeedMaterialLabel= tk.Entry(GUI_FeedFrame, textvariable=TextVar.FeedMaterial, font=("Calibri", int(9*zl), "bold"))
GUI_FeedMaterialLabel.place(relx=0.48, rely=0.35, relwidth=0.4, relheight=0.14)
# Enter button
GUI_FeedInButton= tk.Button(GUI_FeedFrame, text= "Enter" , bg= Unselected_color, command=_FeedMaterial, font=("Calibri", int(8*zl))) 
GUI_FeedInButton.place(relx=0.1, rely=0.55, relwidth=1-0.2, relheight=0.14)



## Status Bar
GUI_BottomBar=tk.Label(GUI_window, textvariable=TextVar.InfoBar ,bg= 'DarkGray' , font=('Calibri ',int(8*zl)), anchor='e'  )
GUI_BottomBar.pack(side='bottom', fill='x' )
#SERIAL PORT
GUI_SerialPortLabel = tk.Label(GUI_BottomBar,text='PORT ',bg='DarkGray', font=('Calibri ',int(6*zl)))
GUI_SerialPortLabel.pack(side='left')
GUI_SerialPortValue = tk.Spinbox(GUI_BottomBar,textvariable=TextVar.COM, values=coms, bg= 'white', font=('Calibri ',int(8*zl)), command= _changeCom)
GUI_SerialPortValue.pack(side='left')


UpdateVarText()
GUI_window.mainloop()



#### CODE TO END THE PROGRAM ####
#End timmers
SecondLoopTimer.cancel()
MinuteLoopTimer.cancel()
UpdateVarTextTimer.cancel()

#CSV changes in Setup csv file
for i in rng:
    CSV.SP[i] = Reactor[i].SP
    CSV.TimeOn[i] = Reactor[i].TimeOn
    CSV.TimeOff[i] = Reactor[i].TimeOff
CSV.config_save(f=dir, SP=CSV.SP, TimeOn=CSV.TimeOn ,TimeOff=CSV.TimeOff, COM=com)

sys.exit()