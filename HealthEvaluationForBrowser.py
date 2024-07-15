#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 08:30:34 2020

@author: ziyun
"""


import redis
import time
import datetime
import numpy as np
import math
import json
import schedule
import thinkdsp
import thinkplot
import os
import GenCalcParaFromCSV
import redis



CalConfig=GenCalcParaFromCSV.CalConfig
DBConfig=GenCalcParaFromCSV.DBConfig
VibSensorInfo=GenCalcParaFromCSV.VibSensorInfo
VibLimitInfo=GenCalcParaFromCSV.VibLimitInfo
RunTimeRecordPath=GenCalcParaFromCSV.RunTimeRecordPath

RunTimeRecord11=RunTimeRecordPath['RunTimeRecord11'][0]

RealTimeRedisKeyFilePath=CalConfig["RealTimeRedisKeyFilePath"][0]

VibWaveRedisIP=DBConfig['VibWaveRedisIP'][0]
VibWaveRedisPort=int(DBConfig['VibWaveRedisPort'][0])
VibWaveRedisDB=int(DBConfig['VibWaveRedisDB'][0])

BrowserRedisIP=DBConfig['BrowserRedisIP'][0]
BrowserRedisPort=int(DBConfig['BrowserRedisPort'][0])
BrowserRedisDB=int(DBConfig['BrowserRedisDB'][0])

#FlagFilePath=CalConfig['FlagFilePath'][0]

VibChannelLimitFilePath=CalConfig['VibChannelLimitFilePath'][0]
#GapsPointToWriteCriterionStable=float(CalConfig['GapsPointToWriteCriterionStable'][0])
#GapsRecordPath=CalConfig['GapsRecordPath'][0]
#WavesRecordPath=CalConfig['WavesRecordPath'][0]

ChannelInfo=[VibSensorInfo[key][2] for key in VibSensorInfo]
BearingInfo=list(set([VibSensorInfo[key][1] for key in VibSensorInfo]))
BearingInfo.sort()
ChannelInfoSVAndBV=[VibSensorInfo[key][2] for key in VibSensorInfo \
                    if VibSensorInfo[key][0]=='Shaft Vibration' or VibSensorInfo[key][0]=='Bearing Vibration']

print(ChannelInfoSVAndBV)
ChannelInfoSV=[VibSensorInfo[key][2] for key in VibSensorInfo if VibSensorInfo[key][0]=='Shaft Vibration']

ChannelIDBID=[[VibSensorInfo[key][2],VibSensorInfo[key][1] ] for key in VibSensorInfo]
ChannelIDBIDDict=dict(ChannelIDBID)

ChannelCount=len(ChannelInfo)
BIDChannelID=[[VibSensorInfo[key][1],VibSensorInfo[key][2]] for key in VibSensorInfo\
            if VibSensorInfo[key][0]=='Shaft Vibration' or VibSensorInfo[key][0]=='Bearing Vibration']
BIDChannelIDDict={}
for BID in BearingInfo:
    BIDChannelIDDict[BID]=[]
for item in BIDChannelID:
    BID=item[0]
    BIDChannelIDDict[BID].append(item[1])
    
BIDSVChannelIDDict={}
for BID in BearingInfo:
    BIDSVChannelIDDict[BID]=[ChannelID for ChannelID in BIDChannelIDDict[BID] if ChannelID in ChannelInfoSV]    


RealTimeRedisDict={}
with open(RealTimeRedisKeyFilePath,"r") as file:
    RealTimeRedisDict=json.load(file)
HealthEvaluationRedisKey=RealTimeRedisDict['HealthEvaluationRedisKey']


def ReadVibOverallLimit():
    VibOverallLimitsForTranscient=[]
    VibOverallLimitsForStable=[]
    with open(VibChannelLimitFilePath,"r") as file:
        VibLimits=json.load(file)
    for ChannelID in VibLimits:
        VibOverallLimitsForTranscient.append(VibLimits[ChannelID]["Transcient"]["Overall"][2])
        VibOverallLimitsForStable.append(VibLimits[ChannelID]["Stable"]["Overall"][2])
    return VibOverallLimitsForTranscient,VibOverallLimitsForStable


def GetFlagFromFile(Path,FlagName):  
    FlagValue=""
    with open(Path,'r') as file:
        for line in file:
            if line.split(",")[0]==FlagName:
                FlagValue=line.replace("\n","").split(",")[1]
    return FlagValue

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

def WriteDataToRedis(Paraname,DataDict):
    #r=redis.Redis(host=BrowserRedisIP,port=BrowserRedisPort,db=BrowserRedisDB)
    #r=redis.Redis(host="192.168.8.133",port=9071,db=2)
    r = redis.Redis(host=BrowserRedisIP, port=6379, db=2)
    
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
    Indexs.append(amps[25:].argmax())
    Indexs.append(amps.argmax())
    
    f=[float("%.2f"%fs[index]) for index in Indexs]
    amp=[float("%.2f"%(2*amps[index])) for index in Indexs]
    angle=[float("%.2f"%angles[index]) for index in Indexs]

    return f,amp,angle

def GenRedisKeyListByChannelCounts():
    KeyList=[]
    KeyList.append("WriteTime")
    KeyList.append("Speed")
    KeyList.append("Gap")
    for i in range(2,ChannelCount+2):
        KeyList.append("%s"%i)
    return KeyList

def ReadRedisVibPP():
    r=redis.Redis(VibWaveRedisIP,VibWaveRedisPort,db=VibWaveRedisDB)
    #r=redis.Redis(host="192.168.8.136",port=9071,db=1)
    r = redis.Redis(host=BrowserRedisIP, port=6379, db=1)

    RedisParaName="VibDaq"
    RedisKeyList=GenRedisKeyListByChannelCounts()
    DataArray=r.hmget('%s'%RedisParaName,RedisKeyList)
    Speed=int(DataArray[1])
    VibPP=[]
    print("Speed:%s"%Speed)
   

    
    for i in range(3,len(DataArray)):
        OneVibs=list(eval(str(DataArray[i],encoding="utf-8")))
        VibPP.append(max(OneVibs)-min(OneVibs))
        
    r.close()
        
    return Speed,VibPP


def ReadRedisWave():

    #r=redis.Redis(VibWaveRedisIP,VibWaveRedisPort,db=VibWaveRedisDB)
    r = redis.Redis(host=BrowserRedisIP, port=6379, db=1)
    #r=redis.Redis(host="192.168.8.133",port=9071,db=1)
    RedisParaName="VibDaq"
    RedisKeyList=GenRedisKeyListByChannelCounts()
    print(RedisKeyList)
    DataArray=r.hmget('%s'%RedisParaName,RedisKeyList)
    Speed=int(DataArray[1])
    Gap=list(eval(str(DataArray[2],"utf-8")))
    VibPP=[]
    Wave=[]
    print("Speed:%s"%Speed)
   

    
    for i in range(3,len(DataArray)):
        OneVibs=list(eval(str(DataArray[i],encoding="utf-8")))
        VibPP.append(max(OneVibs)-min(OneVibs))
        Wave.append(OneVibs)
        
    r.close()
        
    return Speed,Gap,VibPP,Wave



def HealthEvaluateByChannel(VibPP,VibLimits):
    VibEvalutaionByChannelDict={}
    for ChannelID in ChannelInfoSVAndBV:
        ChannelIndex=ChannelInfo.index(ChannelID)
        print(ChannelIndex)
        Diff=VibLimits[ChannelIndex]-VibPP[ChannelIndex]
        if Diff>VibLimits[ChannelIndex]*0.5:
            VibEvalutaionByChannelDict[ChannelID]=100
        if Diff<=VibLimits[ChannelIndex]*0.5:
            TempHE=40/(VibLimits[ChannelIndex]*0.5)*Diff+60
            if TempHE>=0:
                VibEvalutaionByChannelDict[ChannelID]=TempHE
            else:
                VibEvalutaionByChannelDict[ChannelID]=0                
    return VibEvalutaionByChannelDict


def Array_RMS(Array):
    if len(Array)>0:
        return math.sqrt(sum([pow(data,2) for data in Array])/len(Array))
    return 100    

def HealthEvaluateForTranscientState():
    Speed,VibPP=ReadRedisVibPP()
    VibEvalutaionDict={}
    
    if Speed>20:
        VibEvalutaionByChannelDict=HealthEvaluateByChannel(VibPP,VibOverallLimitsForTranscient)
        for BID in BearingInfo:
            Evaluation=[]
            for ChannelID in BIDChannelIDDict[BID]:
                Evaluation.append(float("%.2f"%(VibEvalutaionByChannelDict[ChannelID])))
            VibEvalutaionDict[BID]=Array_RMS(Evaluation)
            
        HealthEvaluationDataDict={}
        for key in HealthEvaluationRedisKey:
            BID=key.split("_")[0]
            if BID in BearingInfo:
                HealthEvaluationDataDict[key]=float("%.2f"%VibEvalutaionDict[BID])
            if BID=="Average":
                HealthEvaluationDataDict[key]=float("%.2f"%np.array(list(VibEvalutaionDict.values())).mean())
                
        WriteDataToRedis("HealthEvaluationRedisKey",HealthEvaluationDataDict)
    return






    

def CalCorrelation(Dataarray1,Dataarray2):
    Dataarray1=np.array(Dataarray1)
    Dataarray2=np.array(Dataarray2)
    return np.corrcoef(Dataarray1,Dataarray2)[0][1]




def HealthEvaluateForStableState():
    Speed,Gap,VibPP,Wave=ReadRedisWave()    
    VibEvalutaionDict={}
    
    
    if Speed>20:
        VibEvalutaionByChannelDict=HealthEvaluateByChannel(VibPP,VibOverallLimitsForStable)
        print(VibEvalutaionByChannelDict)
        for BID in BearingInfo:
            #TestGapsInRate(BID,Gap)
            Evaluation=[]
            for ChannelID in BIDChannelIDDict[BID]:
                Evaluation.append(float("%.2f"%(VibEvalutaionByChannelDict[ChannelID])))
            RMS=Array_RMS(Evaluation)
            if RMS>80:
                VibEvalutaionDict[BID]=RMS
            else:
                #ChannelIndex1=ChannelInfo.index(BIDSVChannelIDDict[BID][0])
                #ChannelIndex2=ChannelInfo.index(BIDSVChannelIDDict[BID][1])
                    
                #GapPoint=[Gap[ChannelIndex1],Gap[ChannelIndex2]]
                #GapsInRate=TestGapsInRate(BID,GapPoint)
               
                #WavePoints=[Wave[ChannelIndex1],Wave[ChannelIndex2]]
                #WaveInRate=CalWaveInRate(BID,WavePoints)
                GapsInRate=1
                WaveInRate=1
                
                VibEvalutaionDict[BID]=RMS*np.array([GapsInRate,WaveInRate]).mean()     
        HealthEvaluationDataDict={}
        for key in HealthEvaluationRedisKey:
            BID=key.split("_")[0]
            if BID in BearingInfo:
                HealthEvaluationDataDict[key]=float("%.2f"%VibEvalutaionDict[BID])
            if BID=="Average":
                HealthEvaluationDataDict[key]=float("%.2f"%np.array(list(VibEvalutaionDict.values())).mean())
        WriteDataToRedis("HealthEvaluationRedisKey",HealthEvaluationDataDict)            
    return
VibOverallLimitsForTranscient,VibOverallLimitsForStable=ReadVibOverallLimit()
def UpdateCalcParameter():
    global VibOverallLimitsForTranscient
    global VibOverallLimitsForStable
    
    VibOverallLimitsForTranscient,VibOverallLimitsForStable=ReadVibOverallLimit()
    
    print("Updating Parameter!")

    return 


def HeathEvaluation():
    nowtime=datetime.datetime.now().strftime(CalConfig['time_format'][0])
    WriteRunTimeRecord(RunTimeRecord11,nowtime)

    #SpeedChangeFlag=GetFlagFromFile(FlagFilePath,"SpeedChangeFlag")
    SpeedChangeFlag="False"
    
    if SpeedChangeFlag!="" and SpeedChangeFlag.lower()=='true':
        Evaluation=HealthEvaluateForTranscientState()
        print("Health Evaluation at Transcient State for Realtime Redis!")
    else:
        Evaluation=HealthEvaluateForStableState()
        print("Health Evaluation at Stable State for Realtime Redis!")

    return
    

def main():
            
    UpdateCalcParameter()
    
    schedule.every(3).seconds.do(HeathEvaluation)
    #schedule.every(1801).seconds.do(UpdateCalcParameter)
    
    while True:       
        schedule.run_pending()
        
    return  
if __name__ == '__main__':
    main()
    VibOverallLimitsForTranscient, VibOverallLimitsForStable = ReadVibOverallLimit()
    print(VibOverallLimitsForStable)
            
    
