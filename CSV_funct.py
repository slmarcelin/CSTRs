import csv

global SP, TimeOn, TimeOff,COM

def config_save(f='',SP=[0]*6,TimeOn=[0]*6,TimeOff=[0]*6,COM='COM13'):
    with open(f, mode='w',newline='') as File:
        
        writer = csv.writer(File)
        writer.writerow(SP)# SP
        writer.writerow(TimeOn)# Ton
        writer.writerow(TimeOff)# Ton
        writer.writerow([COM])# com

def config_read(file=''):
    results = []

    with open(file) as File:
        reader =  csv.reader(File, delimiter=',')
        
        for line in reader:
            results.append(line)

        global SP, TimeOn, TimeOff,COM
        SP = list(map(int, results[0] ))
        TimeOn = list(map(int, results[1] ))
        TimeOff = list(map(int, results[2] ))
        COM = results[3][0]



import os
import time 
from time import sleep
from datetime import datetime


def LOG(File,header,Date,v1='',v2='',v3='',v4=''):
    #"LOG_.csv"
    file = open(File, "a")


    if os.stat(File).st_size == 0:
        file.write(header+'\n')

    file.write(str(Date))
    file.write("," + str(v1))
    if v2 != '': file.write("," + str(v2))
    if v3 != '': file.write("," + str(v3))
    if v4 != '': file.write("," + str(v4))
    file.write('\n')
   





    file.flush()
    file.close()





debug=False
if debug:
    i=0
    header=("Time,Temperature\n")
    while False:
        i=i+1
        LOG(r=0,header=header)
        LOG(r=1,header=header)
        LOG(r=2,header=header)
        LOG(r=3,header=header)
        print(i)
