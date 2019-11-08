#!/usr/bin/python3

import CSV_funct as CSV
import ARD_funct as ard
import Panda_funct as Panda
#from tkinter.ttk import *
import tkinter as tk
from tkinter import *
from threading import Timer
from functools import partial
from time import strftime, gmtime
#import random
import datetime
import time
import sys
from pathlib import Path



# 
#from pandas import DataFrame
#import pandas as pd
#import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



#### REACTOR CLASS...
class Reactor(object):
	def __init__(self, Name, SP, TimeOn,TimeOff, RPM, StirrStatus,HeaterTemp):
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
		self.RPM = RPM
		self.ActiveTime = time.time()  # Time when status changed
		self.StirrStatus = StirrStatus  


### File Paths
def SetupDir(name):
	return '{}\{}\{}'.format(Path(__file__).parent.absolute(),'CSV',name)
def CsvDir(Reactor, Folder):
	return '{}\{}\Reactor ({})\{}\LOG_{}.csv'.format(Path(__file__).parent.absolute(),'CSV',Reactor+1,Folder,Reactor+1)
SetupFile= SetupDir('SETUP_.csv')



## GET VALUES FROM CSV & Create Reactor object
CSV.config_read(SetupFile) 
Reactor = [Reactor(Name="Reactor 1", SP=CSV.SP[0], TimeOn=CSV.TimeOn[0], TimeOff=CSV.TimeOff[0], RPM=CSV.RPM[0], StirrStatus=0, HeaterTemp=0),
		   Reactor(Name="Reactor 2", SP=CSV.SP[1], TimeOn=CSV.TimeOn[1], TimeOff=CSV.TimeOff[1], RPM=CSV.RPM[1], StirrStatus=0, HeaterTemp=0),
		   Reactor(Name="Reactor 3", SP=CSV.SP[2], TimeOn=CSV.TimeOn[2], TimeOff=CSV.TimeOff[2], RPM=CSV.RPM[2], StirrStatus=0, HeaterTemp=0),
		   Reactor(Name="Reactor 4", SP=CSV.SP[3], TimeOn=CSV.TimeOn[3], TimeOff=CSV.TimeOff[3], RPM=CSV.RPM[3], StirrStatus=1, HeaterTemp=0),
		   Reactor(Name="Reactor 5", SP=CSV.SP[4], TimeOn=CSV.TimeOn[4], TimeOff=CSV.TimeOff[4], RPM=CSV.RPM[4], StirrStatus=1, HeaterTemp=0),
		   Reactor(Name="Reactor 6", SP=CSV.SP[5], TimeOn=CSV.TimeOn[5], TimeOff=CSV.TimeOff[5], RPM=CSV.RPM[5], StirrStatus=1, HeaterTemp=0)]



#### Arduino Serial port
# Port in which Arduino is connected
com_arr = [] #array of ports
com = CSV.COM
com_arr.append(com) 
# for windows
com_arr.append('COM3')
com_arr.append('COM4')
com_arr.append('COM11')
com_arr.append('COM12')
com_arr.append('COM13')
com_arr.append('COM14')
com_arr.append('COM15')
# for Raspberry PI
com_arr.append('/dev/ttyACM1')
com_arr.append('/dev/ttyACM2')
com_arr.append('/dev/ttyACM3')
com_arr.append('/dev/ttyUSB0')
com_arr.append('/dev/ttyUSB1')

rng = range(0,6)
#########################################################################


## Control the status of the stirring motor
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

## Update the texts of the GUI objects
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
	TextVar.RPM.set( Reactor[i].RPM)

	TextVar.StirrStatus.set( BoolToText( Reactor[i].StirrStatus,"ON", "OFF") )
	TextVar.CurrTime.set( strftime("%H:%M:%S", gmtime(time.time()-  Reactor[i].ActiveTime)) )
	TextVar.InfoBar.set( BoolToText( ard.run,"ARDUINO IS CONNECTED", "ARDUINO IS NOT DETECTED") )
   
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

