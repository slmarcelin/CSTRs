#!/usr/bin/python3
import CSV_funct as CSV
import ARD_funct as ard
import Panda_funct as Panda

import tkinter as tk
from tkinter import *
from threading import Timer
from functools import partial
from time import *
from datetime import *
import time
import sys
import pandas as pd  
import matplotlib.dates as mdates 
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt



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

## GET VALUES FROM CSV & Create Reactor object
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
com_arr.append('/dev/ttyS0')
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

	date = strftime('%B %eth %Y\nTime: %H:%M:%S', gmtime(time.time() ))
	GUI_Clock.configure(text=date)

	i = selReact
	GUI_ReactorName.configure(text =Reactor[i].Name  )
	#GUI_ReactorEnable.configure(text= boolToText(Reactor[selReact].Enable,'Enabled','Disabled') )
	
	GUI_SpValue.configure(text=  Reactor[i].SP ) 
	GUI_PvValue.configure(text= '{} {}'.format(Reactor[i].PV, '°C') )
	GUI_OpLabel.configure(text= 'Heating {} %'.format(Reactor[i].OP) )
	GUI_HeaterTemp.configure(text= 'Temp: {} °C'.format(Reactor[i].HeaterTemp) )
	GUI_OnValue.configure(text= Reactor[i].TimeOn)
	GUI_OffValue.configure(text= Reactor[i].TimeOff)
	GUI_RpmValue.configure(text= Reactor[i].RPM)

	GUI_StirrStatus.configure(text= BoolToText( Reactor[i].StirrStatus,"ON", "OFF") )
	GUI_StirrTime.configure(text= strftime("%H:%M:%S", gmtime(time.time()-  Reactor[i].ActiveTime)) )

	GUI_StatusInfo.configure(text= BoolToText( ard.run,"ARDUINO IS CONNECTED", "ARDUINO IS NOT DETECTED") )
   

	#Color of ON/OFF stirring status
	if Reactor[selReact].StirrStatus:
		GUI_StirrStatus.configure(bg =RGB_Stirring_ON)
	else:
		GUI_StirrStatus.configure(bg =RGB_Stirring_OFF)
	#Color of Enable button
	if Reactor[selReact].Enable:
		GUI_ReactorEnable.configure(bg =RGB_LeftBar_MidBlue)
	else:
		GUI_ReactorEnable.configure(bg =RGB_LeftBar_LightBlue)

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
			Reactor[i].PV = 0
			Reactor[i].OP = 0
			Reactor[i].HeaterTemp = 0
			Reactor[i].ActiveTime = time.time()
		A = ard.ArdConnect(com)
		if ard.run:
			ard.ArdSetup(A)

	StirrOnOff()
	SecondLoopTimer=Timer(1, SecondLoop)
	SecondLoopTimer.start()

