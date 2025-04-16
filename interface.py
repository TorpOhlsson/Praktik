import requests
import json
import logging
from time import sleep
from crysberg import Crysberg
apikey = "XXXXXXX"
interfaceid = 8
crysberg = Crysberg(apikey, interfaceid)

log = logging.getLogger("root")

class InterFace:
    def __init__(self,hostname):
        self.data = [] # idfk PLACEHOLDER VALUE!!!
        self.hostname = hostname #hostname for interface string
        self.decoders = [] #List of all decoders
        #self.timeout = timeout #timeout value
        self.twstate = None #State of the twowire
        self.leak = None #leak in mA temporary value
        self.voltage = None #voltage in mV temporary value
        self.inrush_raw = [] #inrush verification temporary value
        self.inrush_adjusted = [] #adjusted inrush value temporary value
        self.inrush_verified = False #verifying that the inrush is withing the accepteble params
        self.resistance = None  #Resistance
        self.inductance = None  #inductance of coil from specific 
        self.lineresistance = 0 
        self.message = None
        #self.session = session

##############################################################################################################################################################################################################################################
#INTERFACE CALLS WORKS FOR mk2 AND mk3  INTERFACE CALLS WORKS FOR mk2 AND mk3   INTERFACE CALLS WORKS FOR mk2 AND mk3   INTERFACE CALLS WORKS FOR mk2 AND mk3   INTERFACE CALLS WORKS FOR mk2 AND mk3   INTERFACE CALLS WORKS FOR mk2 AND mk3#
##############################################################################################################################################################################################################################################


    
    def lu_on(self, decoder, switchparam:str = "default", verify:bool=False): 
        cmd_on = "/lu/" + str(decoder["addr"]) + "/1/on" #dfa5 inrush Adjust & hold adjust, Cfa5 inrush adjust, 9fa5 hold adjust, 8fa5 no adjust 
        if decoder["type"] == 6 and switchparam == "default":
            switchparam = "d255"
        elif decoder["type"] == 4 and switchparam == "default":
            switchparam = "643217"
        if verify:
            cmd_on += "?verify" + "&switch=" + switchparam
        elif not verify:
            cmd_on += "?switch=" + switchparam
        result = crysberg.call("post", cmd_on)
        if "error" in result:
            log.error("Rcv: {}".format(result))
        else:
            log.debug("Recv: {}".format(result))
        return {"cmd":cmd_on, "answer": result,"switch":switchparam}
    
    def lu_off(self, decoder, verify:bool=False): 
        """turns off a line unit"""
        cmd_off = "/lu/" + str(decoder["addr"]) + "/1/off" #dfa5 inrush Adjust & hold adjust, Cfa5 inrush adjust, 9fa5 hold adjust, 8fa5 no adjust 
        if verify:
            cmd_off += "?verify"
        else:
            pass 
        result = crysberg.call("post",cmd_off)
        log.debug("Recv: {}".format(result))
        return {"cmd":cmd_off, "answer": result}
    
    def measurement(self,decoder,switch:str="default"): 
        """function that tests and saves inrush current from the interface 50(mk3) or 38(mk2) samples or with a 25 ms interval in mA, if it's a mk2 it also checks the verifysum"""
        self.inrush_adjusted = []
        cmd_measurement = "/lu/measurement"
        if decoder["type"] == 6:
            
            cmd_on = self.lu_on(decoder,switchparam= switch,verify = True)
        elif decoder["type"] == 4:
            cmd_on = self.lu_on(decoder, switchparam=switch, verify = True)
        
        basemax = 0
        basemin = 0
        self.inrush_adjusted = []
        
        #if 'error' not in cmd_on["answer"] or decoder["type"] == 6:
        result = crysberg.call("get",cmd_measurement)
        if "result" in result:
            result = result["result"]
            measurement =  result["array"]
            value = 0 
            maxValue = 0
            temp_list = []
            verifysum =0
            for x in measurement: 
                if x >= 1 << 15:
                    value = abs(x - (1 << 16))
                    self.inrush_adjusted.append(value)
                else:
                    value = x
                    self.inrush_adjusted.append(value)
                if value > maxValue:
                    maxValue = value


            
            
            if decoder["type"] == 6:
                for x in measurement: 
                    if x >= 1 << 15:
                        value = x - (1 << 16)
                        temp_list.append(value)
                        
                    else:
                        value = x
                        temp_list.append(value)
   
                for x in range(1,20):
                    if temp_list[x] > basemax:
                        basemax = temp_list[x]
                    elif temp_list[x] < basemin:
                        basemin = temp_list[x]

                for x in range(20,len(temp_list)):
                    
                    if temp_list[x] > basemax:
                        v = temp_list[x]-basemax
                    elif temp_list[x] < basemin:
                        v = abs(temp_list[x]-basemin)
                    else:
                        v = 0
                    
                    verifysum += v
                output= {"op":"GET","cmd": cmd_on["cmd"],"unit":"mA", "result":self.inrush_adjusted, "DecAddr": decoder["addr"],"switchparam":cmd_on["switch"],"verifysum":verifysum}
            else:
                output = {"op":"GET","cmd": cmd_on["cmd"],"unit":"mA", "result":self.inrush_adjusted, "DecAddr": decoder["addr"],"switchparam":cmd_on["switch"]}
            log.debug("Recv: {}".format(result))
        else:
            result = result["error"]
            log.error("Recv: {}".format(result))
        
        
        return output


    
    def delete_decoder(self,decoder): #removes a specific decoder from the interface
        cmd_deletedec = "/lu/" + decoder["addr"]
        r = self.session.delete(cmd_deletedec)
        return r.json()["result"]
    
    #RESET
    def reset_call(self): #Broadcast command to shut off all outputs on all line units
        cmd_reset = "/lu/reset"
        result = crysberg.call("post",cmd_reset)
        return {"op":"POST","cmd": cmd_reset,"unit":"", "result":"result is "+  result["result"]}
    
    #DELETEALL
    def delete_call(self): #clears the interface of decoders
        cmd_delete = "/lu/deleteAll"
        self.decoders = []
        result = crysberg.call("post",cmd_delete)
        return {"op":"POST","cmd": cmd_delete,"unit":"", "result":"result is " + result["result"]}

    def decoder_type_call(self): #checks the possible decoder types for the interface rainbird/crysberg etc..
        cmd_type = "/luType"
        r = requests.get(cmd_type)
        return r.json()["result"]
    

    def add_mk2(self,address): #function that adds mk2 decoders to the interface 
        cmd_add_mk2 = "/lu/"+ str(address)
        result = crysberg.call("put",cmd_add_mk2, ({'addr':int(address),'type':6,'hwVer':0,'swVer':0, 'outputs':1,'inputs':0,'grp':1,'subGrp':1,'state':0, 'alias':0}))
        self.message = 'Successfully added decoder ' + str(address) + ' to the interface'
        cmd_lu = "/lu"
        result = crysberg.call("get",cmd_lu)
        """for x in r.json()["result"]:
            z = {"addr" : x["addr"], "type" : x["type"]}
        if z not in self.decoders:
                self.decoders.append(z)"""
        return self.message
    
    
    
