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