## This function is been called every minute
def MinuteLoop():

	if ard.run and Reactor[0] != 0 or True:
		date=datetime.strftime(datetime.now(),'%Y-%m-%d')

		for i in rng:   
			
			### LOG REACTOR TEMPERATURE
			path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i+1, CSV.TempReactorName[i])
			#Check if CSV file is older than 30 days or bigger than 10MB
			check = fileCheck(CSV.TempReactorName[i], path,i)
			if check:

				#DETLETE OLD FILE

				CSV.TempReactorName[i] = '{}-CSTR-{}-1.csv'.format(date ,i+1)
				CSV.setup_CSVnames(f = CSV.SetupFile,trn= CSV.TempReactorName, thn= CSV.TempHeaterName, sin= CSV.StirringInfoName, fmn= CSV.FeedingMaterialName)
				path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i+1, CSV.TempReactorName[i])
			CSV.LOG(f = path , header = 'Date,RPM,ON,OFF', v1= Reactor[i].PV )
			#####################################################################################



			### LOG HEATER TEMPERATURE
			path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i+1, CSV.TempHeaterName[i])
			#Check if CSV file is older than 30 days or bigger than 10MB
			check = fileCheck(CSV.TempHeaterName[i], path,i)
			if check:

				#DETLETE OLD FILE
				
				CSV.TempReactorName[i] = '{}-CSTR-{}-2.csv'.format(date ,i+1)
				CSV.setup_CSVnames(f = CSV.SetupFile,trn= CSV.TempReactorName, thn= CSV.TempHeaterName, sin= CSV.StirringInfoName, fmn= CSV.FeedingMaterialName)
				path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i+1, CSV.TempHeaterName[i])
			CSV.LOG(f = path , header = 'Date,Heater Temperature',v1= Reactor[i].HeaterTemp)
			#####################################################################################
			


			### LOG Stirring info
			path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i+1, CSV.StirringInfoName[i])
			#Check if CSV file is older than 30 days or bigger than 10MB
			check = fileCheck(CSV.StirringInfoName[i], path,i)
			if check:

				#DETLETE OLD FILE
				
				CSV.StirringInfoName[i] = '{}-CSTR-{}-3.csv'.format(date ,i+1)
				CSV.setup_CSVnames(f = CSV.SetupFile,trn= CSV.TempReactorName, thn= CSV.TempHeaterName, sin= CSV.StirringInfoName, fmn= CSV.FeedingMaterialName)
				path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, i+1, CSV.StirringInfoName[i])
			CSV.LOG(f = path , header = 'Date,RPM,ON,OFF',v1= Reactor[i].RPM,v2=Reactor[i].TimeOn,v3=Reactor[i].TimeOff)
			#####################################################################################

			
	global MinuteLoopTimer
	MinuteLoopTimer=Timer(5, MinuteLoop) 
	MinuteLoopTimer.start()

## Check if the file is older than 30 days or bigger than 10 MB
def fileCheck(fileName,path,reactor):
	
	## get how old the file is
	date = fileName[0:10]
	delta = datetime.now() - datetime.strptime(date, '%Y-%m-%d') # Get the days of CVS
	age= delta.days
	
	## get size of file
	statinfo = os.stat(path)
	size = statinfo.st_size

	# IF THE CSV IS OLDER THAN 30 DAYS
	if age> 30 or size> 10* 1000000:
		return True
	else:
		return False

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



## Function commands of GUI objects
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
def _SerialPortChange():
	global com
	com = GUI_SerialPortValue.get()


	print("COM CHANGED")

	return True
def _EnableClick():
	toggle = not Reactor[selReact].Enable
	Reactor[selReact].Enable = toggle
	
	print('Reactor {} is {}'.format(selReact+1 ,BoolToText(toggle,"Enabled","Disabled")))
   
	UpdateVarTextTimer.cancel()
	UpdateVarText()
def _FeedMaterial():

	date=datetime.strftime(datetime.now(),'%Y-%m-%d')


	### LOG Feed Material
	path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, selReact+1, CSV.FeedingMaterialName[selReact])
	#Check if CSV file is older than 30 days or bigger than 10MB
	check = fileCheck(CSV.FeedingMaterialName[selReact], path,selReact)
	if check:

		#DETLETE OLD FILE
		
		CSV.FeedingMaterialName[selReact] = '{}-CSTR-{}-4.csv'.format(date ,selReact+1)
		CSV.setup_CSVnames(f = CSV.SetupFile,trn= CSV.TempReactorName, thn= CSV.TempHeaterName, sin= CSV.StirringInfoName, fmn= CSV.FeedingMaterialName)
		path = '{}/Reactor_{}/{}'.format(CSV.CsvFolder, selReact+1, CSV.StirringInfoName[selReact])
	CSV.LOG(f = path , header = 'Date,Qty,Unit,Material',v1= GUI_FeedAmount.get(),v2=GUI_FeedUnit.get(),v3=GUI_FeedMaterial.get() )
	


	#Clear feed material objects
	GUI_FeedAmount.configure(text= '')
	GUI_FeedUnit.configure(text='')
	GUI_FeedMaterial.configure(text='')


	print('Material fed')
def _PIDConfig():
	print('PID CONFIG')
	print(' ')
def _ChangeReactor(r=0):
	global selReact
	selReact = r

	print('Reactor {0} selected'.format(selReact+ 1) )

	for i in rng:
		GUI_ReactorButtons[i].configure(bg= RGB_LeftBar_LightBlue)
	GUI_ReactorButtons[r].configure(bg= RGB_LeftBar_MidBlue)
	
	UpdateVarTextTimer.cancel()
	
	UpdateVarText() 
	UpdatePlot(days=selRange,ax=ax )