## This function is been called every second
def SecondLoop():
	global A, SecondLoopTimer


	###### Update PV,OP und Stirring motor status
	if ard.run :
		## GET READINGS Reactor Temperatures
		PV_temp = ard.ReadReactorTemp(A)
		Heater_temp = ard.ReadHeatherTemp(A)

	if ard.run :
		for i in rng:
			Reactor[i].PV = PV_temp[i]
			Reactor[i].OP = PIDfunct( int(Reactor[i].SP),  int(Reactor[i].PV))
			Reactor[i].HeaterTemp = Heater_temp[i]

			#CONTROL HEATER
			ard.ControlHeaters(ard=A)
			#CONTROL MOTORS
			#ard.ControlStirringMotors(A,rpm=10,en=True)
	  
	else:   #ARDUINO FAILED
		for i in rng:
			Reactor[i].ActiveTime= time.time()
		
		A = ard.ArdConnect(com)
		ard.ArdSetup(A)

	StirrOnOff()
	SecondLoopTimer=Timer(0.5, SecondLoop)
	SecondLoopTimer.start()

## This function is been called every minute
def MinuteLoop():
	global MinuteLoopTimer
	
	if ard.run:
		date = time.time()
		for i in rng:    
			### LOG REACTOR TEMPERATURE
			csv_path = '{}\CSV\Reactor ({})\Reactor_Temperature\LOG_{}.csv'.format(Path(__file__).parent.absolute(),i+1, i+1)
			CSV.LOG(csv_path , 'Date,Temperature', date, Reactor[i].PV )
		   
			### LOG HEATER TEMPERATURE
			csv_path= '{}\CSV\Reactor ({})\Heater_Temperature\LOG_{}.csv'.format(Path(__file__).parent.absolute(),i+1, i+1)
			CSV.LOG(csv_path , 'Date,Temperature',date, Reactor[i].HeaterTemp )
		   
	MinuteLoopTimer=Timer(2, MinuteLoop)
	MinuteLoopTimer.start()

## Convert SP,PV to OP (0-100%)
def PIDfunct(sp,pv):
	op=[]

	K=0.01
	P=1
	d=1

	op = (sp- pv)

	return op

## Returns a text from bool variable
def BoolToText(bool,T='True',F='False'):
	if bool: return T
	else: return F


def _spinSP():
	Reactor[selReact].SP=int(GUI_SpValue.get())
	print('SP changed')
def _spinOn():
	Reactor[selReact].TimeOn= int(GUI_OnValue.get())
	print('TimerOn changed')
def _spinOff():
	Reactor[selReact].TimeOff= int(GUI_OffValue.get())
	print('TimerOff changed')
def _spinRPM():
	Reactor[selReact].RPM = int(GUI_RpmValue.get())
	print('RPM changed')
def _ChangeReactor(r=0):
	global selReact
	selReact = r

	print('Reactor {0} selected'.format(selReact+ 1) )

	for i in rng:
		GUI_ReactorButtons[i].configure(bg= Unselected_color)
	GUI_ReactorButtons[r].configure(bg= Selected_color)
	
	UpdateVarTextTimer.cancel()
	UpdateVarText()  
def _SerialPortChange():
	global com
	com = TextVar.COM.get()
	print("COM CHANGED")

	return True
def _EnableClick():
	toggle = not Reactor[selReact].Enable
	Reactor[selReact].Enable = toggle
	
	print('Reactor {} is {}'.format(selReact+1 ,BoolToText(toggle,"Enabled","Disabled")))
   
	UpdateVarTextTimer.cancel()
	UpdateVarText()
def _FeedMaterial():

	date = time.time()
	### CSV FEEDING METERIAL
	csv_path= '{}\CSV\Reactor ({})\Feeding_material\LOG_{}.csv'.format(Path(__file__).parent.absolute(), selReact+1, selReact+1)
	CSV.LOG(csv_path , 'Date,Qty,Unit,Material', date, TextVar.FeedAmount.get(),TextVar.FeedMaterial.get(),TextVar.FeedUnit.get()) 

	#Clear feed material objects
	TextVar.FeedAmount.set('')
	TextVar.FeedMaterial.set('')
	TextVar.FeedUnit.set('')
	print('Material fed')



def _PIDConfig():
	print('PID CONFIG')


################################################################################################
######## INITIAL CODE ########
################################################################################################
global A
A = ard.ArdConnect(com)
ard.ArdSetup(A)

SecondLoopTimer=Timer(1, SecondLoop).start()
MinuteLoopTimer=Timer(1, MinuteLoop).start()




#################################################################################################
##### GUI CODE #####
#################################################################################################

# Selected reactor to be displayed
selReact = 0 

