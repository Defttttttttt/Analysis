# -*- coding: utf-8 -*-
"""
Created on Tue May 14 14:45:24 2019

@author: 11100027
"""
import json
import os


def GenOtherFileDir():
    Dirlist=['./ConfigFiles/FlagFile',"Parameters","log"]
    for DirName in Dirlist:
        if not os.path.isdir(DirName):
            os.mkdir(DirName)
    return

def GenFlagFile(FlagFilePath,CalFlagInfo):
    GenOtherFileDir()
    filestr=""
    for CalFlag in CalFlagInfo:
        if CalFlag.find("DB")==-1:
            filestr=filestr+"%s,%s\n"%(CalFlag,CalFlagInfo[CalFlag][0])
    with open(FlagFilePath,'w') as file:
        file.write(filestr)
        
    GenOtherFileDir()
    return

def GenDBWriteFlagFile(DBWriteFlagFilePath,CalFlagInfo):
    filestr=""
    for CalFlag in CalFlagInfo:
        if CalFlag.find("DB")!=-1:
            filestr=filestr+"%s,%s\n"%(CalFlag,CalFlagInfo[CalFlag][0])
    with open(DBWriteFlagFilePath,'w') as file:
        file.write(filestr)   
    return
    
def GenVibLimitFile(VibSensorInfo,VibLimitInfo,VibChannelLimitFilePath):
    ChannelBIDType=[[VibSensorInfo[key][2],key[2:4]] for key in VibSensorInfo]
    ChannelBIDType=dict(ChannelBIDType)
    
    SVStableLimits=[[VibLimitInfo[key][0].split(" ")[-1],[float(VibLimitInfo[key][3])*0.5,float(VibLimitInfo[key][3]),float(VibLimitInfo[key][4])]] \
    for key in VibLimitInfo if key[:2]=='SV']
    SVStableLimits=dict(SVStableLimits)
    
    SVTranscientLimits=[[VibLimitInfo[key][0].split(" ")[-1],[float(VibLimitInfo[key][1])*0.5,float(VibLimitInfo[key][1]),float(VibLimitInfo[key][2])]] \
    for key in VibLimitInfo if key[:2]=='SV']
    SVTranscientLimits=dict(SVTranscientLimits)
    
    BVStableLimits=[[VibLimitInfo[key][0].split(" ")[-1],[float(VibLimitInfo[key][3])*0.5,float(VibLimitInfo[key][3]),float(VibLimitInfo[key][4])]]\
    for key in VibLimitInfo if key[:2]=='BV']
    BVStableLimits=dict(BVStableLimits)
    
    BVTranscientLimits=[[VibLimitInfo[key][0].split(" ")[-1],[float(VibLimitInfo[key][1])*0.5,float(VibLimitInfo[key][1]),float(VibLimitInfo[key][2])]] \
    for key in VibLimitInfo if key[:2]=='BV']
    BVTranscientLimits=dict(BVTranscientLimits)
    
    ADStableLimits=[[VibLimitInfo[key][0].split(" ")[-1],[float(VibLimitInfo[key][3])*0.5,float(VibLimitInfo[key][3]),float(VibLimitInfo[key][4])]] \
    for key in VibLimitInfo if key[:2]=='AD']
    ADStableLimits=dict(ADStableLimits)
    
    ADTranscientLimits=[[VibLimitInfo[key][0].split(" ")[-1],[float(VibLimitInfo[key][1])*0.5,float(VibLimitInfo[key][1]),float(VibLimitInfo[key][2])]] \
    for key in VibLimitInfo if key[:2]=='AD']
    ADTranscientLimits=dict(ADTranscientLimits)

    SVLimits={"Stable":SVStableLimits,"Transcient":SVTranscientLimits}
    BVLimits={"Stable":BVStableLimits,"Transcient":BVTranscientLimits}
    ADLimits={"Stable":ADStableLimits,"Transcient":ADTranscientLimits}
    
    VibTypeLimits={"SV":SVLimits,"BV":BVLimits,"AD":ADLimits}
    
    VibCHNLimits=[[key,VibTypeLimits[ChannelBIDType[key]]] for key in ChannelBIDType]
    VibCHNLimits=dict(VibCHNLimits)

    with open(VibChannelLimitFilePath,"w") as file:
        json.dump(VibCHNLimits,file)
    
    return    
       
def GenBearingGapsFile(BearingInfo,GapsRecordPath):
    initialdata={'StableSets':[],'TranscientSets':[]}
    if not os.path.isdir(GapsRecordPath):
        os.mkdir(GapsRecordPath) 
    for BID in BearingInfo:
        filename="%s.json"%BID
        filepath=GapsRecordPath+filename
        
        with open(filepath,'w') as file:
            json.dump(initialdata,file)    
    return

def GenBearingWavesFile(BearingInfo,WavesRecordPath):
    initialdata={'StableSets':[],'TranscientSets':[]}
    if not os.path.isdir(WavesRecordPath):
        os.mkdir(WavesRecordPath) 
    for BID in BearingInfo:
        filename="%s.json"%BID
        filepath=WavesRecordPath+filename       
        with open(filepath,'w') as file:
            json.dump(initialdata,file)    
    return

                
def GenFaultDetectResultFile(FaultDetectResult,FaultDetectResultFilePath):
    initialData={}
    initialData['FaultTime']=""
    initialData['FaultInfo']={}

    if not os.path.exists(FaultDetectResultFilePath):
        os.mkdir(FaultDetectResultFilePath)        
         
    for key in FaultDetectResult:
        filename="%s.json"%key
        filepath=FaultDetectResultFilePath+filename
        with open(filepath,'w') as file:
            json.dump(initialData,file)
            
    return




    
   
    
    
    
    
    