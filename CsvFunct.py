import csv
import os
from datetime import datetime
from pathlib import Path


# List to store values to read and write in CSV file
DesiredTemp = [0]
TimeOn = [0]
TimeOff = [0]
RPM = [0]
COM = [0]
Enable = [0]
Kp = [0]
Ki = [0]
Kd = [0]


# --- Path of CSV files and folders -------------------------------------------
#
# path of the main CSV folder where all Csv files are stored.
CsvFolder = '{}/{}'.format(Path(__file__).parent.absolute(), 'CSV')
# path of the Memory file
MemoryFile = '{}/{} '.format(CsvFolder, 'Memory.csv')
# path of the folder where the Csv files for every reactor is contained
ReactorFolder = [''] * 6  # Location of the reactor folder
#
# Name of the Csv file to register 'Reactor' temperatures for every reactor
TempReactorName = [''] * 6
# Name of the Csv file to register 'Heater' temperatures for every reactor
TempHeaterName = [''] * 6
# Name of the Csv file to register the Stirring information for every reactor
StirringInfoName = [''] * 6
# Name of the CSV file to register the Feeding material for every reactor
FeedingMaterialName = [''] * 6
# ------------------------------------------------------------------------


# Store the GUI configuration
#  When the programm is executed for the first time, a memory csv file will be
#  created with the default values for:
#     - Desired temperatures
#     - Stirring information
#     - PID controller parameters
#     - Serial communication port
#     - Enable status of reactor
#  Every time the application is closed, this function is going to be executed,
#  to store the current GUI configuration
def Memory_set(f='',
               DesiredTemp=[35] * 6,
               TimeOn=[10] * 6, TimeOff=[5] * 6, RPM=[30] * 6,
               Kp=[1] * 6, Ki=[2] * 6, Kd=[3] * 6,
               COM='--',
               Enable=[False]*6):

    data = [[''] * 6] * 15  # Data to be written in the file

    # Read folder data if it already exists
    if os.path.exists(f):
        r = csv.reader(open(f))  # Read Memory file
        data = list(r)
        data = [e for e in data if e]  # filter empty elements
    #

    # Modify values in the data array
    data[0] = DesiredTemp
    data[1] = TimeOn
    data[2] = TimeOff
    data[3] = RPM
    data[4] = Kp
    data[5] = Ki
    data[6] = Kd
    data[7] = [COM]
    data[12] = Enable

    # Write the values in the csv file
    with open(f, mode='w', newline='') as File:
        writer = csv.writer(File)
        writer.writerows(data)
# -----------------------------------------------------------------------------


# This function stores the name of the CSV files
# in the Memory csv file
def Memory_CSVnames(f, trn, thn, sin, fmn):

    # Read Memory.csv file
    r = csv.reader(open(f))
    data = list(r)
    data = [e for e in data if e]  # filter empty elements

    # Update the file names in Memory.csv
    data[8] = trn  # Reactor temperature CSV name
    data[9] = thn  # Heater temperature CSV name
    data[10] = sin  # Stirring info CSV name
    data[11] = fmn  # Fedding material CSV name
    with open(f, mode='w') as File:
        writer = csv.writer(File)
        writer.writerows(data)
# -----------------------------------------------------------------------------


# This function is used to get the previous configuration,
# when application starts
def Memory_get(file=''):

    global DesiredTemp, TimeOn, TimeOff
    global RPM, Kp, Ki, Kd, COM, Enable
    global TempReactorName, TempHeaterName
    global StirringInfoName, FeedingMaterialName

    # read Memory CSV file and get the values
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file)
        data = list(csv_reader)
        data = [e for e in data if e]  # filter empty elements

        # Asign value to global variables
        DesiredTemp = list(map(int, data[0]))
        TimeOn = list(map(int, data[1]))
        TimeOff = list(map(int, data[2]))
        RPM = list(map(int, data[3]))
        Kp = list(map(float, data[4]))
        Ki = list(map(float, data[5]))
        Kd = list(map(float, data[6]))
        COM = data[7][0]

        TempReactorName = list(data[8])
        TempHeaterName = list(data[9])
        StirringInfoName = list(data[10])
        FeedingMaterialName = list(data[11])

        Enable = list(data[12])
        for i in range(len(Enable)):  # Convert enable values to BOOLEAN
            Enable[i] = Enable[i] in ('true', 'True', '1')
