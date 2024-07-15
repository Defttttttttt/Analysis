#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 10:56:53 2020

@author: ziyun
"""

import json

def ReadParaFromFile(FilePath,Paraname):
    ParaDict={}
    with open(FilePath,"r") as file:
        for line in file:
            if line.find("parmname")==Paraname:
                pass
            if line.find("info")==0:
                key=line.replace("\n","").split(",")[1]
                values=line.replace("\n","").split(",")[2:]
                ParaDict[key]=values
    return ParaDict

def GenVibGapRedisKey(RealTimeParaDict,BearingInfo):
    VibGapRedisKey=[]
    SVChannels=[ChannelID for ChannelID in RealTimeParaDict if RealTimeParaDict[ChannelID][2]=="ShaftVibration"]
    if SVChannels!=[]:
        SVBearingDict={}
        for BID in BearingInfo:
            SVBearingDict[BID]=[ChannelID for ChannelID in SVChannels if  RealTimeParaDict[ChannelID][0]==BID]
        for BID in SVBearingDict:
            if len(SVBearingDict[BID])==2:
                VibGapRedisKey+=["%s_X_Gap"%BID,"%s_Y_Gap"%BID]
            
    return VibGapRedisKey


def GenVibInofoRedisKey(RealTimeParaDict,BearingInfo):
    VibInfoRedisKey=[]
    SVLabels={}
    SVLabels[1]=["X"]
    SVLabels[2]=["X","Y"]
    SVLabels[3]=["X","Y","Z"]
    
    BVLabels={}
    BVLabels[1]=["A"]
    BVLabels[2]=["A","B"]
    BVLabels[3]=["A","B","C"]
    
    AVLabels={}
    AVLabels[1]=["D"]
    AVLabels[2]=["D","E"]
    AVLabels[3]=["D","E","F"]
    AVLabels[4]=["D","E","F","G"]
    AVLabels[5]=["D","E","F","G","H"]
    AVLabels[6]=["D","E","F","G","H","I"]
    
    xParms=["<1X","1X","2X","3X",">3X"]
    
    VibInfoRedisKey+=["Speed"]
    for BID in BearingInfo:
        SVCount=sum([1 for ChannelID in RealTimeParaDict if RealTimeParaDict[ChannelID][0]==BID \
                     and RealTimeParaDict[ChannelID][2]=='ShaftVibration'])
        print(SVCount)
        if SVCount>0:
            for label in SVLabels[SVCount]:
                VibInfoRedisKey.append("%s%s_overall"%(BID[-1],label))
                for x in xParms:
                    if x=="1X" or x=="2X":
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_angle"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq" % (BID[-1], label, x))
                    elif x=="<1X" or x==">3X":
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq"%(BID[-1],label,x))
                    else:
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq" % (BID[-1], label, x))
          
        BVCount=sum([1 for ChannelID in RealTimeParaDict if RealTimeParaDict[ChannelID][0]==BID \
                     and RealTimeParaDict[ChannelID][2]=='BearingVibration'])
        if BVCount>0:
            for label in BVLabels[BVCount]:
                VibInfoRedisKey.append("%s%s_overall"%(BID[-1],label))
                for x in xParms:
                    if x=="1X" or x=="2X":
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_angle"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq" % (BID[-1], label, x))
                    elif x=="<1X" or x==">3X":
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq"%(BID[-1],label,x))
                    else:
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq" % (BID[-1], label, x))
        
        
        AVCount=sum([1 for ChannelID in RealTimeParaDict if RealTimeParaDict[ChannelID][0]==BID \
                     and RealTimeParaDict[ChannelID][2]=='AxialDisplacement'])
        
        if AVCount>0:
            for label in AVLabels[AVCount]:
                VibInfoRedisKey.append("%s%s_overall"%(BID[-1],label))
                for x in xParms:
                    if x=="1X" or x=="2X":
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_angle"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq" % (BID[-1], label, x))
                    elif x=="<1X" or x==">3X":
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq"%(BID[-1],label,x))
                    else:
                        VibInfoRedisKey.append("%s%s_%s_amp"%(BID[-1],label,x))
                        VibInfoRedisKey.append("%s%s_%s_freq" % (BID[-1], label, x))
    return VibInfoRedisKey



def GenHealthEvaluationRedisKey(BearingInfo):
    HealthEvaluationRedisKey=[]
    HealthEvaluationRedisKey=["%s_HealthEvaluation"%BID for BID in BearingInfo]
    HealthEvaluationRedisKey+=["Average_HealthEvaluation"]
    return HealthEvaluationRedisKey
    

def GenFaultInfoRedisKey(BearingInfo):
    
    FaultInfoRedisKey=[]
    
    
    for BID in BearingInfo:
        FaultInfoRedisKey.append("%s_FaultFlag"%BID)
        FaultInfoRedisKey.append("%s_FaultInfo"%BID)
        FaultInfoRedisKey.append("%s_FaultDiagResult"%BID)
        FaultInfoRedisKey.append("%s_FaultSolution"%BID)
        
    return FaultInfoRedisKey

def GenThermalDataRedisKey(BearingInfo):
    BearingTempRedisKey=[]
    BearingTempRedisKey.append('Load')
    for BID in BearingInfo:
        for i in [1,2]:
            BearingTempRedisKey.append("%s_Temperature_%s"%(BID,i))
    for i in [1,2,3,4]:
        BearingTempRedisKey.append("ThrustBearing_Temperature_%s"%i)
    
    return BearingTempRedisKey
        

def main():
    BrowserConfigFilePath="./ConfigFiles/channel_config.csv"
    RedisJsonFilePath="./ConfigFiles/RealTimeRedisKey.json"
    RealTimeParaDict=ReadParaFromFile(BrowserConfigFilePath,"RealTimePara")
    print(RealTimeParaDict)
    BearingInfo=list(set([RealTimeParaDict[ChannelID][0] for ChannelID in RealTimeParaDict]))
    BearingInfo.sort()
    print(BearingInfo)
    
    VibGapRedisKey=GenVibGapRedisKey(RealTimeParaDict,BearingInfo)
    VibInfoRedisKey=GenVibInofoRedisKey(RealTimeParaDict,BearingInfo)
    HealthEvaluationRedisKey=GenHealthEvaluationRedisKey(BearingInfo)
    FaultInfoRedisKey=GenFaultInfoRedisKey(BearingInfo)
    ThermalDataRedisKey=GenThermalDataRedisKey(BearingInfo)
    
    
    
    RedisKeyDict={}
    
    RedisKeyDict['VibGapRedisKey']=VibGapRedisKey
    RedisKeyDict["VibInfoRedisKey"]=VibInfoRedisKey
    RedisKeyDict["HealthEvaluationRedisKey"]=HealthEvaluationRedisKey
    RedisKeyDict["FaultInfoRedisKey"]=FaultInfoRedisKey
    RedisKeyDict["ThermalDataRedisKey"]=ThermalDataRedisKey
    print(RedisKeyDict)
    with open(RedisJsonFilePath,"w") as file:
        json.dump(RedisKeyDict,file)
    return
     
if __name__ == '__main__':
    main()
       
    
    



