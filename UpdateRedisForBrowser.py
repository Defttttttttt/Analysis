#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:13:35 2020

@author: ziyun
"""

import os
import redis
import time
import datetime
import json
import numpy as np
import pandas as pd

import GenCalcParaFromCSV
import thinkdsp
import thinkplot

VibSensorInfo=GenCalcParaFromCSV.VibSensorInfo
RunTimeRecordPath=GenCalcParaFromCSV.RunTimeRecordPath

RunTimeRecord12=RunTimeRecordPath['RunTimeRecord12'][0]

ChannelInfo=[VibSensorInfo[key][2] for key in VibSensorInfo]
BearingInfo=list(set([VibSensorInfo[key][1] for key in VibSensorInfo]))
BearingInfo.sort()
ShaftVibChannels=[VibSensorInfo[key][2] for key in VibSensorInfo if key.find("SV")!=-1]


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ShareMenmorySegLength=18+4104*len(ChannelInfo)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

CalConfig=GenCalcParaFromCSV.CalConfig
RealTimeRedisKeyFilePath=CalConfig['RealTimeRedisKeyFilePath'][0]
DBConfig=GenCalcParaFromCSV.DBConfig

VibWaveRedisIP=DBConfig['VibWaveRedisIP'][0]
VibWaveRedisPort=int(DBConfig['VibWaveRedisPort'][0])
VibWaveRedisDB=int(DBConfig['VibWaveRedisDB'][0])

BrowserRedisIP=DBConfig['BrowserRedisIP'][0]
BrowserRedisPort=int(DBConfig['BrowserRedisPort'][0])
BrowserRedisDB=int(DBConfig['BrowserRedisDB'][0])

ChannelInfo=[VibSensorInfo[key][2]  for key in VibSensorInfo]
ChannelCount=len(ChannelInfo)


RealTimeRedisDict={}

with open(RealTimeRedisKeyFilePath,"r") as file:
    RealTimeRedisDict=json.load(file)
    
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
    KeyList.append("Speed")
    KeyList.append("Gap")
    for i in range(2,ChannelCount+2):
        KeyList.append("%s"%i)
    return KeyList


def MakeWaveToSPEC(WaveData,Speed):
    cutoff=1
    wave=thinkdsp.Wave([])
    wave.ys=WaveData 
    spec=wave.make_spectrum()
    return spec.fs*Speed/480,spec.amps/len(spec),spec.angles 


def AnalyzeSPEC(SPEC):
    fs=np.array(SPEC[0])
    amps=np.array(SPEC[1])
    angles=np.array(SPEC[2])
    f=[]
    amp=[]
    angle=[]
    
    Indexs=[]
    Indexs.append(amps[:8].argmax())
    Indexs+=[8,16,24]
    Indexs.append(25+amps[25:].argmax())
    Indexs.append(amps.argmax())
    
    f=[float("%.2f"%fs[index]) for index in Indexs]
    amp=[float("%.2f"%(2*amps[index])) for index in Indexs]   
    angle=[float("%.1f"%(angles[index]%360)) for index in Indexs]
        
    return f,amp,angle




def ReadRedisPPandSPEC():

    #r=redis.Redis(VibWaveRedisIP,VibWaveRedisPort,db=VibWaveRedisDB)
    r=redis.Redis(host=VibWaveRedisIP,port=6379,db=1)

    RedisParaName="VibDaq"
    RedisKeyList=GenRedisKeyListByChannelCounts()
    DataArray=r.hmget('%s'%RedisParaName,RedisKeyList)
    Speed=int(DataArray[0])
    Gap=list(eval(str(DataArray[1],"utf-8")))
    VibPP=[]
    SPEC=[]
    print("Speed:%s"%Speed)
    
    for i in range(2,len(DataArray)):
        OneVibs=list(eval(str(DataArray[i],encoding="utf-8")))
        AllSPEC=MakeWaveToSPEC(OneVibs,Speed)
        EigenSPEC=AnalyzeSPEC(AllSPEC)
        VibPP.append(max(OneVibs)-min(OneVibs))
        SPEC.append(EigenSPEC)
    r.close()
        
    return Speed,Gap,VibPP,SPEC



def WriteDataToRedis(Paraname,DataDict):
    
    #r=redis.Redis(VibWaveRedisIP,VibWaveRedisPort,db=VibWaveRedisDB)
    r=redis.Redis(host=VibWaveRedisIP,port=6379,db=2)
    
    print("Paraname:%s..."%Paraname)
    dictstring="{"
    for Key in DataDict:
        dictstring+="'%s':%s,"%(Key,DataDict[Key])
    dictstring=dictstring[:-1]+"}"
    while True:
        try:
            r.hmset("%s"%Paraname,eval(dictstring))
            print("Redis Written Successfully!")
            break
        except:
            break             
    r.close()
    return

def GetGapDict(IndexDict,DataArray):
    DataDict={}
    for key in IndexDict:
        index=IndexDict[key]
        DataDict[key]=DataArray[index]
    return DataDict


def GetGapsIndexDict(GapsRedisKeys):
    
    SVLables={}
    SVLables["X"]=1
    SVLables["Y"]=2
    
    GapsIndexDict={}
    for key in GapsRedisKeys:
        VibSensorKey="%sSV%s"%(key[:2],SVLables[key.split("_")[1]])
        Index=ChannelInfo.index(VibSensorInfo[VibSensorKey][2])
        GapsIndexDict[key]=Index
    
    return GapsIndexDict


def GetVibDict(IndexDict,DataArray):
    DataDict={}
   
    for key in IndexDict:
        Indexs=IndexDict[key]
        if Indexs[0]==0 or Indexs[0]==1:
            if key[1] in ["A","B","C"] and key[3:] in ["overall"]:
                DataDict[key]=0.36*(DataArray[Indexs[0]][Indexs[1]])
            else:
                DataDict[key]=DataArray[Indexs[0]][Indexs[1]]
        if Indexs[0]==2:
            if key[1] in ["A","B","C"] and key[3:] in ["1X_amp","2X_amp"]:
                DataDict[key]=0.36*(DataArray[Indexs[0]][Indexs[1][0]][Indexs[1][1]][Indexs[1][2]])
            else:
                DataDict[key]=DataArray[Indexs[0]][Indexs[1][0]][Indexs[1][1]][Indexs[1][2]]
                
    return DataDict
                    

def GetVibIndexDict(VibsRedisKeys):
    #DataArray=[[Speed],VibPP,SPEC]
    SensorLablesDict={}
    SensorLablesDict["X"]=1
    SensorLablesDict["Y"]=2
    SensorLablesDict["Z"]=3
    
    SensorLablesDict["A"]=1
    SensorLablesDict["B"]=2
    SensorLablesDict["C"]=3
    
    
    SensorLablesDict["D"]=1
    SensorLablesDict["E"]=2
    SensorLablesDict["F"]=3
    SensorLablesDict["G"]=4
    SensorLablesDict["H"]=5
    SensorLablesDict["I"]=6

    
    xParm=["<1X","1X","2X","3X",">3X"]
    valuetypes=["freq","amp","angle"]
    
    VibIndexDict={}
    for key in VibsRedisKeys:
        if key=="Speed":
            VibIndexDict[key]=[0,0]
        else:
            BID="B%s"%(key[0])
            if key[1] in ["X","Y","Z"]:
                SensorType="SV"
            if key[1] in ["A","B","C"]:
                SensorType="BV"
            if key[1] in ["D","E","F","G","H","I"]:
                SensorType="AD"
            VibSensorKey="%s%s%s"%(BID,SensorType,SensorLablesDict[key[1]])
            ChannelIndex=ChannelInfo.index(VibSensorInfo[VibSensorKey][2])
            if key.split("_")[-1]=="overall":
                VibIndexDict[key]=[1,ChannelIndex]
            else:
                x,valuetype=key.split("_")[1:]
                x_index=xParm.index(x)
                value_index=valuetypes.index(valuetype)
                VibIndexDict[key]=[2,[ChannelIndex,value_index,x_index]]
                
    return VibIndexDict

    
def WriteVibDatasToRedis(RealTimeRedisDict,GapsIndexDict,VibIndexDict):
    
    Speed,Gap,VibPP,SPEC=ReadRedisPPandSPEC()
    if Speed >10:
        if GapsIndexDict!={}:
            GapsDict=GetGapDict(GapsIndexDict,Gap)
            WriteDataToRedis("VibGapRedisKey",GapsDict)
        
        DataArray=[[Speed],VibPP,SPEC]
        
        VibDict=GetVibDict(VibIndexDict,DataArray)
        WriteDataToRedis("VibInfoRedisKey",VibDict)
    return

def WriteFaultInfoToRedis(RealTimeRedisDict):
    FaultInfoDict={}
    for Key in RealTimeRedisDict['FaultInfoRedisKey']:
        if Key.find("FaultFlag")!=-1:
            FaultInfoDict[Key]=False
        else:
            FaultInfoDict[Key]="Nothing"
    WriteDataToRedis("FaultInfoRedisKey",FaultInfoDict)
    
    return


def InitialRedis(RealTimeRedisDict):
    #r=redis.Redis(host=BrowserRedisIP,port=BrowserRedisPort,db=BrowserRedisDB)
    r=redis.Redis(host=BrowserRedisIP,port=6379,db=2)
    value=0
    
    for Paraname in RealTimeRedisDict:
        dictstring="{"
        for key in RealTimeRedisDict[Paraname]:
            dictstring+="'%s':'%s',"%(key,value)
        dictstring=dictstring[:-1]+"}"
        r.hmset("%s"%Paraname,eval(dictstring))
    
    r.close()
    return


def main():
    #pass the initial
    InitialRedis(RealTimeRedisDict)
    GapsIndexDict={}
    if ShaftVibChannels!=[]:
        GapsIndexDict=GetGapsIndexDict(RealTimeRedisDict["VibGapRedisKey"])
        print(GapsIndexDict)
    
    VibIndexDict=GetVibIndexDict(RealTimeRedisDict['VibInfoRedisKey'])
    print(VibIndexDict)



    while True:

        nowtime=datetime.datetime.now().strftime(CalConfig['time_format'][0])
        WriteRunTimeRecord(RunTimeRecord12,nowtime)

        WriteVibDatasToRedis(RealTimeRedisDict,GapsIndexDict,VibIndexDict)


        print("Redis Written For Browser!")
        time.sleep(1)
    
    return
if __name__ == '__main__':
    #pass
    main()
    # VibIndexDict = GetVibIndexDict(RealTimeRedisDict['VibInfoRedisKey'])
    # print(VibIndexDict)
    # print(RealTimeRedisDict)
    # GapsIndexDict = GetGapsIndexDict(RealTimeRedisDict["VibGapRedisKey"])
    # print(GapsIndexDict)
    # print(RealTimeRedisDict['VibInfoRedisKey'])
    # VibIndexDict = GetVibIndexDict(RealTimeRedisDict['VibInfoRedisKey'])
    # print(VibIndexDict)