def UpdatePlot(days,ax):

	global selRange,selReact
	
	if days!=0: 
		selRange = days

	RTPath  = '{}/{}'.format(CSV.ReactorFolder[selReact],CSV.TempReactorName[selReact]) # Reactor temperature CSV file
	HTPath  = '{}/{}'.format(CSV.ReactorFolder[selReact],CSV.TempHeaterName[selReact]) # Heater temperature CSV file
		
	desiredRange= timedelta(hours= 24 * selRange) #obtain date for last 24 hrs
	now = datetime.now() #get today's date
	TimeRange = now - desiredRange #Get the date


	if selRange == 1:
		#desiredRange=datetime.timedelta(hours=24) #obtain date for last 24 hrs
		
		GUI_24HourButton.configure(bg= RGB_Graph_b1,relief=SUNKEN)
		GUI_WeekButton.configure(bg= RGB_Graph_b2,relief=GROOVE)
		GUI_MonthButton.configure(bg= RGB_Graph_b2,relief=GROOVE)
		GraphTitle = "Hour Rate" #Title of the graph
		xlabel = 'Last 24 hours' #set the x axis label
		rate='30min'

	if selRange == 7:
		#desiredRange=datetime.timedelta(days=7) #obtain date for last 24 hrs
		
		GUI_24HourButton.configure(bg= RGB_Graph_b2,relief=GROOVE)
		GUI_WeekButton.configure(bg= RGB_Graph_b1,relief=SUNKEN)
		GUI_MonthButton.configure(bg= RGB_Graph_b2,relief=GROOVE)
		GraphTitle = "Week Rate" #Title of the graph
		xlabel = 'Last 7 days' #set the x axis label
		rate='D'

	if selRange == 32:
		#desiredRange=datetime.timedelta(days=32) #obtain date for last 24 hrs
		
		GUI_24HourButton.configure(bg= RGB_Graph_b2,relief=GROOVE)
		GUI_WeekButton.configure(bg= RGB_Graph_b2,relief=GROOVE)
		GUI_MonthButton.configure(bg= RGB_Graph_b1,relief=SUNKEN)
		GraphTitle = "Month Rate" #Title of the graph
		xlabel = 'Last 32 days' #set the x axis label
		rate='D'

	now = datetime.now() #get today's date
	TimeRange = now - desiredRange #Get the date

	ReactorTemperatureDF = Panda.DataFrame(path=RTPath, rate=rate, TimeRange=TimeRange,now= now) # Reactor Temperature DataFrame
	HeaterTemperatureDF =  Panda.DataFrame(path=HTPath, rate=rate, TimeRange=TimeRange,now= now) # Heater Temperature DataFrame

	#This arrays formats the x axis, according to time or dates
	locator = mdates.AutoDateLocator() #from the matpotlib library package
	formatter = mdates.ConciseDateFormatter(locator) #specific type of style
	formatter.formats = ['%y','%b','%d','%H:%M','%H:%M','%S.%f',] #Format the dates 
	formatter.zero_formats = [''] + formatter.formats[:-1] #add format
	formatter.zero_formats[3] = '%d-%b' #format
	formatter.offset_formats = ['','%Y','%b %Y','%d %b %Y','%d %b %Y','%d %b %Y %H:%M', ] #other format

	if not ReactorTemperatureDF.empty and not HeaterTemperatureDF.empty :
		ax.cla()
		p1=ax.plot(ReactorTemperatureDF, marker='.', markersize=8, linestyle='-', color='DarkBlue')
		p2=ax.plot(HeaterTemperatureDF, marker='.', markersize=8, linestyle='-', color='red') #plot the data
		ax.legend((p1[0], p2[0]), ('Reactor', 'Heater') )
		ax.grid()

		ax.xaxis.set_major_locator(locator) #set the x axis locator
		ax.xaxis.set_major_formatter(formatter) #set format

	else:
		ax.cla()
		GraphTitle = "Not enough data to graph the "+ GraphTitle+" for Reactor "+str(selReact+1)+"\nTry again later or pick another option"

	ax.set_title( GraphTitle, size = 12*zl)  #set the graph title
	ax.set_xlabel(xlabel, size = 12*zl) #set the x axis label
	ax.set_ylabel('°C Degrees',size = 12*zl) #set the y axis label
	
	
	graph.draw()
	
	print("PLOT UPDATED")



