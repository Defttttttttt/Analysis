# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 14:43:44 2020

@author: admin
"""
import schedule
import os
import time
import datetime
import numpy as np

import GenCalcParaFromCSV


CalConfig=GenCalcParaFromCSV.CalConfig
RunTimeRecordPath=GenCalcParaFromCSV.RunTimeRecordPath
RunTimeRecord14=RunTimeRecordPath['RunTimeRecord14'][0]

#@@
MinitesGuardList=["VibDaq","ReadAndSaveDBPPandSPEC","ReadAndSaveDBWave","UpdateRedisForBrowser"]

def GenTimeRecordPathDict():
    PathDict={}
    for key in RunTimeRecordPath:
        PathKey=(RunTimeRecordPath[key][0]).split("/")[-1]
        PathDict[PathKey]=RunTimeRecordPath[key][0]
    return PathDict
TimeRecordPathDict=GenTimeRecordPathDict()


def GenGuartDeltaTimeLimit():
    GuartDeltaTimeLimit={}
    for key in RunTimeRecordPath:
        ProcessLabel=(RunTimeRecordPath[key][0]).split("/")[-1]
        Limit=int(RunTimeRecordPath[key][1])
        GuartDeltaTimeLimit[ProcessLabel]=Limit
    return GuartDeltaTimeLimit
GuartDeltaTimeLimit=GenGuartDeltaTimeLimit()

def CalDeltaTime(TimeString,TimeType):
    
    if TimeType=="S" or TimeType=="s":
        DeltaTime=(datetime.datetime.now()-datetime.datetime.strptime(TimeString,CalConfig['time_format'][0])).total_seconds()
        
    if TimeType=="D" or TimeType=="d":
        DeltaTime=(datetime.datetime.now()-datetime.datetime.strptime(TimeString,CalConfig['time_format'][0])).days
    return DeltaTime

def ReadTimeString(TimeFilePath):
    TimeString=""
    if os.path.exists(TimeFilePath):
        with open(TimeFilePath,"r") as file:
            TimeString=file.read()
    return TimeString


def AppendBatRestartRecord(RestartList):
    NowTime=datetime.datetime.now().strftime(CalConfig['time_format'][0])
    DataString="%s,"%NowTime
    for ProcessName in RestartList:
        DataString+="%s,"%(ProcessName)
    DataString=DataString[:-1]+"\n"
    with open('./Parameters/BatRunningRecord.csv',"a") as file:
        file.write(DataString)
    return
        
def RestartOnePythonShell(ProcessName):

    os.system("ps aux | grep -v grep| grep  /home/admin/Analysis/RunPython%s > ./Parameters/tempfile"%ProcessName)
    RS_Pids=[]
    
    with open("./Parameters/tempfile","r") as file:
        for line in file:
            RS_Pids.append(line.split(" ")[4])
        
    for pid in RS_Pids:
        os.system("kill -9 %s"%pid)
        print("%s killed"%pid)
    
    ShellScriptString="nohup python3 /home/admin/Analysis/RunPython%s.py > /home/admin/Analysis/log/%s.log 2>&1 &\n"%(ProcessName,ProcessName)
    
    with open("./TempRunShell.sh","w") as file:
        file.write(ShellScriptString)
        
    time.sleep(2)
    os.system("chmod u+x ./TempRunShell.sh")
    os.system("sh ./TempRunShell.sh")
    
    time.sleep(5)
    #os.remove("./TempRunShell.sh")
    
    print("Complete Restart %s.."%ProcessName)
    
    return
    
def RunSomeProcessRestart(RunningFlagDict):
    RestartList=[ProcessLabel for ProcessLabel in RunningFlagDict if RunningFlagDict[ProcessLabel]==False]
    AppendBatRestartRecord(RestartList)
    for ProcessName in RestartList:
        RestartOnePythonShell(ProcessName)
    return
    
def MinutesGuard():
    print("Minute-Guarding...")
    
    nowtime=datetime.datetime.now().strftime(CalConfig['time_format'][0])
    WriteRunTimeRecord(RunTimeRecord14,nowtime)
    
    DelTimeRecordDict={}
    RunningFlagDict={}
        
    for ProcessLabel in MinitesGuardList:
        TFPath=TimeRecordPathDict[ProcessLabel]
        TimeString=ReadTimeString(TFPath)
        
        if len(TimeString)>0:
            UnitLabel="S"            
            delTime=CalDeltaTime(TimeString,UnitLabel)
            DelTimeRecordDict[ProcessLabel]=delTime      
                       
    for ProcessLabel in DelTimeRecordDict:
        RunningFlagDict[ProcessLabel]=DelTimeRecordDict[ProcessLabel]<=GuartDeltaTimeLimit[ProcessLabel]
    
    print(RunningFlagDict)
    
    if len(RunningFlagDict.values())>0:            
        if (np.array(list(RunningFlagDict.values()))==False).any():
            RunSomeProcessRestart(RunningFlagDict)
            
    print("Complete Minute-Guarding!")
    return

def WriteRunTimeRecord(RunTimeRecord,TimeString):
    while True:
        try:
            with open(RunTimeRecord,"w") as file:
                file.write(TimeString)
                break
        except:
            time.sleep(0.5)
        finally:
            break
    return

def main():
    MinutesGuard()
    schedule.every(15).seconds.do(MinutesGuard)    
    while True:       
        schedule.run_pending()       
    return


if __name__ == '__main__':
    #pass
    main()
       