## Color constants
Selected_color    =  'steelblue'
Unselected_color  = '#{:02X}{:02X}{:02X}'.format(180,200,220)  # Temperature area background
Enabled_color     =  Selected_color 
Disabled_color    = Unselected_color
Temperature_dark  = '#{:02X}{:02X}{:02X}'.format(0,0,90)
Temperature_light = 'lightsteelblue'
Stirring_dark     = '#{:02X}{:02X}{:02X}'.format(0,90,90)
Stirring_light    = 'azure'
Stirring_on       = '#{:02X}{:02X}{:02X}'.format(0,255,10)
Stirring_off      = '#{:02X}{:02X}{:02X}'.format(0,60,10)
Feeding_dark      = '#{:02X}{:02X}{:02X}'.format(255,215,0)
Feeding_light     = '#{:02X}{:02X}{:02X}'.format(255,255,160)


## Main window size and zoom(temporary)
z=1         # ZOOM
zl=1.6  *z  # Font zoom

## Main Window
GUI_window = tk.Tk()
w, h = GUI_window.winfo_screenwidth(), GUI_window.winfo_screenheight()
## Main window size and zoom(temporary)
z=1         # ZOOM
zl=1.6  *z  # Font zoom

GUI_window.geometry('{}x{}'.format(int(w*0.9) , int(h*0.9)) )
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
		self.RPM = StringVar()
		self.StirrStatus = StringVar()
		self.CurrTime = StringVar()
		#Feeding Frame
		self.FeedAmount = StringVar()
		self.FeedMaterial = StringVar()
		self.FeedUnit = StringVar()
		#Graph Frame
		self.fromDate = StringVar()
		#Bottom bar
		self.InfoBar = StringVar()
		self.COM =StringVar()
TextVar =  VarLabel() #Variable text object



## LEFT BAR with the reactor buttons
#GUI_LeftPanelLeftBar = tk.Canvas(GUI_window, bg="blue4", height=(h//0.9), width=(w//10) )
#GUI_LeftPanelLeftBar.pack(side=LEFT)
GUI_LeftPanelLeftBar = tk.Canvas(GUI_window, bg="blue4" )
GUI_LeftPanelLeftBar.place(x=0,y=0 ,height= h, width=(w*0.1) )
# Column of buttons
GUI_ReactorButtons=[0]*6
for i in rng:
	GUI_ReactorButtons[i]= tk.Button(GUI_LeftPanelLeftBar, text= '{} {}'.format('Reactor ', i+1) , bg= Unselected_color, font=("Calibri", int(10*zl))
							,relief=FLAT,command= partial(_ChangeReactor,i)) 
	GUI_ReactorButtons[i].place(x=0, y= (i*h/15)+(1*h/15) , relwidth=1, height= h/15 -5)
GUI_ReactorButtons[selReact].configure(bg=Selected_color)



