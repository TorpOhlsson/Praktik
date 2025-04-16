import csv
import statistics

def dataman(cvs_dict):
    with open(f"{cvs_dict["filename"]}", "r") as file:
        print(f"DATA FRA {cvs_dict["filename"]}")
        
        reader = csv.reader(file, delimiter = ",")
        measurement_list = [] #list of all measurements from csv
        cmd_list = []   
        counter = 0
        average_measurement_list = []
        for row in reader:
            #print(row)
            if row[2] == "mA":

                if row[3] not in  cmd_list:
                    cmd_list.append(row[3])
                measurement_list.append(row)
        
        file.seek(0)        
        with open(f"{cvs_dict["directory"]}\\masters\\{cvs_dict["decoder"]} master.csv","a") as masterfile:
            writer = csv.writer(masterfile, delimiter=",",lineterminator="\n")
            for row in reader:
                writer.writerow(row)
        

        for cmd in cmd_list:
            trigger_list = []
            
            first = True
            switchparam = ""
            for i, character in reversed(list(enumerate(cmd))): #iterates over the requests and saves the switch params
                if character == "=" and first == True:
                    for character in range(i+1,len(cmd)):
                        switchparam += cmd[character]
                    first = False
                    break

            average_measurement_list.append([cmd,switchparam])

            avg_count = 0
            for measurement in measurement_list:


                if measurement[3] == cmd:
                    if cvs_dict["type"] == 6:
                        nylist = [measurement[0:4]]
                        Firstvalue = False 
                        Previousvalue = 9999
                        
                        for i, val in enumerate(measurement): #trigger that shows when the inrush begins
                            if i > 5 and int(val) > int(Previousvalue) + 5 and Firstvalue == False: #
                                trigger_list.append(i)
                                Firstvalue = True    
                            Previousvalue = val
            if cvs_dict["type"] == 6: #finds the mode trigger to use for every measurement for that specific switch parameter
                Trigger = statistics.mode(trigger_list)
            for measurement in measurement_list:
                if measurement[3] == cmd:
                    if cvs_dict["type"] == 6:
                        nylist = measurement[0:5]               
                        for snippet in range(Trigger-10, Trigger+10):
                                    if snippet < 5 or snippet >= len(measurement):

                                        nylist = ["no","no"]
                                        print("faulty trigger disregarding measurement",measurement)
                                        avg_count -= 1
                                        break
                                    else:

                                        nylist.append(measurement[snippet])
                        measurement = nylist
                    avg_count += 1
                    position = 1

                    for x in range(5, len(measurement)):
                    
                        if len(average_measurement_list[counter]) < x-2:
                            average_measurement_list[counter].append(0)
                        position += 1

                        average_measurement_list[counter][position] += int(measurement[x])
            for tal in range(2, len(average_measurement_list[counter])): 
                average_measurement_list[counter][tal] = int(average_measurement_list[counter][tal]/avg_count)       
            counter +=1

   
        #inserts the
        headers = ["inrush",cvs_dict["decoder"] , "gennemsnit"]
        for gennemsnit in average_measurement_list:
            for g in headers:
                gennemsnit.insert(0,g)

       
        

    tests = False
    #test_values = [["test","test",filename["decoder"],"test","test","linevoltage","aHigh","att","inrush shoulder", "inrush cycle", "hold cycle","verify cycle","verify shoulder", "bHigh"]]
    test_average_list = ["gennemsnit","gennemsnit", cvs_dict["decoder"], "gennemsnit","test"]

    
    new_average2 = []
    for each in range(5,len(test_average_list)):
            new_average2.append(0)
            test_average_list[each] =  "{0:.2f}".format(sum(test_average_list[each])/len(test_average_list[each]))
            new_average2[each-5] = test_average_list[each]
    
    
    with open(f"{cvs_dict["directory"]}/{cvs_dict["datetime"]} summary.csv", mode = "a") as file:
        writer = csv.writer(file, delimiter = ",")
        test_average = [cvs_dict["decoder"],"test average"]
        for hver in new_average2:
            test_average.append(hver)
        writer.writerows(average_measurement_list)
        if tests == True:
            writer.writerow(test_average)
    

if __name__ == "__main__": #indtast manuelt en fil og dens attributer for test
    liste =  {"filename":"C:\\Program Files (x86)\\Crysberg\\log\\2025-04-03 1628\\raw\\decoder 152_2025-04-04 0803.csv", "decoder":152,"directory" : "C:\\Program Files (x86)\\Crysberg\\log\\2025-04-03 1628", "datetime" : "2025-04-03 1628","type":6} 
    dataman(liste)