################################################################################################
######## INITIAL CODE ########
################################################################################################
global A
A = ard.ArdConnect(com)
ard.ArdSetup(A)






#################################################################################################
##### GUI CODE #####
################################################################################################

# Selected reactor to be displayed
selReact = 0 
# Selected range to be ploted
selRange = 1


## Color constants
RGB_LeftBar_DarkBlue =	'#{:02X}{:02X}{:02X}'.format(0,0,140)
RGB_LeftBar_MidBlue = 	'#{:02X}{:02X}{:02X}'.format(82,136,174)
RGB_LeftBar_LightBlue =	'#{:02X}{:02X}{:02X}'.format(199,214,221)

RGB_Temperature_title =	'#{:02X}{:02X}{:02X}'.format(27,61,88)
RGB_Stirring_title =	'#{:02X}{:02X}{:02X}'.format(27,124,41)
RGB_Feeding_title =		'#{:02X}{:02X}{:02X}'.format(242,208,1)
RGB_Sections_bg =		'#{:02X}{:02X}{:02X}'.format(235,236,232)

RGB_Stirring_ON = 	'#{:02X}{:02X}{:02X}'.format(60,255,108)
RGB_Stirring_OFF=	'#{:02X}{:02X}{:02X}'.format(0,85,15)

RGB_Graph_b1 = 	'#{:02X}{:02X}{:02X}'.format(181,197,196)
RGB_Graph_b2=	'#{:02X}{:02X}{:02X}'.format(237,241,244)




## Main Window
GUI_window = tk.Tk()

# get screen width and height
sw = GUI_window.winfo_screenwidth() # width of the screen
sh = GUI_window.winfo_screenheight() # height of the screen

## Main window size and zoom
z=0.85      # ZOOM
w=int(sw*z) # width for the Tk root
h=int(sh*z) # height for the Tk root
zl=1.7  *z  # Font zoom

# calculate x and y coordinates for the Tk root window
x = (sw/2) - (w/2)
y = (sh/2) - (h/2)


# Font config
font_name = 'calibri'
font_small = (font_name, int(10*zl) )   # Small
font_small_bold = (font_name, int(10*zl),'bold' )   # Smallbold
font_medium = (font_name, int(12*zl) )	#medium
font_big = (font_name, int(32*zl) )	#big




#GUI_window.geometry('{}x{}'.format(w,h) )
GUI_window.geometry('%dx%d+%d+%d' % (w, h, x, 0))
#GUI_window.state("zoomed")
GUI_window.configure(bg='white')
GUI_window.resizable(1,1)


GUI_FRAME = tk.Canvas(GUI_window,bg="white")
GUI_FRAME.place(x=0,y=0 ,height= h, width= w)



## LEFT BAR with the reactor buttons
GUI_LeftPanelLeftBar = tk.Canvas(GUI_FRAME, bg=RGB_LeftBar_DarkBlue )
GUI_LeftPanelLeftBar.place(relx=0.0, rely=0.0, relwidth=0.2, relheight=1)

# Column of buttons
GUI_ReactorButtons=[0]*6
for i in rng:
	GUI_ReactorButtons[i]= tk.Button(GUI_LeftPanelLeftBar, text= '{} {}'.format('Reactor ', i+1) , bg= RGB_LeftBar_LightBlue, font= font_medium
							, relief=FLAT,command= partial(_ChangeReactor,i)) 
	GUI_ReactorButtons[i].place(relx=0, rely= (i/14)+(3/14) , relwidth=1, relheight= (1/15) )
GUI_ReactorButtons[selReact].configure(bg=RGB_LeftBar_MidBlue)
#CLOCK



GUI_Clock = Label(GUI_LeftPanelLeftBar,font= font_small_bold, bg='blue', fg='white')
GUI_Clock.place(relx= 0.01, rely= 0.03, relwidth= 1-0.02, relheight= 0.065)




