import csv
import os
from time import *
from datetime import datetime
from pathlib import Path



global SP, TimeOn, TimeOff, RPM, COM

CsvFolder= '{}/{}'.format(Path(__file__).parent.absolute(),"CSV")
SetupFile = '{}/{} '.format( CsvFolder,"Setup.csv")


TempReactorName =[""]*6
TempHeaterName =[""]*6


ReactorFolder = [""]*6
StirringInfoName =[""]*6
FeedingMaterialName =[""]*6
date = strftime("%Y-%m-%d", gmtime(time()))








# THIS FUNCTION IS USED TO STORE THE CURRENT CONFIGURATION, WHEN THE APPLICATION IS CLOSED
def setup_set(f='',SP=[35]*6,TimeOn=[10]*6,TimeOff=[5]*6,RPM=[30]*6, P=[1]*6, I=[2]*6, D=[3]*6,COM='COM13'):
   
    data = [['']*6]*15

    if os.path.exists(f):
        r = csv.reader(open(f)) # Here your csv file
        data = list(r)

    data[0] = SP
    data[1] = TimeOn
    data[2] = TimeOff
    data[3] = RPM
    data[4] = P
    data[5] = I
    data[6] = D
    data[7] = [COM]*6
    

    with open(f, mode='w',newline='') as File:
        writer = csv.writer(File)
        writer.writerows(data)
     #   print(data)

def setup_CSVnames(f, trn, thn, sin, fmn):
    r = csv.reader(open(f)) # Here your csv file
    data = list(r)
    data[8] = trn
    data[9] = thn
    data[10] = sin
    data[11] = fmn
    
    with open(f, mode='w',newline='') as File:
        writer = csv.writer(File)
        writer.writerows(data)
        #print(data)
    #print(lines)



# THIS FUNCTION IS USED TO GET PREVIOUS CONFIGURATION, WHEN THE APPLICATION STARTS
def setup_get(file=''):
    results = []

    with open(file) as File:

        global SP, TimeOn, TimeOff, RPM, P,I,D, COM, TempReactorName, TempHeaterName, StirringInfoName, FeedingMaterialName
        data = []

        reader =  csv.reader(File, delimiter=',')
        for line in reader:
            data.append(line)

        SP = list(map(int, data[0]))
        TimeOn = list(map(int, data[1] ))
        TimeOff = list(map(int, data[2] ))
        RPM = list(map(int, data[3] ))
        P = list(map(int, data[4] ))
        I = list(map(int, data[5] ))
        D = list(map(int, data[6] ))

        COM = data[7][0]

        TempReactorName = list( data[8] )
        TempHeaterName = list( data[9] )
        StirringInfoName = list(data[10] )
        FeedingMaterialName = list(data[11] )


# THIS FUNCTION IS USED TO SAVE A REGISTER IN A CSV FILE
def LOG(f,header='',v1='',v2='',v3='',v4=''):
    #"LOG_.csv"
    file = open(f, "a")
    date = strftime("%Y-%m-%d %H:%M:%S", gmtime(time()))

    if os.stat(f).st_size == 0:
        file.write(header+'\n')

    if v1 != '':
        file.write(str(date))
        file.write("," + str(v1))
    if v2 != '': file.write("," + str(v2))
    if v3 != '': file.write("," + str(v3))
    if v4 != '': file.write("," + str(v4))
    file.write('\n')
    file.flush()
    file.close()





# CREATE CSV FOLDER AND FILES ID THEY DO NOT EXIST
for i in range(6):
    ReactorFolder[i] = '{}/Reactor_{}'.format( CsvFolder,i+1)

if not os.path.exists(CsvFolder):
    os.mkdir(CsvFolder)

    # Create the folder for every reactor
    for i in range(6):
        #Create reactor folder and 4 CSV files
        if not os.path.exists(ReactorFolder[i]):
            os.mkdir(ReactorFolder[i])
            
            # Reactor Temperature file
            TempReactorName[i] = '{}-CSTR-{}-1.csv'.format(date ,i+1)
            LOG(f ='{}/{}'.format(ReactorFolder[i],TempReactorName[i]) , header = 'Date,Reactor Temperature' )
            
            # Heater Temperature file
            TempHeaterName[i] = '{}-CSTR-{}-2.csv'.format(date ,i+1)
            LOG(f ='{}/{}'.format(ReactorFolder[i],TempHeaterName[i]) , header = 'Date,Heater Temperature' )
            
            # Stering info file
            StirringInfoName[i] ='{}-CSTR-{}-3.csv'.format(date ,i+1)
            LOG(f ='{}/{}'.format(ReactorFolder[i],StirringInfoName[i]) , header = 'Date,RPM,ON,OFF' )
            
            # Feeding material file
            FeedingMaterialName[i] = '{}-CSTR-{}-4.csv'.format(date ,i+1)
            LOG(f ='{}/{}'.format(ReactorFolder[i],FeedingMaterialName[i]) , header = 'Date,Qty,Unit,Material' )

    # Create Setup file 
    setup_set(f = SetupFile)
    # Save the CSV names in setup file
    setup_CSVnames(f = SetupFile,trn= TempReactorName, thn= TempHeaterName, sin= StirringInfoName, fmn= FeedingMaterialName)


# Get last configuration status
setup_get(SetupFile) 
#print(SP)
# print(TimeOn)
# print(TimeOff)
# print(COM)
print(P)
print(I)
print(D)
# print(TempHeaterName)
# print(TempReactorName)
# print(StirringInfoName)
# print(FeedingMaterialName)

#####################################################################



#REWRITE DATA
# r = csv.reader(open('test.csv')) # Here your csv file
# lines = list(r)
# print(lines)
# lines[1][1] = 1000
# print ( lines ) 






