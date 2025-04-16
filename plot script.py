import matplotlib.pyplot as plt
import csv
import numpy
from math import floor,ceil
import tkinter as tk
from tkinter.filedialog import askopenfilename
tk.Tk().withdraw() # part of the import if you are not using other tkinter functions

fn = askopenfilename(initialdir="C:\\Program Files (x86)\\Crysberg\\log") #open file explorer in the log directory
print("user chose", fn)
loft = True
decoder_list = [] #list of decoders that is used as keys for the master_dict
master_dict = {} #dict that holds every decoder and has their measurement for each switch param
mk2param = [] #switch parameters for mk2
mk3param = [] #switch parameters for mk3.2
#liste =  {"filnavn":"C:\\Program Files (x86)\\Crysberg\\log\\2025-03-18 1412\\2025-03-18 1412summary.csv", "decoder":122,"directory" : "C:\\Program Files (x86)\\Crysberg\\log\\2025-03-18 1412", "datetime" : "2025-03-06 1042","type":6} 

average = input("Average for decoder type? ")

if average.lower() == 'yes':
    average = True
else:
    average = False



##############################################################################################################################################################################################
###FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE READ FILE###
##############################################################################################################################################################################################
with open(fn, mode = "r") as file: #opens selected file
    reader = csv.reader(file, delimiter=",")
    maxread = 0 # the maximum measurement
    minread = 9999 # the minimum measurement
    
    for row in reader:
        #print(row[4])
        if len(row) > 2: #discards any empty or non inrush rows
            if row[2] == "mA" or row[2] == "inrush":
                if row[1] not in decoder_list: #checks if the decoder is already added to the list
                    decoder_list.append(row[1]) #adds decoders to the list
                

                if row[4] not in mk2param and len(row[4]) == 4: #checks if the switch params already are in the list
                    mk2param.append(row[4]) #adds the switch params to the list 
                elif row[4] not in mk3param and len(row[4]) == 6 : #checks if the switch params already are in the list
                    mk3param.append(row[4]) #adds the switch params to the list

                for x in range(5,len(row)): #iterates over every measurement and saves the lowest measurement
                    if row[x]!= "" and int(row[x]) < minread: 
                        minread = int(row[x]) 


    decoder_list.sort()
    switchparam_list = [mk2param,mk3param] #
    for decoders in decoder_list:
        measurement_dict = {}
        measurement_list = [] #temporary list of measurement for a specific decoder
        switchparam_pointer = 0 #counter that points at measurement from 
        for decodermk in switchparam_list:
            
            ##############################################################################################################################
            """if average == True:
                test = measurement_dict[decodermk]
            elif average == False:
                test = measurement_dict[switchparam]"""
            ##############################################################################################################################

            for switchparam in decodermk:
                file.seek(0)
                avg_counter = 0
                
                measurement_dict[switchparam] = []
                #print(decodermk,switchparam)
                for row in reader:

                    position = 0
                    
                    if len(row) < 2:
                        pass
                
                    elif row[4] == switchparam and row[1] == decoders:
                        
                        
                        for x in range(5,len(row)):
                            
                            if len(measurement_dict[switchparam]) < x-4 and row[x] != "":
                                measurement_dict[switchparam].append(0)
                            
                            if row[x] != "":
                                measurement_dict[switchparam][position] += int(row[x])
                            position += 1
                            if row[x] != "" and int(row[x]) > maxread:
                                maxread = int(row[x])
                            
                        avg_counter +=1
                if measurement_dict[switchparam] == []:
                    measurement_dict.pop(switchparam)
                
                
                if switchparam in measurement_dict:
                    for measurement in range(0, len(measurement_dict[switchparam])):
                        
                        measurement_dict[switchparam][measurement] = int(measurement_dict[switchparam][measurement]/avg_counter) - minread

                switchparam_pointer += 1
       
        
        master_dict.update({decoders : measurement_dict})
        
        ########################################################################
print(master_dict)
if average == True:
    average = {"mk32":{},"mk2":{},"mk3f13":{},"mk3f6":{}}
    mk2 = range(100,130)
    mk32 = range(1200,1230)
    mk3f13 = range(12000,12030)
    mk3f6 = range(600,610)
    mktypes = ["mk32","mk2","mk3f13","mk3f6"]
    for types in average:
        if types == "mk3f13":
            ranges = mk3f13
            params = switchparam_list[1]
        elif types == "mk3f6":
            ranges = mk3f6
            params = switchparam_list[1]
        elif types == "mk32":
            ranges = mk32
            params = switchparam_list[0]
        elif types == "mk2":
            ranges = mk2
            params = switchparam_list[0]
        for para in params:
            count = 0
            average[types][para] = []
            for i in ranges:
                if str(i) in master_dict:
                    try:
                        for t, measurement in enumerate(master_dict[str(i)][para]):
                            if len(average[types][para]) < len(master_dict[str(i)][para]):
                                average[types][para].append(0)
                            average[types][para][t] += measurement
                            #print(average,measurement,t)
                        count += 1
                    except Exception as e:
                        print(master_dict[str(i)])
                        print(e) 
            for each, value in enumerate(average[types][para]):
                average[types][para][each] = int(value/count)
    master_dict = average
    decoder_list = mktypes



##############################################################################################################################################################################################
###PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER PLOTTER ###
##############################################################################################################################################################################################
print(switchparam_list)
print(master_dict)
for dtype in switchparam_list:
    if dtype != []:
        fig = plt.figure()

        if len(dtype) <= 3:
            column = len(dtype)
        else:
            column = 3


        axes = fig.subplots(ceil(len(dtype)/3),column) 
        
        for i, switchparam in enumerate(dtype): 
            if len(dtype) == 1:
                placement = axes
            elif len(dtype) <= 3 and len(dtype) > 1:
                placement = axes[i%3]
            else:
                placement = axes[floor(i/3),i%3]
            for decoders in decoder_list:

                if switchparam in master_dict[decoders] and master_dict[decoders][switchparam] != []:
                    x = numpy.arange(1,len(master_dict[decoders][switchparam])+1,1)
                    placement.plot(x,master_dict[decoders][switchparam],label = f"decoder {decoders}")
                    placement.axis((1,len(x),-10,(maxread-minread)*1.2))
            placement.title.set_text(dtype[i])
            placement.legend()
            
            placement.grid()            
        plt.show()