## Reactor Frame
GUI_ReactorFrame= tk.Frame(GUI_FRAME, bg='black', bd=2)
GUI_ReactorFrame.place(relx= 0.205, rely= 0.01, relwidth= 1-0.21, relheight= 0.45 )
# Reactor Label
GUI_ReactorName=tk.Label(GUI_ReactorFrame,bg='white' ,width=10, font= font_medium, anchor= 'w')
GUI_ReactorName.place(relx=0.0, rely=0.0, relwidth=1, relheight=0.1)
# ENABLE/DISABLE Reactor
GUI_ReactorEnable= tk.Button(GUI_ReactorFrame, bd=1,bg='light blue', command= _EnableClick, font=(font_name, int(9*zl)), relief="solid")
#GUI_ReactorEnable.place(relx=0.8, rely=0.0, relwidth=0.2, relheight=0.1)



## Temperature FRAME
GUI_TempFrame=tk.Frame(GUI_ReactorFrame, bg= RGB_Sections_bg)
GUI_TempFrame.place(relx=0, rely=0.11 , relwidth=1/3, relheight= 0.86)
# Temperature label
GUI_TempLabel=tk.Label(GUI_TempFrame, text="Temperature", bg=RGB_Temperature_title, fg="white",font= font_medium, anchor="w")
GUI_TempLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# SP Label
GUI_SpLabel= tk.Label(GUI_TempFrame, text="SP", fg="black",bg=RGB_Sections_bg, font= font_small_bold, anchor="w")
GUI_SpLabel.place(relx=0, rely=0.15, relwidth=0.15, relheight=0.15)
GUI_SpValue=tk.Spinbox(GUI_TempFrame, from_=25, to=50, fg="green", command= _spinSP, font= font_big, relief="solid")
GUI_SpValue.place(relx=0.02, rely=0.3, relwidth=0.3, relheight=0.3)
# Pv
GUI_PvLabel=tk.Label(GUI_TempFrame, text='PV',  fg="black",bg=RGB_Sections_bg , font= font_small_bold, anchor="w")
GUI_PvLabel.place(relx=0.45, rely=0.15, relwidth=0.15, relheight=0.15)
GUI_PvValue=tk.Label(GUI_TempFrame, bg=RGB_Sections_bg, fg=RGB_Temperature_title , font= font_big, anchor="w")
GUI_PvValue.place(relx=0.45, rely=0.3, relwidth=0.6, relheight=0.25)
# OP Status
GUI_OpLabel=tk.Label(GUI_TempFrame, bg='white', fg="red", font= font_small)
GUI_OpLabel.place(relx=0.45, rely=0.6, relwidth=0.5, relheight=0.15)
# Heater temperature sensor
GUI_HeaterTemp=tk.Label(GUI_TempFrame, bg=RGB_Sections_bg, fg="black", font= font_small,anchor='w')
GUI_HeaterTemp.place(relx=0.45, rely=0.75, relwidth=0.5, relheight=0.1)
# PID parameters button
GUI_PID = tk.Button(GUI_TempFrame, text= "PID" , bg= RGB_Graph_b2, command=_PIDConfig, font= font_small) 
GUI_PID.place(relx=0.01, rely=1-0.15, relwidth=0.2, relheight=0.14)





