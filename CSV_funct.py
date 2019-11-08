import csv
import os
import time 

from datetime import datetime


global SP, TimeOn, TimeOff,COM



# THIS FUNCTION IS USED TO STORE THE CURRENT CONFIGURATION, WHEN THE APPLICATION IS CLOSED
def config_save(f='',SP=[0]*6,TimeOn=[0]*6,TimeOff=[0]*6,RPM=0,COM='COM13'):
    with open(f, mode='w',newline='') as File:
        
        writer = csv.writer(File)
        writer.writerow(SP)     # SP
        writer.writerow(TimeOn) # Ton
        writer.writerow(TimeOff)# Ton
        writer.writerow(RPM)    # RPM
        writer.writerow([COM])  # com


# THIS FUNCTION IS USED TO GET PREVIOUS CONFIGURATION, WHEN THE APPLICATION STARTS
def config_read(file=''):
    results = []

    with open(file) as File:
        reader =  csv.reader(File, delimiter=',')
        
        for line in reader:
            results.append(line)

        global SP, TimeOn, TimeOff, RPM, COM
        SP = list(map(int, results[0] ))
        TimeOn = list(map(int, results[1] ))
        TimeOff = list(map(int, results[2] ))
        RPM = list(map(int, results[3] ))
        COM = results[4][0]




# THIS FUNCTION IS USED TO SAVE A REGISTER IN A CSV FILE
def LOG(File,header,Date,v1='',v2='',v3='',v4=''):
    #"LOG_.csv"
    file = open(File, "a")

    date = time.strftime("%Y-%m-%d %H:%M.%S", time.gmtime(Date))

    if os.stat(File).st_size == 0:
        file.write(header+'\n')

    file.write(str(date))
    file.write("," + str(v1))
    if v2 != '': file.write("," + str(v2))
    if v3 != '': file.write("," + str(v3))
    if v4 != '': file.write("," + str(v4))
    file.write('\n')
   


    file.flush()
    file.close()



