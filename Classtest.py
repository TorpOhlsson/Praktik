import logging.handlers
from Interface import InterFace
from time import sleep
import csv
import logging
import os
from datetime import datetime
import shutil
import requests
from dataman import dataman
import regReader
import random

connection = False 
host = "SRC-IF-LOFT2"  #"cry-citel192.168.1.222SRC-IF-LOFT2" 
interface = InterFace(hostname=host) #, timeout = 9, session= s
logSet = False
log = logging.getLogger("root") 
automate = True #bool that makes the program loop if True or stop after each decoder if False
number_of_tests = 1 #how many time the inrush measurement is done for each switch parameter
reg = ["e101"] #registers to read
mk2param = ["d2a5","c2a5","92a5","82a5"] #d begge holds, c kun inrush, 9 kun hold, 8 ingen adjust "dea5","cea5",
mk2lutype = 6 #rainbird golf lutype
mk3lutype = 4 #mk3 lutype
number_of_random_on = 10 #How many decoders that it tries to turn on continuously per full cycle
###########################################################################################################################
#CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV    CSV   
###########################################################################################################################
"""function that writes a CSV document with inrush measurements and mk3 test functions"""
def csvskriver(decoder_reading): 
    csvrow = []
    keys = ["op", "DecAddr", "unit" ,"cmd","switchparam","result"]
    test_key = ["luVoltage","aHigh","att","inrushShoulderWidth","inrushCycleCount",
                "holdCycleBase","verifyCycleCount","verifyShoulderWidth","bHigh"]
    if decoder_reading["unit"] == "various": #if its a test call it adds the appropriate
        for each_key in test_key:
            keys.append(each_key)
    for k in keys: #iterates over the keys and writes a row with it
         try:
            if len(str(decoder_reading[k])) > 37 and decoder_reading[k][0] != "h":
                for measurement in decoder_reading[k]:
                    csvrow.append(measurement)
            else:
                #print(k+str(len(i[k])))
                csvrow.append(decoder_reading[k])
            
         except Exception as e:
            print(f"{k} not found")
            print(e)
            csvrow.append("")
    
        
    writer.writerow(csvrow)
    if "verifysum" in decoder_reading:
        csvrowtwo = []

        keys = ["op", "DecAddr", "unit" ,"cmd","switchparam","verifysum"]
        for k in keys:
            if k == "unit":
                csvrowtwo.append("verifysum")
            else:
                csvrowtwo.append(decoder_reading[k])
        writer.writerow(csvrowtwo)

###########################################################################################################################
#LOGGING    LOGGING    LOGGING    LOGGING    LOGGING    LOGGING    LOGGING    LOGGING    LOGGING    LOGGING    LOGGING    
###########################################################################################################################
grey = "\x1b[38;20m"
blue = "\x1b[38;5;69m"
yellow = "\x1b[33;20m"
red = "\x1b[31;20m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"