## Stirring FRAME
GUI_StirrFrame=tk.Frame(GUI_ReactorFrame, bg= RGB_Sections_bg)
GUI_StirrFrame.place(relx=1/3+0.005,rely=0.11, relwidth=1/3-0.01, relheight=0.86)
# Stirring Label
GUI_StirrLabel=tk.Label(GUI_StirrFrame, text="Stirring", bg=RGB_Stirring_title, fg="white", font= font_medium, anchor="w")
GUI_StirrLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# Stirring RPM
GUI_MotorLabel=tk.Label(GUI_StirrFrame, text="Motor" , fg="black" , bg=RGB_Sections_bg,  font= font_small_bold, anchor="w")
GUI_MotorLabel.place(relx=0.0, rely=0.14, relwidth=0.2, relheight=0.15)
GUI_RpmLabel=tk.Label(GUI_StirrFrame, text="RPM ", bg= RGB_Sections_bg ,  font= font_small, anchor="w")
GUI_RpmLabel.place(relx=0.0, rely=0.3, relwidth=0.25, relheight=0.15)
GUI_RpmValue=tk.Spinbox(GUI_StirrFrame, values=(1, 5, 10, 15, 30, 60), bg= 'white', fg="black", command= _spinRPM, font= font_small, relief="solid")
GUI_RpmValue.place(relx=0.14, rely=0.3, relwidth=0.25, relheight=0.15)
# Duration label
GUI_DurationLabel=tk.Label(GUI_StirrFrame, text="Inteval duration (mins)", fg="black",bg=RGB_Sections_bg, font= font_small_bold, anchor="w")
GUI_DurationLabel.place(relx=0.44, rely=0.14, relwidth=0.55, relheight=0.15)
# On time label
GUI_OnLabel=tk.Label(GUI_StirrFrame, text="ON" , fg="black" , bg=RGB_Sections_bg, font= font_small, anchor="w")
GUI_OnLabel.place(relx=0.49, rely=0.3, relwidth=0.2, relheight=0.15)
GUI_OnValue=tk.Spinbox(GUI_StirrFrame, from_=1, to=60, fg="black", command= _spinOn, font= font_small, relief="solid")
GUI_OnValue.place(relx=0.6, rely=0.3, relwidth=0.25, relheight=0.15)
# Off time label
GUI_OffLabel=tk.Label(GUI_StirrFrame, text="OFF", bg= RGB_Sections_bg , font= font_small, anchor="w")
GUI_OffLabel.place(relx=0.49, rely=0.5, relwidth=0.2, relheight=0.15)
GUI_OffValue=tk.Spinbox(GUI_StirrFrame, from_=1, to=60 ,command=_spinOff, bg= 'white', fg="black", font= font_small, relief="solid")
GUI_OffValue.place(relx=0.6, rely=0.5, relwidth=0.25, relheight=0.15)
# Stirring Status
GUI_StirrStatus=tk.Label(GUI_StirrFrame, bg= RGB_Stirring_ON,font= font_medium)
GUI_StirrStatus.place(relx=0.25, rely=0.7, relwidth=0.55, relheight=0.2)
# Time counter
GUI_StirrTime=tk.Label(GUI_StirrFrame, bg= RGB_Sections_bg, font= font_small,anchor='nw')
GUI_StirrTime.place(relx=0.6, rely=0.9, relwidth=0.45, relheight=0.15)




## Feeding Material FRAME
GUI_FeedFrame=tk.Frame(GUI_ReactorFrame, bg= RGB_Sections_bg)
GUI_FeedFrame.place(relx=2/3, rely=0.11, relwidth=1/3, relheight=0.86)
# Feeding Label
GUI_FeedLabel=tk.Label(GUI_FeedFrame, text="Feeding Material", bg=RGB_Feeding_title, fg="white", font= font_medium, anchor="w")
GUI_FeedLabel.place(relx=0, rely=0, relwidth=1, relheight=0.14)
# Amount of material
GUI_FeedAmountLabel=tk.Label(GUI_FeedFrame, text='Qty',  fg="black",bg=RGB_Sections_bg, font= font_small_bold, anchor="w")
GUI_FeedAmountLabel.place(relx=0.1, rely=0.2, relwidth=0.15, relheight=0.15)
GUI_FeedAmount= tk.Entry(GUI_FeedFrame, font= font_small)
GUI_FeedAmount.place(relx=0.1, rely=0.35, relwidth=0.15, relheight=0.14)
# Unit of material
GUI_FeedUnitLabel=tk.Label(GUI_FeedFrame, text='Unit',  fg="black",bg=RGB_Sections_bg, font= font_small_bold, anchor="w")
GUI_FeedUnitLabel.place(relx=0.27, rely=0.2, relwidth=0.2, relheight=0.15)
GUI_FeedUnit= tk.Spinbox(GUI_FeedFrame, font= font_small)
GUI_FeedUnit.place(relx=0.27, rely=0.35, relwidth=0.2, relheight=0.14)
# Feed material
GUI_FeedMaterialLabel=tk.Label(GUI_FeedFrame, text='Material',  fg="black",bg=RGB_Sections_bg,  font= font_small_bold, anchor="w")
GUI_FeedMaterialLabel.place(relx=0.48, rely=0.2, relwidth=0.4, relheight=0.15)
GUI_FeedMaterial= tk.Entry(GUI_FeedFrame, font= font_small)
GUI_FeedMaterial.place(relx=0.48, rely=0.35, relwidth=0.4, relheight=0.14)
# Enter button
GUI_FeedInButton= tk.Button(GUI_FeedFrame, text= "Enter" , bg= 'white', command=_FeedMaterial, font= font_small) 
GUI_FeedInButton.place(relx=0.1, rely=0.55, relwidth=1-0.2, relheight=0.14)


