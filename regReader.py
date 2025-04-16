import requests, time
from crysberg import Crysberg
# Registers to read: ["2899", "2933", "4077"]

apikey = "xXXXXX"
interfaceid = 8
crysberg = Crysberg(apikey, interfaceid)


def regUnlock(host:str, addr:int):
  res = crysberg.call("post",'/tw/mk3/regUnlock/' + str(addr))["result"]
  return res.status_code == 200
  
def regLockAll(host:str):
  res = crysberg.call("post",'/tw/mk3/lockAll')
  return res.status_code == 200
  
def readSomeRegisters(host:str, regs:list, addr:int):
  '''Reads a list of registers (XXYY pairs, XX = bank, YY = regStart,regEnd), returns list of reads done untill error or finished'''
  output = []
  for x in regs:
    res = crysberg.call("get",'/tw/mk3/regRead/' + str(addr) + '/' + x)["result"]

    cnt = (int(x[3], 16) - int(x[2], 16) + 1)
    for y in range(cnt):
      output.append(res[0+y*2] + res[1+y*2])
    #time.sleep(0.2)
  return output
      
def writeSomeRegisters(host:str, regs:list, addr:int):
  '''Writes a list of registers (XXYY pairs, XX = bank, YY = regStart,regEnd), returns number of writes done untill error or finished.'''
  writes = 0
  for x in regs:
    res = crysberg.call("get",'/tw/mk3/regWrite/' + str(addr) + '/' + x)["result"]
    if not('result' in res.json()):
      return writes
    writes += 1
    #time.sleep(0.2)
  return writes
  
def countRegisterPositions(regs:list):
  cnt = 0
  for x in regs:
    cnt += (int(x[3], 16) - int(x[2], 16) + 1)
  return cnt
  
if __name__ == '__main__':
  regs = ["2923", "2801", "E003", "E047", "E08B", "E0CF"]
  regs2 = ["2923AAAA", "2801BBBB", "E003ABABCDCD", "E047DEDEEFEF", "E08BFEFEFAFA", "E0CFC0FFEEEE"]
  print('regUnlock:', regUnlock('192.168.10.75', 97507))
  r = readSomeRegisters("192.168.10.75", regs, 97507)
  print('Read', len(r), 'values out of', countRegisterPositions(regs), ':')
  print(r)
  #print(countRegisterPositions(regs2))
  print('regLockAll:', regLockAll('192.168.10.75'))
