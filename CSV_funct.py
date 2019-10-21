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




def LOG(r=0,header="Var1,Var2"+"\n"):

    file = open("LOG_.csv", "a")

    if os.stat("LOG_.csv").st_size == 0:
        file.write(header)

    now = datetime.now()
    file.write(str(now)+","+str(r)+","+str(-r)+","+str(r-10)+","+str(r+5)+","+str(r*r)+"\n")
    file.flush()
    file.close()
    #time.sleep(.1)

i=0
header=("Time,Temperature\n")
while True:
    i=i+1
    LOG(r=0,header=header)
    LOG(r=1,header=header)
    LOG(r=2,header=header)
    LOG(r=3,header=header)
    print(i)