### Graphs Frame
GUI_GraphicsCanvas= tk.Canvas(GUI_FRAME, bg='white')
GUI_GraphicsCanvas.place(relx= 0.205, rely= 0.47, relwidth= 1 - 0.21, relheight= 0.45 )
## Plot Area
#fig = plt.Figure(figsize=(15,15), dpi=100) #figure to hold plot
fig = plt.Figure(figsize=(3,4),dpi=80 * z) #figure to hold plot
ax = fig.add_subplot(111)
graph = FigureCanvasTkAgg(fig, master=GUI_GraphicsCanvas)
graph.get_tk_widget().place(x=2,y=2, relwidth=0.9, relheight=0.95)


# Hour button
GUI_24HourButton= tk.Button(GUI_GraphicsCanvas, text= "DAY" , bg= RGB_Graph_b1, command= partial(UpdatePlot,days=1,ax=ax ), font= font_medium) 
GUI_24HourButton.place(relx=1-0.15, rely=1*(1/6) , relwidth= 0.15, relheight=(1/6) )
# Week button
GUI_WeekButton= tk.Button(GUI_GraphicsCanvas, text= "Week" , bg= RGB_Graph_b2, command=partial(UpdatePlot,days=7,ax=ax ), font= font_medium) 
GUI_WeekButton.place(relx=1-0.15, rely=2*(1/6) , relwidth= 0.15, relheight=(1/6) )
# Month button
GUI_MonthButton= tk.Button(GUI_GraphicsCanvas, text= "Month" , bg= RGB_Graph_b2, command= partial(UpdatePlot,days=32,ax=ax ), font= font_medium) 
GUI_MonthButton.place(relx=1-0.15, rely=3*(1/6) , relwidth= 0.15, relheight=(1/6) )
# Update button
GUI_UpdateButton= tk.Button(GUI_GraphicsCanvas,relief=GROOVE, text= "Update" , bg= RGB_Graph_b2, command= partial(UpdatePlot,days=0,ax=ax ), font= font_medium) 
GUI_UpdateButton.place(relx=1-0.15, rely=5*(1/6) , relwidth= 0.15, relheight=(1/6) )



## Status Bar
GUI_BottomBar= tk.Canvas(GUI_FRAME, bg='DarkGray')
GUI_BottomBar.place(relx= 0, rely= 1- 0.04, relwidth= 1, relheight= 0.045 )
#SERIAL PORT
GUI_SerialPortLabel = tk.Label(GUI_BottomBar,text='PORT ',bg='DarkGray',font= font_small, anchor='e')
GUI_SerialPortLabel.place(relx=0, rely=0, relwidth= 0.05, relheight=1)
#
GUI_SerialPortValue = tk.Spinbox(GUI_BottomBar, values=com_arr, bg= 'white', font= font_small, command= _SerialPortChange)
GUI_SerialPortValue.place(relx=0.05,rely=0, relwidth= 0.1, relheight=1)
#ARDUINO STATUS
GUI_StatusInfo=tk.Label(GUI_BottomBar,bg= 'DarkGray', font= font_small,anchor='e')
GUI_StatusInfo.place(relx= 0.15, rely= 0, relwidth= 1-0.15, relheight= 1 )



UpdatePlot(selRange,ax)
SecondLoop()
MinuteLoop()

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
CSV.setup_set(f=CSV.SetupFile, SP=CSV.SP, TimeOn=CSV.TimeOn ,TimeOff=CSV.TimeOff, RPM=CSV.RPM, COM=com)


print('APP CLOSED')
sys.exit()