# -----------------------------------------------------------------------------


# This function creates a log in the corresponding CSV file
#  ARGUMENTS:
#  header-> The header of the csv
#  v1-> value written on third column
#  v2-> value written on fourth column
#  v3-> value written on fifth column
#  v4-> value written of sixth column
def LOG(f, header='', v1='', v2='', v3='', v4=''):

    file = open(f, 'a')
    # today's date with format
    date = datetime.now()
    date = date.strftime('%Y-%m-%d %H:%M:%S')

    # If file does not exist yet, write the header
    if os.stat(f).st_size == 0:
        file.write(header)

    if v1 != '':
        file.write('\n' + str(date))
        file.write(',' + str(v1))
    if v2 != '':
        file.write(',' + str(v2))
    if v3 != '':
        file.write(',' + str(v3))
    if v4 != '':
        file.write(',' + str(v4))

    # file.write('\n')
    # file.flush()
    file.close()
# -----------------------------------------------------------------------------


# Create the CSV folders and files
def CSV_file_create():
    global ReactorFolder

    # today's date
    date = datetime.now()
    date = date.strftime('%Y-%m-%d')
    #

    # Create the main CSV folder when it does not exist---
    if not os.path.exists(CsvFolder):
        os.mkdir(CsvFolder)
    # ------------------------------

    # Create Memory file if it does not exist
    if not os.path.exists(MemoryFile):
        Memory_set(f=MemoryFile)
    # ------------------------------

    Memory_get(MemoryFile)  # Get the values stored in the memory file

    # Create a folder and csv file for each Reactor
    for i in range(6):

        # Reactor folder
        ReactorFolder[i] = '{}/Reactor_{}'.format(CsvFolder, i + 1)
        if not os.path.exists(ReactorFolder[i]):  # create reactor folder
            os.mkdir(ReactorFolder[i])
        # ------------------------

        # Reactor Temperature file
        if TempReactorName[i] == '':
            TempReactorName[i] = '{}-CSTR-{}-1.csv'.format(date, i + 1)
        if not os.path.exists(TempReactorName[i]):  # create file folder
            LOG(f='{}/{}'.format(ReactorFolder[i], TempReactorName[i]),
                header='Date,Reactor Temperature')
        # -------------------------------

        # Heater Temperature files
        if TempHeaterName[i] == '':
            TempHeaterName[i] = '{}-CSTR-{}-2.csv'.format(date, i + 1)
        if not os.path.exists(TempHeaterName[i]):  # create file folder
            LOG(f='{}/{}'.format(ReactorFolder[i], TempHeaterName[i]),
                header='Date,Heater Temperature')
        # -------------------------------

        # Stirring information file
        if StirringInfoName[i] == '':
            StirringInfoName[i] = '{}-CSTR-{}-3.csv'.format(date, i + 1)
        if not os.path.exists(StirringInfoName[i]):  # create file folder
            LOG(f='{}/{}'.format(ReactorFolder[i], StirringInfoName[i]),
                header='Date,RPM,ON,OFF')
        # -------------------------------

        # Feeding material Temperature file
        if FeedingMaterialName[i] == '':
            FeedingMaterialName[i] = '{}-CSTR-{}-4.csv'.format(date, i + 1)
        if not os.path.exists(FeedingMaterialName[i]):  # create file folder
            LOG(f='{}/{}'.format(ReactorFolder[i], FeedingMaterialName[i]),
                header='Date,Qty,Unit,Material')
        # -------------------------------

    # Save csv file name for every reactor in Memory file
    Memory_CSVnames(f=MemoryFile,
                    trn=TempReactorName, thn=TempHeaterName,
                    sin=StirringInfoName, fmn=FeedingMaterialName)
# ----------------------------------------------------


CSV_file_create()  # Create the CSV folder with all the files inside
Memory_get(MemoryFile)  # Get configuration status

#