##############################################################################################################################################################################################################################################
#######ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3    ONLY ON/FOR MK3#######
##############################################################################################################################################################################################################################################

    def factory_reset(self, decoder): #factory reset for a specific mk3 decoder, resets the registerbanks.
        cmd_factory_reset = "/lu/"+ str(decoder)+"/factoryReset"
        result = crysberg.call("post",cmd_factory_reset)
        
        sleep(5) #sleep to ensure that the factory reset had time to write the registers
        
        return result
    
    def test_function(self, decoder, session = requests): #Test function for a mk3 decoder, returns a object with luVoltage aHigh inrushShoulderWidth inrushCycleCount holdCycleBase verifyShoulderWidth bHigh
        cmd_test = "/lu/" + str(decoder["addr"]) + "/test?output=1"
        result = crysberg.call("get",cmd_test)["result"]
        log.debug("Recv: {}".format(result))
        luvoltage = result["luVoltage"]
        aHigh = result["aHigh"]
        att = result["att"]
        inrushShoulderWidth = result["inrushShoulderWidth"]
        inrushCycleCount = result["inrushCycleCount"]
        holdCycleBase = result["holdCycleBase"]
        verifyCycleCount = result["verifyCycleCount"]
        verifyShoulderWidth = result["verifyShoulderWidth"]
        bHigh = result["bHigh"]
        return {"op":"GET","cmd": cmd_test,"unit":"various", "result": result , "DecAddr": decoder["addr"], "luVoltage": luvoltage, "aHigh": aHigh, "att":att, "inrushShoulderWidth": inrushShoulderWidth,
                "inrushCycleCount":inrushCycleCount,"holdCycleBase":holdCycleBase, "verifyCycleCount": verifyCycleCount,"verifyShoulderWidth": verifyShoulderWidth, "bHigh":bHigh}

    def resistance_call(self, decoder): #Gets the resistance for a Mk3 field decoder coil. Unit is ohm.
       
        cmd_resistance = "/lu/" + str(decoder["addr"]) + "/1/resistance"
        r = self.session.get(cmd_resistance)
        self.resistance = r.json()["result"]
    
        return {"op":"GET","cmd": cmd_resistance,"unit":"ohm", "result":str(self.resistance) , "DecAddr": decoder}

    def line_resistance_call(self, decoder): #checks the lineresistance for a decoder returns a value between 0 and 255 Ohm. mk3 only?
       
        cmd_resistance = "/lu/" + str(decoder["addr"]) + "/lineResistance"
        r = self.session.get(cmd_resistance)
        self.lineresistance = r.json()["result"]
        return {"op":"GET","cmd": cmd_resistance,"unit":"ohm", "result":str(self.lineresistance) , "DecAddr": decoder}

    def discover_call(self,to:int = 75): #function that discovers MK3 decoders on the two-wire
        discovered = []
        self.interface = []
        temporary_decoder = None
        cmd_discover = "/lu/discover?reset"
        result = crysberg.call("get",cmd_discover)["result"]

        for x in result:
            discovered.append(x)
        cmd_lu = "/lu"
        result = crysberg.call("get",cmd_lu)["result"]
    
        if "error" in result:
            raise Exception("error in call")
        for x in result:
            temporary_decoder = {"addr" : x["addr"], "type" : x["type"] 
                }
            if temporary_decoder not in self.decoders:
                    self.decoders.append(temporary_decoder) 
        return {"op":"GET","cmd": cmd_discover,"unit":"DecAddr", "result":"found " + str(temporary_decoder)}
    
    def voltage_call(self, decoder): #Gets the voltage from a Mk3 field decoder. Unit is milli Volt (divide by 1000 for volts).
        cmd_voltage = "/lu/"+ str(decoder["addr"]) +"/voltage"
        r = self.session.get(cmd_voltage)
        if r.json():
            self.voltage = r.json()["result"]
        else:
            pass
        return {"op":"GET","cmd": cmd_voltage,"unit":"mV", "result":str(self.voltage) , "DecAddr": decoder}
    
    def inductance_call(self, decoder): #Gets the inductance for a Mk3 field decoder coil. Unit is in mH
        cmd_inductance = "/lu/" + str(decoder["addr"]) + "/1/inductance"
        r = self.session.get(cmd_inductance)
        self.inductance = {"op":"GET","cmd": cmd_inductance,"unit":"mH", "result":r.json["result"] , "DecAddr": decoder}

        return self.inductance
    

    def leak_call(self, decoder): #returns leak current in mA
        cmd_leak = "/lu/"+ str(decoder["addr"]) +"/leak"
        r = self.session.get(cmd_leak)
        self.leak = {"op":"GET","cmd": cmd_leak,"unit":"mA", "result":r.json()["result"] , "DecAddr": decoder}

        return self.leak

##############################################################################################################################################################################################################################################
#CUSTOM TEST FUNKTION   CUSTOM TEST FUNKTION    CUSTOM TEST FUNKTION    CUSTOM TEST FUNKTION    CUSTOM TEST FUNKTION    CUSTOM TEST FUNKTION    CUSTOM TEST FUNKTION    CUSTOM TEST FUNKTION    CUSTOM TEST FUNKTION    CUSTOM TEST FUNKTION #
##############################################################################################################################################################################################################################################

    def custom_tester(self,metode, tekst , body={}):
        try:
            cmd_test = str(tekst)
            result = crysberg.call(metode, cmd_test, body)
        except:
            result = "error"
            pass
        return result