class CustomFormatter(logging.Formatter):
    """Sets format for logger in terminal window"""

    msg = "%(message)s "

    FORMATS = {
        logging.DEBUG: blue + msg + reset,
        logging.INFO: grey + msg + reset,
        logging.WARNING: yellow + msg + reset,
        logging.ERROR: red + msg + reset,
        logging.CRITICAL: bold_red + msg + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomFormatterDebug(logging.Formatter):
    """Sets format for logger written to a file"""

    msg = "%(asctime)s - %(levelname)-8s - [%(filename)s:%(lineno)d] - %(message)s "

    FORMATS = {
        logging.DEBUG: blue + msg + reset,
        logging.INFO: grey + msg + reset,
        logging.WARNING: yellow + msg + reset,
        logging.ERROR: red + msg + reset,
        logging.CRITICAL: bold_red + msg + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setLogger(termdebug, filepath):
    """function used to get logger options"""
    log.setLevel(logging.DEBUG)
    logfile = logging.FileHandler(filepath, mode="w")
    logfile.setLevel(logging.DEBUG)
    logfileformat = logging.Formatter(
        "%(asctime)s,%(msecs)03d; %(levelname)-8s; %(filename)s; %(lineno)d; %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    logfile.setFormatter(logfileformat)
    log.addHandler(logfile)

    # create console handler with a higher log level
    term = logging.StreamHandler()
    if termdebug:
        term.setLevel(logging.DEBUG)
        term.setFormatter(CustomFormatterDebug())
        log.addHandler(term)

    else:
        term.setLevel(logging.INFO)
        term.setFormatter(CustomFormatter())
        log.addHandler(term)
    log.debug(("logfile path set to {} ").format(filepath))
    return log
    
def setnewloggerfile(clone_last: bool, new_log_file: str):
    """changes logger file"""
    global log
    log_file = None
    handler = None
    # assumes only 1 filehandler exists
    for handler in log.__dict__["handlers"]:
        if handler.__class__.__name__ == "FileHandler":
            log_file = handler.baseFilename
            break

    log.debug(
        "changing logfile path from {} to {}, copy content {}".format(
            log_file, new_log_file, clone_last
        )
    )
    log.removeHandler(handler)
    if clone_last:
        shutil.copyfile(log_file, new_log_file)

    logfile = logging.FileHandler(os.path.abspath(new_log_file), mode="a")
    logfile.setLevel(logging.DEBUG)
    logfileformat = logging.Formatter(
        "%(asctime)s,%(msecs)03d; %(levelname)-8s; %(filename)s; %(lineno)d; %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    logfile.setFormatter(logfileformat)
    log.addHandler(logfile)

###########################################################################################################################


def mk3_test(addr): 
    """function that calls a inrush measurement for a mk3 and a test"""
    global fail
    maxretries = 0
    while maxretries < 2:
        mk3 = interface.measurement(addr)
        interface.lu_off(addr,verify=True)
        if mk3["result"] == {'error': {'code': 3000, 'msg': 'line unit failure detected'}}:
            mk3 = interface.measurement(addr)
            fail = True
            maxretries += 1
        else:
            log.info("result of measurement for decoder " + str(mk3["DecAddr"]) + " is " + str(mk3["result"]))
            fail = False   
            maxretries = 2
        csvskriver(mk3)

        mk3 = interface.test_function(i)
        log.info("result of test function for decoder " + str(mk3["DecAddr"]) + " is " + str(mk3["result"]))
    csvskriver(mk3)

def mk2_test(addr, switchparam:str="default"): 
    """function that calls a inrush measurement for a mk2"""
    global fail
    maxretries = 0
    while maxretries < 2:
        mk2 = interface.measurement(addr,switchparam)
        interface.lu_off(addr,verify=True)
        if mk2["result"] == {'error': {'code': 3000, 'msg': 'line unit failure detected'}}:
            log.error("result of measurement for decoder " + str(mk2["DecAddr"]) + " is " + str(mk2["result"]))
            fail = True
            maxretries +=1
        else:
            log.info("result of measurement for decoder " + str(mk2["DecAddr"]) + " is " + str(mk2["result"]))
            fail = False
            maxretries = 2
        if "verifysum" in mk2:
            log.info("verifysum is " + str(mk2["verifysum"]))
    csvskriver(mk2)


#function that saves the decoder adresses through discover, manual input or tester.csv if set to auto
def read_and_write_addresses(): 
    """function that saves the discovered addresses in a temporary list and reads registers for mk3.2 addresses if automate is True it will also read 'tester.csv' for mk2 addresses"""
    address_list = []
    
    if automate == True:
        with open('tester.csv', mode = 'r') as file:
            reader = csv.reader(file, delimiter= ',', lineterminator = '\n')
            for row in reader:
                if row[0].isnumeric() == True:
                    dict2 = {"addr": row[0] , "type": mk2lutype}
                    address_list.append(dict2) 
    elif mk2 == "":
        pass
    else:
        interface.decoders.append({"addr": mk2 ,"type": mk2lutype})
    print(address_list)
    temp_address_list = []
    with open('addresses.csv', mode = 'w') as file:
        writer = csv.writer(file, delimiter= ';',lineterminator = '\n')
        header = ["mk2","mk3"]
        writer.writerow(header)
        for i in address_list: # writes list of mk2 decoders
            y = [i["addr"],"None"]
            writer.writerow(y)
            dict1 = i
            temp_address_list.append(dict1)
        for i in interface.decoders:
            if i["type"] != 6:    
                i = int(i["addr"])
                firmread = regReader.readSomeRegisters(host, ["e011"], i)
                log.info(f"Read values out of {firmread}")
                
                if firmread == ['0C']:
                    print(str(i)+" is a firmware 12")
                    r = regReader.readSomeRegisters(host, reg, i)
                    log.info(f"Read {len(r)} values out of {regReader.countRegisterPositions(reg)} : {r}")
                    number = int(r[0]+r[1],16)
                    dict = {"addr": number, "type":6}
                    writer.writerow([number,i])
                elif firmread == ['06']:
                    dict = {"addr": i, "type": mk3lutype} 
                    writer.writerow(["None",i])
                """first = i
                last = i
                while first > 100: # Find the first two digits
                    first = int(first /10)

                if len(str(last)) > 4:
                    last = "{:02d}".format(last % 100)#Finds the last digit
                elif len(str(last)) <= 4:
                    last = last % 10
                number = int(str(first)+str(last)) #combines the first two and last digits

                if first == 12:
                    dict = {"addr": number, "type":6}
                    writer.writerow([number,i])
                elif first == 60:
                    dict = {"addr": i, "type": mk3lutype} 
                    writer.writerow(["None",i])"""
                temp_address_list.append(dict)
            else:
                pass
        for i in temp_address_list:
                if i not in interface.decoders:
                    interface.decoders.append(i)
        for i in interface.decoders:
            if i["type"] == 6:
                log.info(interface.add_mk2(i["addr"]))


###########################################################################################################################



if __name__ == '__main__':
    dt = datetime.now()
    dt = dt.strftime("%Y-%m-%d %H%M")
    directory_name  = f"log/{dt}"
    log_name = f"{directory_name}/Test_{dt}.log"
    
    try:
        os.mkdir(directory_name)
        os.mkdir(directory_name + "/raw")
        os.mkdir(directory_name + "/masters")
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

    if not(logSet):
            setLogger(True, log_name)
            logSet = True
    else:
        log.info("\n\n\n")
        setnewloggerfile(False, log_name)
    mk2 = ""
    dtcreate = datetime.now()
    dtcreate = dtcreate.strftime("%Y-%m-%d %H%M")
    dt = dtcreate

    """with open(f"{directory_name}/read me.txt", mode = 'w') as file:
        file.write("bord opstilling\n")
        two_wire_res_a = input("What is the line resistance? ")
        file.write(f"two-wire modstand ca. {two_wire_res_a}\n")
        decoder_placement = input("at what point is the decoder connected? ")
        file.write(f"decoder placering: {decoder_placement}\n")
        load_res = input("What is the resistance of the potentiometer on the load? ")
        file.write(f"Last modstand {load_res} ohm\n")
        power_supply = input("What it the voltage of the PSU? ")
        file.write(f"PSU: {power_supply}V\n")"""


    ######################################################################################################################################################################################################################################################
    ######################################################################################################################################################################################################################################################
    ##LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START LOOP START ##
    ######################################################################################################################################################################################################################################################
    reset = interface.reset_call()
    log.info("reset " + str(reset))
    while True:
        try:
            

            try:
                interface.decoders = []
                

                interface.custom_tester("put","/luType/6",{"name":"rainbird golf","protocol":2,"customerId":4,"mk2Cipher":0,"mk3KeyMangle":0,"mk3Key":0,"mk3Hash":0} )
                
                delete = interface.delete_call()
            except requests.exceptions.HTTPError as errh:
                log.error("Http Error",errh)
            except requests.exceptions.ConnectionError as errc:
                log.error(f"Connection Error!!!{errc}")
                connection = False
                log.error(f"Failed to reach {host} check cables")
                while connection == False:
                    try:
                        response = interface.custom_tester("get","")
                        log.info(f"Connection to {host} has been reestablished and the program will now restart")
                        sleep(2)
                        connection = True
                        header = ["reconnected"]
                        mk2 = ""
                    except:
                        print(f"Failed to reach {host} check cables" )
                        sleep(15)
                    
            except requests.exceptions.ConnectTimeout as errt:
                log.error("Timeout Error!!!",errt)
            except requests.exceptions.RequestException as err:
                log.error("Something else went wrong",err)

            try:
                
                log.info("delete " + str(delete))
                
                discover = interface.discover_call()
                log.info(discover)
                if discover["result"] == 'found None' and mk2 == "" and automate == False:
                    mk2= input("No decoders discovered \nPlease enter mk2 address ")
                read_and_write_addresses()
                print("!" , interface.decoders)
                address_pairs = []
                if not(logSet):
                        setLogger(True, log_name)
                        logSet = True
                else:
                    log.info("\n\n\n")
                    setnewloggerfile(False, log_name)
            except requests.exceptions.HTTPError as errh:
                log.error("Http Error",errh)
            except requests.exceptions.ConnectionError as errc:
                log.error(f"Connection Error!!!{errc}")
                connection = False
                log.error(f"Failed to reach {host} check cables")
                while connection == False:
                    try:
                        response = interface.custom_tester("get","")
                        log.info(f"Connection to {host} has been reestablished and the program will now restart")
                        sleep(2)
                        connection = True
                        header = ["reconnected"]
                        mk2 = ""
                    except:
                        print(f"Failed to reach {host} check cables" )
                        sleep(15)
                    
            except requests.exceptions.ConnectTimeout as errt:
                log.error("Timeout Error!!!",errt)
            except requests.exceptions.RequestException as err:
                log.error("Something else went wrong",err)
            
            li = []
            for x in range(0,number_of_random_on):
                selector = random.sample(interface.decoders,1)[0]
                
                if len(str(selector["addr"])) == 4:
                    
                    første = selector["addr"]
                    while første > 100:
                        første = int(første / 10)
                    sidste = "{:02d}".format(selector["addr"] % 100)
                    alternative_address = int(str(første) + "0" + str(sidste)) 
                    for each in interface.decoders:
                        if each == {"addr":alternative_address, "type":4}:
                            interface.decoders.remove(each)
                        elif each == selector:
                            interface.decoders.remove(each)
                elif len(str(selector)) == 5:
                    første = selector["addr"]
                    while første > 100:
                        første = int(første / 10)
                    sidste = "{:02d}".format(selector["addr"] % 100)
                    alternative_address = int(str(første) + str(sidste)) 
                    for each in interface.decoders:
                        if each == {"addr":alternative_address, "type":6}:
                            interface.decoders.remove(each)
                        elif each == selector:
                            interface.decoders.remove(each)
                else:
                    for each in interface.decoders:
                        if each == selector:
                            interface.decoders.remove(each)
                            break
                li.append(selector)
            #li = random.sample(interface.decoders,number_of_random_on)
            print(li)
            """selects x decoders and turns them on continuously for a full cycle, also removes their address from the temporary list"""
            for selected in li:
                try:
                
                    if len(str(selected["addr"])) == 4:
                        interface.lu_on(selected,switchparam="d2a5")

                        
                    elif len(str(selected["addr"])) == 5:
                        interface.lu_on(selected,switchparam="643217")
                        
                        
                    else:
                        interface.lu_on(selected,switchparam="d2a5")
                    log.info(str(selected["addr"]) + "has been selected randomly to hold continuously")
                    #interface.decoders.remove(selected)
                except Exception as e:
                    log.error("error ocorured "+str(selected) + " responded" + str(e))
        
            for i in interface.decoders:
                filename = f"{directory_name}/raw/decoder {i["addr"]}_{dt}.csv"
                csv_list = {"filename" : filename,"decoder": i["addr"],"directory": directory_name, "datetime": dtcreate, "type": i["type"]}
                address_pairs.append(i["addr"])
                connection = True
                
                
            
                """if i["type"] == 4:
                    r = regReader.readSomeRegisters(host, reg, i["addr"])
                    log.info(f"Read {len(r)} values out of {regReader.countRegisterPositions(reg)} : {r}")
                    print("factory reset")
                    interface.factory_reset(i)
                    #r = regReader.writeSomeRegisters(host = host,regs = ["293310"], addr = i["addr"])
                    r = regReader.readSomeRegisters(host, reg, i["addr"])
                    log.info(f"Read {len(r)} values out of {regReader.countRegisterPositions(reg)} : {r}")"""



            
        

                with open(filename, mode='a') as file:
                    writer = csv.writer(file, delimiter= ',', lineterminator = '\n')
                    

                    if i["type"] == 4: #checks if mk3
                        
                        for x in range(number_of_tests): #number of measurements for a mk3
                            log.info("\n\n\n")
                            try:
                                mk3_test(i)
                                """if fail == True:
                                    print("due to failure " , i["addr"] , " is removed from list")
                                    #address_pairs.remove(i)
                                    interface.delete_decoder(i) """
                            except Exception as e:
                                log.error("Exception occured:" + str(e))
                            except requests.exceptions.HTTPError as errh:
                                log.error("Http Error",errh)
                            except requests.exceptions.ConnectionError as errc:
                                log.error(f"Connection Error!!!{errc}")
                                connection = False
                                log.error(f"Failed to reach {host} check cables")
                                while connection == False:
                                    try:
                                        response = interface.custom_tester("get","")
                                        log.info(f"Connection to {host} has been reestablished and the program will now restart")
                                        sleep(2)
                                        connection = True
                                        header = ["reconnected"]
                                        mk2 = ""
                                    except:
                                        print(f"Failed to reach {host} check cables" )
                                        sleep(15)
                            except requests.exceptions.ConnectTimeout as errt:
                                log.error("Timeout Error!!!",errt)
                            except requests.exceptions.RequestException as err:
                                log.error("Something else went wrong",err)

                    elif i["type"] == 6: #checks if mk2
                        for switch in mk2param:
                            
                            if int(i["addr"]) > 999:
                                første = int(i["addr"] / 100)
                                sidste = "{:02d}".format(i["addr"] % 100)
                                alternative_address = int(str(første) + "0" + str(sidste)) 
                                interface.factory_reset(alternative_address)
                            for x in range(number_of_tests): #number of measurements for a mk2
                                log.info("\n\n\n")
                                try:
                                    mk2_test(i, switch)

                                    if fail == True:
                                        print("due to failure " , i["addr"] , " is removed from list")
                                        address_pairs.remove(i)
                                        interface.delete_decoder(i)
                                        interface.decoders.remove(i)
                                        break        
                                except Exception as e:
                                    log.error("Exception occured:" + str(e))
                                except requests.exceptions.HTTPError as errh:
                                    log.error("Http Error",errh)
                                except requests.exceptions.ConnectionError as errc:
                                    log.error(f"Connection Error!!!{errc}")
                                    connection = False
                                    log.error(f"Failed to reach {host} check cables")
                                    while connection == False:
                                        try:
                                            response = interface.custom_tester("get","")
                                            log.info(f"Connection to {host} has been reestablished and the program will now restart")
                                            sleep(2)
                                            connection = True
                                            header = ["reconnected"]
                                            mk2 = ""
                                        except:
                                            print(f"Failed to reach {host} check cables" )
                                            sleep(15)
                                except requests.exceptions.ConnectTimeout as errt:
                                    log.error("Timeout Error!!!",errt)
                                 
                try:
                    dataman(csv_list)
                except Exception as e:
                    log.error("csv error", e)
            for decoder in li:
                try:
                    r = interface.lu_off(decoder,verify=True)
                    log.info(f"{decoder} result is {r}")
                except Exception as e:
                    log.error("error ocorured "+str(decoder) + " responded" + str(e))
            for i in interface.decoders:
                """if i["type"] == 4:
                    r = regReader.readSomeRegisters("SRC-IF-LOFT2", reg, i["addr"])
                    log.info(f"Read {len(r)} values out of {regReader.countRegisterPositions(reg)} : {r}")"""
            if automate == True:
                dt = datetime.now()
                dt = dt.strftime("%Y-%m-%d %H%M")
                

                pass
            else:
                input(f"test complete for {address_pairs} ")
                mk2 = input("input address if it's a mk2 you're testing now ")
                dt = datetime.now()
                dt = dt.strftime("%Y-%m-%d %H%M")           

        
        except KeyboardInterrupt:
            print("\nTest ended \ndisabling all outputs")
            interface.reset_call()
            break