## Reactor Frame
GUI_ReactorFrame= tk.Frame(GUI_window, bg='black', bd=2)
GUI_ReactorFrame.place(x= (w//10)+20 ,y= 0*(h//10)  ,width= 8*(w//10) , height= 4*(h//10))
# Reactor Label
GUI_ReactorName=tk.Label(GUI_ReactorFrame, textvariable=TextVar.Name ,width=10, font=("Calibri", int(15*zl)), anchor= 'w')
GUI_ReactorName.place(relx=0.0, rely=0.0, relwidth=1, relheight=0.1)
# ENABLE/DISABLE Reactor
GUI_ReactorEnable= tk.Button(GUI_ReactorFrame, textvariable=TextVar.Enable, bd=1,bg='light blue', command= _EnableClick, font=("Calibri", int(9*zl)), relief="solid")
#GUI_ReactorEnable.place(relx=0.8, rely=0.0, relwidth=0.2, relheight=0.1)



## Temperature FRAME
GUI_TempFrame=tk.Frame(GUI_ReactorFrame, bg= Temperature_light)
GUI_TempFrame.place(relx=0, rely=0.11 , relwidth=1/3, relheight= 0.86)
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
GUI_OpLabel.place(relx=0.45, rely=0.6, relwidth=0.5, relheight=0.15)
# Heater temperature sensor
GUI_HeaterTemp=tk.Label(GUI_TempFrame, textvariable= TextVar.HeaterTemp, bg=Temperature_light, fg="black", font=("Calibri", int(8*zl)),anchor='w')
GUI_HeaterTemp.place(relx=0.45, rely=0.75, relwidth=0.5, relheight=0.1)
# PID parameters button
GUI_PID = tk.Button(GUI_TempFrame, text= "PID" , bg= Unselected_color, command=_PIDConfig, font=("Calibri", int(8*zl))) 
GUI_PID.place(relx=0.01, rely=1-0.15, relwidth=0.2, relheight=0.14)





## Stirring FRAME
GUI_StirrFrame=tk.Frame(GUI_ReactorFrame, bg= Stirring_light)
GUI_StirrFrame.place(relx=1/3+0.005,rely=0.11, relwidth=1/3-0.01, relheight=0.86)
# Stirring Label
GUI_StirrLabel=tk.Label(GUI_StirrFrame, text="Stirring", bg=Stirring_dark, fg="white", font=("Calibri", int(11*zl),'bold'), anchor="w")
GUI_StirrLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# Stirring RPM
GUI_MotorLabel=tk.Label(GUI_StirrFrame, text="Motor" , fg="black" , bg=Stirring_light,  font=("Calibri", int(9*zl),'bold'), anchor="w")
GUI_MotorLabel.place(relx=0.0, rely=0.14, relwidth=0.2, relheight=0.15)
GUI_RpmLabel=tk.Label(GUI_StirrFrame, text="RPM ", bg= Stirring_light ,  font=("Calibri", int(9*zl)), anchor="w")
GUI_RpmLabel.place(relx=0.0, rely=0.3, relwidth=0.25, relheight=0.15)
GUI_RpmValue=tk.Spinbox(GUI_StirrFrame, textvariable= TextVar.RPM, values=(1, 5, 10, 15, 30, 60), bg= 'white', fg="black", command= _spinRPM, font=("Calibri", int(13*zl)), relief="solid")
GUI_RpmValue.place(relx=0.14, rely=0.3, relwidth=0.25, relheight=0.15)
# Duration label
GUI_DurationLabel=tk.Label(GUI_StirrFrame, text="Inteval duration (seg)", fg="black",bg=Stirring_light,  font=("Calibri", int(10*zl), "bold"), anchor="w")
GUI_DurationLabel.place(relx=0.5, rely=0.14, relwidth=0.5, relheight=0.15)
# On time label
GUI_OnLabel=tk.Label(GUI_StirrFrame, text="ON" , fg="black" , bg=Stirring_light,  font=("Calibri", int(9*zl)), anchor="w")
GUI_OnLabel.place(relx=0.5, rely=0.3, relwidth=0.2, relheight=0.15)
GUI_OnValue=tk.Spinbox(GUI_StirrFrame, from_=1, to=60, textvariable=TextVar.TimeOn, fg="black", command= _spinOn, font=("Calibri", int(15*zl)), relief="solid")
GUI_OnValue.place(relx=0.6, rely=0.3, relwidth=0.25, relheight=0.15)
# Off time label
GUI_OffLabel=tk.Label(GUI_StirrFrame, text="OFF", bg= Stirring_light ,  font=("Calibri", int(9*zl)), anchor="w")
GUI_OffLabel.place(relx=0.5, rely=0.5, relwidth=0.2, relheight=0.15)
GUI_OffValue=tk.Spinbox(GUI_StirrFrame, textvariable= TextVar.TimeOff, from_=1, to=60 ,command=_spinOff, bg= 'white', fg="black",  font=("Calibri", int(13*zl)), relief="solid")
GUI_OffValue.place(relx=0.6, rely=0.5, relwidth=0.25, relheight=0.15)
# Stirring Status
GUI_StirrStatus=tk.Label(GUI_StirrFrame, textvariable=TextVar.StirrStatus, bg= Stirring_on, font=("Calibri", int(15*zl), "bold"))
GUI_StirrStatus.place(relx=0.25, rely=0.7, relwidth=0.55, relheight=0.2)
# Time counter
GUI_StirrTime=tk.Label(GUI_StirrFrame, textvariable=TextVar.CurrTime, bg= Stirring_light, font=("Calibri", int(9*zl), "bold"),anchor='nw')
GUI_StirrTime.place(relx=0.6, rely=0.9, relwidth=0.45, relheight=0.15)




## Feeding Material FRAME
GUI_FeedFrame=tk.Frame(GUI_ReactorFrame, bg= Feeding_light)
GUI_FeedFrame.place(relx=2/3, rely=0.11, relwidth=1/3, relheight=0.86)
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
GUI_FeedInButton= tk.Button(GUI_FeedFrame, text= "Enter" , bg= 'white', command=_FeedMaterial, font=("Calibri", int(8*zl))) 
GUI_FeedInButton.place(relx=0.1, rely=0.55, relwidth=1-0.2, relheight=0.14)




### Graphs Frame
GUI_GraphicsCanvas= tk.Canvas(GUI_window, bg='black', bd=2)
GUI_GraphicsCanvas.place(x= (w//10)+20 ,y= 4.1*(h//10)  ,width= 8*(w//10) , height= 4.8*(h//10))
# Header label
GUI_GraphHeaderLabel=tk.Label(GUI_GraphicsCanvas, text='Temperature',  fg="white",bg='black',  font=("Calibri", int(10*zl), "bold"), anchor='n')
GUI_GraphHeaderLabel.place(relx=0.01, rely=0.01, relwidth=1-0.02, relheight=0.15)
## PLOT
figure = plt.Figure(figsize=(15,15), dpi=100)
ax = figure.add_subplot(111)
line = FigureCanvasTkAgg(figure, GUI_GraphicsCanvas)
line.get_tk_widget().place(relx=0.01,rely=0.1, relwidth=0.85, relheight=0.85)
# REACT TMP
df = Panda.GRAPH(path = CsvDir(selReact,'Heater_Temperature'), info = 'Temperature', from_date = '2019-11-01 00:00:00' ,to_date = '2019-11-29 11:59:00'  )
df.plot(kind='line', legend=True, ax=ax, color='r',marker='.', fontsize=10)
# HEATER TMP
df = Panda.GRAPH(path = CsvDir(selReact,'Reactor_Temperature'), info = 'Temperature', from_date = '2019-11-01 00:00:00' ,to_date = '2019-11-29 11:59:00'  )
df.plot(kind='line', legend=True, ax=ax, color='b',marker='.', fontsize=10)


# Hour button
GUI_HourButton= tk.Button(GUI_GraphicsCanvas, text= "Hour" , bg= 'white', command=_FeedMaterial, font=("Calibri", int(12*zl))) 
GUI_HourButton.place(relx=1-0.1, rely=1*(1/7) , relwidth= 0.1, relheight=0.14)
# Day button
GUI_DayButton= tk.Button(GUI_GraphicsCanvas, text= "Day" , bg= 'white', command=_FeedMaterial, font=("Calibri", int(12*zl))) 
GUI_DayButton.place(relx=1-0.1, rely=2*(1/7) , relwidth= 0.1, relheight=0.14)
# Week Days button
GUI_WeekButton= tk.Button(GUI_GraphicsCanvas, text= "Week" , bg= 'white', command=_FeedMaterial, font=("Calibri", int(12*zl))) 
GUI_WeekButton.place(relx=1-0.1, rely=3*(1/7) , relwidth= 0.1, relheight=0.14)
# Month button
GUI_MonthButton= tk.Button(GUI_GraphicsCanvas, text= "Month" , bg= 'white', command=_FeedMaterial, font=("Calibri", int(12*zl))) 
GUI_MonthButton.place(relx=1-0.1, rely=4*(1/7) , relwidth= 0.1, relheight=0.14)
# Year button
GUI_YearButton= tk.Button(GUI_GraphicsCanvas, text= "Year" , bg= 'white', command=_FeedMaterial, font=("Calibri", int(12*zl))) 
GUI_YearButton.place(relx=1-0.1, rely=5*(1/7) , relwidth= 0.1, relheight=0.14)





## Status Bar
GUI_BottomBar=tk.Label(GUI_window, textvariable=TextVar.InfoBar ,bg= 'DarkGray' , font=('Calibri ',int(8*zl)), anchor='e'  )
GUI_BottomBar.pack(side='bottom', fill='x' )
#SERIAL PORT
GUI_SerialPortLabel = tk.Label(GUI_BottomBar,text='PORT ',bg='DarkGray', font=('Calibri ',int(6*zl)))
GUI_SerialPortLabel.pack(side='left')
GUI_SerialPortValue = tk.Spinbox(GUI_BottomBar,textvariable=TextVar.COM, values=com_arr, bg= 'white', font=('Calibri ',int(8*zl)), command= _SerialPortChange)
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
	CSV.RPM[i] = Reactor[i].RPM
CSV.config_save(f=SetupFile, SP=CSV.SP, TimeOn=CSV.TimeOn ,TimeOff=CSV.TimeOff, RPM=CSV.RPM, COM=com)

sys.exit()