import csv
import os
from datetime import datetime
from pathlib import Path

# VARIABLES
SP = [0]    # store the SETPOINT
TimeOn = [0]
TimeOff = [0]
RPM = [0]
COM = [0]
Enable = [0]


# --- Path of CSV files and folders -----------------------------------
# path of the main CSV folder where all Csv files are stored.
CsvFolder = '{}/{}'.format(Path(__file__).parent.absolute(), "CSV")
# path of the folder where the Csv files for every reactor is contained
ReactorFolder = [""] * 6  # Location of the reactor folder
# path of the Setup file
SetupFile = '{}/{} '.format(CsvFolder, "Setup.csv")

# Name of the Csv file to register 'Reactor' temperatures for every reactor
TempReactorName = [""] * 6
# Name of the Csv file to register 'Heater' temperatures for every reactor
TempHeaterName = [""] * 6
# Name of the Csv file to register the Stirring information for every reactor
StirringInfoName = [""] * 6
# Name of the CSV file to register the Feeding material for every reactor
FeedingMaterialName = [""] * 6
# ------------------------------------------------------------------------


# This function stores the current configuration
# in the csv Setup file
def setup_set(f='', SP=[35] * 6, TimeOn=[10] * 6, TimeOff=[5] * 6,
              RPM=[30] * 6, Kp=[1] * 6, Ki=[2] * 6, Kd=[3] * 6,
                Enable=[1, 0, 0, 0, 0, 0], COM='COM15'):

    data = [[''] * 6] * 15  # Data to be written in the file

    if os.path.exists(f):
        r = csv.reader(open(f))  # Read setup file
        data = list(r)

    # Modify values in the data array
    data[0] = SP
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
# in the setup csv file
def setup_CSVnames(f, trn, thn, sin, fmn):
    r = csv.reader(open(f))  # Here your csv file
    data = list(r)
    data[8] = trn  # Reactor temperature CSV name
    data[9] = thn  # Heater temperature CSV name
    data[10] = sin  # Stirring info CSV name
    data[11] = fmn  # Fedding material CSV name

    with open(f, mode='w', newline='') as File:
        writer = csv.writer(File)
        writer.writerows(data)
# -----------------------------------------------------------------------------


# This function is used to get the previous configuration,
# when application starts
def setup_get(file=''):

    with open(file) as File:

        global SP, TimeOn, TimeOff, RPM, Kp, Ki, Kd, COM, Enable, TempReactorName, TempHeaterName, StirringInfoName, FeedingMaterialName

        data = []  # Data to be written in the file

        reader = csv.reader(File, delimiter=',')
        data = list(reader)

        # Asign value to global variables
        SP = list(map(int, data[0]))
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


# This function creates a log in the corresponding
# CSV file
# ARGUMENTS:
# header-> The header of the csv
# v1-> value written on third column
# v2-> value written on fourth column
# v3-> value written on fifth column
# v4-> value written of sixth column
def LOG(f, header='', v1='', v2='', v3='', v4=''):

    file = open(f, "a")
    # today's date with format
    date = datetime.now()
    date = date.strftime("%Y-%m-%d %H:%M:%S")

    if os.stat(f).st_size == 0:
        file.write(header)

    if v1 != '':
        file.write(str(date))
        file.write("," + str(v1))
    if v2 != '':
        file.write("," + str(v2))
    if v3 != '':
        file.write("," + str(v3))
    if v4 != '':
        file.write("," + str(v4))

    file.write('\n')
    file.flush()
    file.close()
# -----------------------------------------------------------------------------


# CREATE CSV FILES IF THEY DO NOT EXIST
def CSV_file_create():

    date = datetime.now()
    date = date.strftime("%Y-%m-%d")  # today's date

    for i in range(6):
        ReactorFolder[i] = '{}/Reactor_{}'.format(CsvFolder, i + 1)

    if not os.path.exists(CsvFolder):
        os.mkdir(CsvFolder)

        # Create the folder for every reactor
        for i in range(6):
            # Create reactor folder and 4 CSV files
            if not os.path.exists(ReactorFolder[i]):
                os.mkdir(ReactorFolder[i])

                # Reactor Temperature file
                TempReactorName[i] = '{}-CSTR-{}-1.csv'.format(date, i + 1)
                LOG(f='{}/{}'.format(ReactorFolder[i], TempReactorName[i]),
                    header='Date,Reactor Temperature')

                # Heater Temperature file
                TempHeaterName[i] = '{}-CSTR-{}-2.csv'.format(date, i + 1)
                LOG(f='{}/{}'.format(ReactorFolder[i],
                                     TempHeaterName[i]), header='Date,Heater Temperature')

                # Stering info file
                StirringInfoName[i] = '{}-CSTR-{}-3.csv'.format(date, i + 1)
                LOG(f='{}/{}'.format(ReactorFolder[i],
                                     StirringInfoName[i]), header='Date,RPM,ON,OFF')

                # Feeding material file
                FeedingMaterialName[i] = '{}-CSTR-{}-4.csv'.format(date, i + 1)
                LOG(f='{}/{}'.format(ReactorFolder[i], FeedingMaterialName[
                    i]), header='Date,Qty,Unit,Material')

        # Create Setup file
        setup_set(f=SetupFile)
        # Save the CSV names in setup file
        setup_CSVnames(f=SetupFile, trn=TempReactorName, thn=TempHeaterName,
                       sin=StirringInfoName, fmn=FeedingMaterialName)
# -----------------------------------------------------------------------------


CSV_file_create()
# Get last configuration status
setup_get(SetupFile)
