# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 15:21:19 2019

@author: 11100027
"""
import os
import time
import datetime
import numpy as np
import redis
import GenCalcParaFromCSV



CalConfig=GenCalcParaFromCSV.CalConfig
FlagFilePath=CalConfig['FlagFilePath'][0]
TranscientWaveFilePath=CalConfig['TranscientWaveFilePath'][0]
TranscientTimeRecordFilePath=CalConfig['TranscientTimeRecordFilePath'][0]
TranscientWaveSavingCount=int(CalConfig['TranscientWaveSavingCount'][0])
TranscientWaveReadingInterval=float(CalConfig['TranscientWaveReadingInterval'][0])
TranscientWaveSleepTime=float(CalConfig['TranscientWaveSleepTime'][0])
WaveFilenameTime_format=CalConfig['WaveFilenameTime_format'][0]

VibSensorInfo=GenCalcParaFromCSV.VibSensorInfo
CalConfig=GenCalcParaFromCSV.CalConfig

ChannelInfo=[VibSensorInfo[key][2] for key in VibSensorInfo]
ChannelCount=len(ChannelInfo)

SpeedChangeFlag=False


DBConfig=GenCalcParaFromCSV.DBConfig
VibWaveRedisIP=DBConfig['VibWaveRedisIP'][0]
VibWaveRedisPort=int(DBConfig['VibWaveRedisPort'][0])
VibWaveRedisDB=int(DBConfig['VibWaveRedisDB'][0])

RunTimeRecordPath=GenCalcParaFromCSV.RunTimeRecordPath
RunTimeRecord3=RunTimeRecordPath['RunTimeRecord3'][0]


def AppendingStringToFile(FilePath,ToWringString):
    import time
    while True:
        try:
            with open(FilePath,'a') as file:
                file.write(ToWringString)
            break
        except IOError:
            time.sleep(0.5)
        finally:
            break
    return

def AppendingVibStringToFile(FilePath,ToWringString):
    while True:
        try:
            with open(FilePath,'a') as file:
                file.write(ToWringString)
            break
        except:
            time.sleep(0.5)
        finally:
            break
    return


def WriteFlagToFile(Path,FlagName,FlagValue):
    filestr=""
    with open(Path,'r') as file:
        for line in file:
            if line.split(",")[0]!=FlagName:
                filestr=filestr+line
            else:
                filestr=filestr+"%s,%s\n"%(FlagName,FlagValue)    
    while True:
        try:
            with open(Path,'w') as file:
                file.write(filestr)
            break
        except:
            time.sleep(0.5)
        continue
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

def GenRedisKeyListByChannelCounts():
    KeyList=[]
    KeyList.append("WriteTime")
    KeyList.append("Speed")
    for i in range(2,ChannelCount+2):
        KeyList.append("%s"%i)
    return KeyList


def ReadRedisWave():
    #r=redis.Redis(VibWaveRedisIP,VibWaveRedisPort,db=VibWaveRedisDB)
    r = redis.Redis(host="localhost", port=6379, db=1)
    RedisParaName="VibDaq"
    RedisKeyList=GenRedisKeyListByChannelCounts()
    DataArray=r.hmget('%s'%RedisParaName,RedisKeyList)
    WriteTime=str(DataArray[0],"utf-8")
    Speed=int(DataArray[1])
    VibData=[]   
    for i in range(2,len(DataArray)):
        OneVibs=str(DataArray[i],encoding="utf-8")
        VibData.append(OneVibs)
        
    r.close()
        
    return WriteTime,Speed,VibData

def ReadRedisSpeed():
    #r=redis.Redis(VibWaveRedisIP,VibWaveRedisPort,db=VibWaveRedisDB)
    r = redis.Redis(host="localhost", port=6379, db=1)
    RedisParaName="VibDaq"
    DataArray=r.hmget('%s'%RedisParaName,["Speed"])
    Speed=int(DataArray[0])
        
    return Speed

def main():

    #默认速度
    StandardSpeed=[]
    PreSpeedChangeFlag=False
    SpeedChangeFlag=False
    

   
    while True:
        nowtime=datetime.datetime.now().strftime(WaveFilenameTime_format)
        TimeRecord=datetime.datetime.now().strftime(CalConfig['time_format'][0])
        WriteRunTimeRecord(RunTimeRecord3,TimeRecord)
        
        VibFilePath=r"%s"%TranscientWaveFilePath+r"Wave%s"%nowtime
        Count=1
        PreTime=""
        
        nowSpeed=ReadRedisSpeed()

                  
        if len(StandardSpeed)>0 and nowSpeed>50:
            
            SpeedChangeFlag=(abs(np.array(StandardSpeed).mean()-nowSpeed)>15)
            if SpeedChangeFlag!=PreSpeedChangeFlag:
                WriteFlagToFile(FlagFilePath,"SpeedChangeFlag",SpeedChangeFlag)
            PreSpeedChangeFlag=SpeedChangeFlag
            pretime=""
            if SpeedChangeFlag:
                for i in range(TranscientWaveSavingCount):
                    WriteTime,Speed,VibData=ReadRedisWave()
                    
                    if pretime!=WriteTime:
                        ToWriteString="%s&&%s&&"%(WriteTime,Speed)
                        for OneVib in VibData:
                            ToWriteString+="%s**"%OneVib
                        ToWriteString=ToWriteString[:-2]+"####"
                        AppendingVibStringToFile(VibFilePath,ToWriteString)
                        pretime=WriteTime
                StandardSpeed=[]
                towritetime=datetime.datetime.now().strftime(CalConfig['time_format'][0])+"\n" 
                AppendingStringToFile(TranscientTimeRecordFilePath,towritetime)
                print("Waves have been saved. Path:%s"%VibFilePath)
            print(StandardSpeed)

        if len(StandardSpeed)>10:
            StandardSpeed=StandardSpeed[1:]
        StandardSpeed.append(nowSpeed)
        if not SpeedChangeFlag:
            time.sleep(TranscientWaveSleepTime)

        if os.path.exists(VibFilePath)==1 and os.path.getsize(VibFilePath)==0:
            os.remove(VibFilePath)
        
             
    return
    
    
if __name__ == '__main__':
    main()
    print(CalConfig['time_format'][0])
    print(RunTimeRecord3)