# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 13:28:42 2022

@author: ziyun
"""

import socket
import struct
import time
import datetime
import math
import numpy as np
import os
import json
import redis
#@@delete
#from matplotlib import pyplot as plt
#filetag_format="%Y%m%d%H%M%S"

RunTimeRecord="./Parameters/VibDaq"
time_format="%Y-%m-%d %H:%M:%S"

def ImportDaqConfig():    
    ParameterCSVPath="./ConfigFiles/DaqConfig.csv"
    ParmDict={}
    
    with open(ParameterCSVPath,'r') as file:
        DataDict={}
    
        for line in file:
            if line.find("parmname")!=-1:
                Parmname=line.replace("\n","").split(",")[1]
                
            if line.find("info")!=-1:
                SubKey=line.replace("\n","").split(",")[1]
                Value=line.replace("\n","").split(",")[2]
                DataDict[SubKey]=Value
                
            if line.find("$$$")!=-1:
                ParmDict[Parmname]=DataDict
                DataDict={}
            
    return ParmDict

ParmDict=ImportDaqConfig()
DaqConfig=ParmDict['DaqConfig']
VibCoef=ParmDict['VibCoef']


SlotCount=int(DaqConfig['SlotCount'])
MaxSampleRate=int(DaqConfig['MaxSampleRate'])
MinSampleRate=int(DaqConfig['MinSampleRate'])
RawWavePoints=int(DaqConfig['RawWavePoints'])
WavePoints=int(DaqConfig['WavePoints'])
WaveCounts=int(DaqConfig['WaveCounts'])
DaqIP=DaqConfig['DaqIP']
LocalIP=DaqConfig['LocalIP']
RatedSpeed=int(DaqConfig["RatedSpeed"])
SystemMaxSpeed=int(DaqConfig['SystemMaxSpeed'])

ChannelCount=4*SlotCount
RestartConfig=int(DaqConfig['RestartConfig'])
RedisHost=DaqConfig['RedisHost']
RedisPort=int(DaqConfig['RedisPort'])
RedisDB=int(DaqConfig['RedisDB'])
RedisParaname=DaqConfig['RedisParaname']
PulsePositeiveFlag=bool(DaqConfig['PulsePositeiveFlag'])
PulseGap=float(DaqConfig['PulseGap'])


#@@
DaqIP="192.168.1.131"
LocalIP="192.168.1.140"
    
def WriteRunTimeRecord(RunTimeRecord,TimeString):
    while True:
        try:
            with open(RunTimeRecord,"w") as file:
                file.write(TimeString)
                break
        except:
            time.sleep(0.1)
        finally:
            break
    return


def ProcessPulseData(Data):
    if PulsePositeiveFlag==True:
        Data=[item-PulseGap for item in Data]
    elif PulsePositeiveFlag==False:
        Data=[PulseGap-item for item in Data]
    return Data

def FloatArrayToString(array): 
    data_str=""
    for i in range(len(array)):
        data_str=data_str+str(array[i])+","
    return data_str[:-1]

def ProcessData(Data):
    NewData=[]
    for item in Data:
        if item > 32767:
            NewData.append((65535-item)/1000)
        else:
            NewData.append(-item/1000)
    return NewData

def ParseBytestring(Bytestring):
    Header=Bytestring[0]
    Something=struct.unpack("<5B",Bytestring[1:6])
    PackageID=Bytestring[6]
    ChannelID=Bytestring[8]
    Data=struct.unpack(">512H",Bytestring[9:1033])
    Tail=Bytestring[-1]
    Data=ProcessData(Data)
    return ChannelID,Data

def BroadCast(udp_socket):
    udp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
    PORT=16500
    network='<broadcast>'
    returninfo=udp_socket.sendto(("Who has %s?  Tell %s"%(DaqIP,LocalIP)).encode("utf-8"),(network,PORT))
    return



def SendConfigToDevice(udp_socket,SampleRate):
    SampleRate=int(SampleRate)
    RandomValueDict={}
    RandomValueDict[1]=[math.floor(SampleRate/16-149)%255]
    RandomValueDict[2]=[math.floor(SampleRate/16-143)%255]
    RandomValueDict[3]=[math.floor(SampleRate/16-137)%255]
    RandomValueDict[4]=[math.floor(SampleRate/16-130)%255]
    RandomValueDict[5]=[math.floor(2712-SampleRate*11/40)%255]
    RandomValueDict[6]=[math.floor(2782-SampleRate*11/40)%255]
    RandomValueDict[7]=[math.floor(2852-SampleRate*11/40)%255]
    RandomValueDict[8]=[math.floor(2921-SampleRate*11/40)%255]
    
    RandomValueDict[2]=[153]
    
    NotFixValue=RandomValueDict[SlotCount]

    RearValueDict={}
    RearValueDict[1]=[0,55,0,0,0,0,0,0,0,39,0,0,0,32,48,49,32,48,48,32,48,48,32]
    RearValueDict[2]=[0,55,0,0,0,0,0,0,0,39,0,0,0,32,48,49,32,48,49,32,48,49,32]
    RearValueDict[3]=[0,55,0,0,0,0,0,0,0,39,0,0,0,32,48,49,32,48,49,32,48,49,32]
    RearValueDict[4]=[0,55,0,0,0,0,0,0,0,39,0,0,0,32,48,49,32,48,49,32,48,49,32]
    RearValueDict[5]=[0,0,0,0,0,2,0,0,0,92,7,0,0,19,0,0,0,0,0,0,0,2,0,0,0,108,7]
    RearValueDict[6]=[0,176,6,0,0,19,0,0,0,0,0,0,0,2,0,0,0,192,6,0,0,75,0,0,0,0,0,0,0,57,0]
    RearValueDict[7]=[0,0,0,0,0,2,0,0,0,132,8,0,0,83,0,0,0,0,0,0,0,65,0,0,0,48,49,32,48,49,32,48,49,32,48]
    RearValueDict[8]=[49,32,48,49,32,48,49,32,48,49,32,48,49,32,48,49,32,48,49,32,48,49,32,48,49,32,48,49,32,48,49,32,48,49,32,48,49,96,1]

    SampleRateBytestring=struct.pack(">H",SampleRate)
    ChannelCount=4*SlotCount
    ChannelCountBytestring=struct.pack(">B",ChannelCount)
    Fore=[68,0,0]
    SampleRateArray=[item for item in SampleRateBytestring]
    ChannelCountArray=[item for item in ChannelCountBytestring]
    ChannelLabelArray=[]
    if SlotCount<=4:
        for i in range(16):
            if i < ChannelCount:
                ChannelLabelArray.append(1)
            else:
                ChannelLabelArray.append(0)
        
    if SlotCount==5:
        ChannelLabelArray=[1 for i in range(20)]
       
    if SlotCount==6:
        ChannelLabelArray=[1 for i in range(24)]
        
    if SlotCount==7:
        ChannelLabelArray=[1 for i in range(28)]
        
    if SlotCount==8:
        ChannelLabelArray=[1 for i in range(32)]
 
    Rear=RearValueDict[SlotCount]
    MessageArray=Fore+SampleRateArray+ChannelCountArray+ChannelLabelArray+NotFixValue+Rear
    if SlotCount<=4:
        MessageBytestring=struct.pack("<46B",*MessageArray)
    elif SlotCount==5:
        MessageBytestring=struct.pack("<54B",*MessageArray)
    elif SlotCount==6:
        MessageBytestring=struct.pack("<62B",*MessageArray)
    elif SlotCount==7:
        MessageBytestring=struct.pack("<70B",*MessageArray)
    elif SlotCount==8:
        MessageBytestring=struct.pack("<78B",*MessageArray)

    client_addr=(DaqIP,16500)
    udp_socket.sendto(MessageBytestring,client_addr)

    return



def StopDaq(udp_socket):
    Message=struct.pack("<B",53)
    client_addr=(DaqIP,16500)
    udp_socket.sendto(Message,client_addr)
    return



def StartService(udp_socket):
    Message=struct.pack("<2B",*[53,0])
    client_addr=(DaqIP,16500)
    udp_socket.sendto(Message,client_addr)
    return



def WriteDataToRedis(Paraname,DataDict):
    r=redis.Redis(host=RedisHost,port=RedisPort,db=RedisDB)
    #r=redis.Redis(host="192.168.8.136",port=9071,db=1)
    #r=redis.Redis(host="localhost",port=9071,db=9)
    dictstring="{"
    for Key in DataDict:
        dictstring+="'%s':'%s',"%(Key,DataDict[Key])
    dictstring=dictstring[:-1]+"}"
        
    while True:
        try:
            r.hmset("%s"%Paraname,eval(dictstring))
            #print("Vib Written Successfully!")
            break
        except:
            print("Vib Written Error..")
            break             
    r.close()
    return



def ReadSpeedFromRedis():
    r=redis.Redis(host=RedisHost,port=RedisPort,db=RedisDB)
    #@@
    #r=redis.Redis(host="localhost",port=9071,db=9)
    KeyList=["WriteTime","Speed"]
    SpeedValidFlag,Speed=[False,0]
    WriteTime,Speed=r.hmget(RedisParaname,KeyList)
    if Speed!=None:
        Speed=int(float(Speed))
        SpeedValidFlag=(datetime.datetime.now()-datetime.datetime.strptime(str(WriteTime,"utf-8"),time_format)).seconds<6
        
    return SpeedValidFlag,Speed




def CalPositivePulse(Data):
    OneWaveCount,PulseJumpIndex=[0,0]
    PositiveItems=[i for i in range(len(Data)) if Data[i]>0]
    ItemDict={}
    JumpKey=1
    ItemDict[JumpKey]=[]
    for i in range(len(PositiveItems)-1):
        ItemDict[JumpKey].append(PositiveItems[i])
        if PositiveItems[i+1]-PositiveItems[i]>5:
            JumpKey+=1
            ItemDict[JumpKey]=[]

    if (len(ItemDict)==2 or len(ItemDict)==3) and (len(ItemDict[2])>0 and len(ItemDict[1])>0):
        PulseJumpIndex=ItemDict[2][0]
        OneWaveCount=ItemDict[2][-1]-ItemDict[1][-1]
    else:
        OneWaveCount,PulseJumpIndex=[0,0]

    return OneWaveCount,PulseJumpIndex


def CalPositivePulseForSpeedBelow100(Data):
    OneWaveCount,PulseJumpIndex=[0,0]
    PositiveItems=[i for i in range(len(Data)) if Data[i]>0]
    ItemDict={}
    JumpKey=1
    ItemDict[JumpKey]=[]
    for i in range(len(PositiveItems)-1):
        if PositiveItems[i+1]-PositiveItems[i]<5:
            ItemDict[JumpKey].append(PositiveItems[i])
        else:
            JumpKey+=1
            ItemDict[JumpKey]=[]
    if len(ItemDict)==2:
        if ItemDict[1]!=[] and ItemDict[2]!=[]:
            PulseJumpIndex=ItemDict[1][0]
            OneWaveCount=ItemDict[2][-1]-ItemDict[1][-1]
            
    elif len(ItemDict)>=3 and len(ItemDict)<6 and ItemDict[3]!=[] and ItemDict[2]!=[]:
        PulseJumpIndex=ItemDict[2][0]
        OneWaveCount=ItemDict[3][-1]-ItemDict[2][-1]
    return OneWaveCount,PulseJumpIndex,len(ItemDict)
    


def TargetFixedSampleRate(SpeedCaled): 
    FixSampleRate=12800
    SpeedCaled=int(SpeedCaled)
    if SpeedCaled in range(2823,3323):
        FixSampleRate=12800
    elif SpeedCaled in range(2423,2823):
        FixSampleRate=11008
    elif SpeedCaled in range(1823,2423):
        FixSampleRate=8704
    elif SpeedCaled in range(1423,1823):
        FixSampleRate=6400
    elif SpeedCaled in range(1123,1423):
        FixSampleRate=5210
    elif SpeedCaled in range(823,1123):
        FixSampleRate=3840
    elif SpeedCaled in range(523,823):
        FixSampleRate=2560
    elif SpeedCaled in range(323,523):
        FixSampleRate=1536
    elif SpeedCaled in range(213,323):
        FixSampleRate=1024
    elif SpeedCaled in range(163,213):
        FixSampleRate=768
    elif SpeedCaled in range(103,163):
        FixSampleRate=512
    elif SpeedCaled in range(40,103):
        FixSampleRate=256
    elif SpeedCaled<40:
        FixSampleRate=128
    return FixSampleRate



def CalUpLimitAndLowLimit(FixSampleRate):
    FixSampleRate=int(FixSampleRate)
    LowLimit,UpLimit=[80,450]
    UpLimitAndLowLimit={}
    UpLimitAndLowLimit[12800]=[220,290]
    UpLimitAndLowLimit[11008]=[210,290]
    UpLimitAndLowLimit[8704]=[200,290]
    UpLimitAndLowLimit[6400]=[190,290]
    UpLimitAndLowLimit[5120]=[200,290]
    UpLimitAndLowLimit[3840]=[200,290]
    UpLimitAndLowLimit[2560]=[160,310]
    UpLimitAndLowLimit[1536]=[160,290]
    UpLimitAndLowLimit[1024]=[160,300]
    UpLimitAndLowLimit[768]=[180,300]
    UpLimitAndLowLimit[512]=[140,340]
    UpLimitAndLowLimit[256]=[100,360]
    UpLimitAndLowLimit[128]=[80,420]
    
    if FixSampleRate in UpLimitAndLowLimit.keys():
        LowLimit,UpLimit=UpLimitAndLowLimit[FixSampleRate]
        
    return LowLimit,UpLimit




def CalBaseSpeedByStep(Step):
    CalSpeed=15
    FoundFlag=False
    while CalSpeed<SystemMaxSpeed+301:
        if CalSpeed>100 and Step >= 100:
            CalSpeed=int(CalSpeed/100)*100+1
        SampleRate=TargetFixedSampleRate(CalSpeed)
        WidthCount_LowLimit,WidthCount_UpLimit=CalUpLimitAndLowLimit(SampleRate)
        udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udp_socket.bind((LocalIP,0))
        StopDaq(udp_socket)
        BroadCast(udp_socket)
        SendConfigToDevice(udp_socket,SampleRate)
        ChannelID,Data=[0,[]]
        for Count in range(10):
            recv_data=udp_socket.recvfrom(1033)
            if len(recv_data[0])==1033:
                ChannelID,Data=ParseBytestring(recv_data[0])
            Count+=1
            if ChannelID==1:
                Data=ProcessPulseData(Data)
                WidthCounts,PulseJumpIndex=CalPositivePulse(Data)
                print("Step:%s,CalSpeed:%s,WidthCounts:%s,PulseJumpIndex:%s"%(Step,CalSpeed,WidthCounts,PulseJumpIndex))
                if WidthCounts in range(WidthCount_LowLimit,WidthCount_UpLimit):
                    FoundFlag=True
                    break
            if ChannelID==2:
                udp_socket.close()
                break
        if Step<20 and CalSpeed>=200:
            CalSpeed=SystemMaxSpeed+301
            break
        
        if FoundFlag:
            break
        CalSpeed+=Step
    return CalSpeed
      


def CalBaseSpeedAtLowSpeed():
    SampleRate=128
    WidthCount_LowLimit,WidthCount_UpLimit=[80,450]
    Speeds=[]
    TestCount=0
    FoundFlag=False
    CalSpeed=0
    while TestCount<301:
        
        SampleRate=TargetFixedSampleRate(CalSpeed)
    
        udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udp_socket.bind((LocalIP,0))
        StopDaq(udp_socket)
        BroadCast(udp_socket)
        SendConfigToDevice(udp_socket,SampleRate)
        ChannelID,Data=[0,[]]

        for Count in range(10):
            Count+=1
            recv_data=udp_socket.recvfrom(1033)
            if len(recv_data[0])==1033:
                ChannelID,Data=ParseBytestring(recv_data[0])

            if ChannelID==1:
                Data=ProcessPulseData(Data)
                #plt.plot(Data)
                #plt.show()
                WidthCounts,PulseJumpIndex=CalPositivePulse(Data)
                print("CalSpeed:%s,WidthCounts:%s,PulseJumpIndex:%s"%(CalSpeed,WidthCounts,PulseJumpIndex))
                
                if WidthCounts in range(WidthCount_LowLimit,WidthCount_UpLimit):
                    NowSpeed=int(SampleRate/WidthCounts*60)
                    Speeds.append(NowSpeed)

            if ChannelID==2:
                udp_socket.close()
                break
            if len(Speeds)>=3:
                CalSpeed=np.array(Speeds).mean()
                FoundFlag=True
        TestCount+=1
        if FoundFlag:
            udp_socket.close()
            break
        if TestCount>=10:
            break
        
    return CalSpeed



def CalBaseSampleRate():
    CalSpeed=0
    CalFlag=False
    
    for Step in [300,200,100,50,10,5]:
        CalSpeed=CalBaseSpeedByStep(Step)
        if CalSpeed < SystemMaxSpeed:
            CalFlag=True
            #print(CalSpeed)
            break
        
    if CalFlag==False:
        CalSpeed=CalBaseSpeedAtLowSpeed()
    print("BaseSpeed:%s"%CalSpeed)
        
    return CalSpeed


def ProcessDataTo256(Data):
    ReturnData=Data
    WidthCounts=len(Data)
    if WidthCounts>256:
        PopCounts=WidthCounts-256
        Step=int(WidthCounts/(PopCounts+1))
        PopIndexs=[int(Step*i+1) for i in range(PopCounts)]
        ReturnData=[Data[i] for i in range(len(Data)) if i not in PopIndexs]
    elif WidthCounts<256:
        ReturnData=[Data[0]]
        PushCounts=256-WidthCounts
        Step=int(WidthCounts/(PushCounts+1))
        PushIndexs=[int(Step*i) for i in range(PushCounts)]
        if len(PushIndexs)>1:
            for j in range(len(PushIndexs)-1):
                FrantIndex=PushIndexs[j]
                RearIndex=PushIndexs[j+1]
                ReturnData+=[Data[FrantIndex]]+Data[FrantIndex:RearIndex]
            ReturnData+=[Data[RearIndex]]+Data[RearIndex:]
        else:
            ReturnData=Data[:128]+[(Data[127]+Data[128])/2]+Data[128:]
    return ReturnData


    

def AnalysisIfStop():
    nowtime=datetime.datetime.now().strftime(time_format)
    WriteRunTimeRecord(RunTimeRecord,nowtime)

    SampleRate=1024
    udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp_socket.bind((LocalIP,0))
    BroadCast(udp_socket)
    StopDaq(udp_socket)
    SendConfigToDevice(udp_socket,SampleRate)
    
    Speeds=[]
    Count=0
    WidthCounts=0
    NewSampleRate=0
    PulseJumpIndex=0
    MeanSpeed=0
    
    PulseGaps=[]
    Flags=[]
    StopFlag=False
    
    AllGapData=[]
    CollectCount=0
    
    while True:
        Count+=1
        ChannelID,Data=[0,[]]       
        recv_data=udp_socket.recvfrom(1033)
        if len(recv_data[0])==1033:
            ChannelID,Data=ParseBytestring(recv_data[0])
        if ChannelID==1:
            Data=ProcessPulseData(Data)
            AllGapData+=Data
            CollectCount+=1
            
        if ChannelID==2 or Count%5==0:
            if Count%3==0:
                SampleRate=MinSampleRate
            else:
                SampleRate=MaxSampleRate
                                
            udp_socket.close()
            udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            udp_socket.bind((LocalIP,0))
            BroadCast(udp_socket)
            StopDaq(udp_socket)
            SendConfigToDevice(udp_socket,SampleRate)
              
        if CollectCount>=5:
            if abs(np.array(AllGapData).mean()-max(AllGapData))<0.01:
                StopFlag=True
            break               
    return StopFlag


def InitialVibData():
    Gap={}
    VibData={}    
    for key in VibCoef:
        VibData[int(key)]=[]
        Gap[int(key)]=0
    return Gap,VibData


def InitialRedis():
    r=redis.Redis(host=RedisHost,port=RedisPort,db=RedisDB)
    #@@
    #r=redis.Redis(host="localhost",port=9071,db=9)
    try:
        r.hkeys("VibDaq")
    except:
        r.close()
        RedisDataDict={}
        RedisDataDict["Speed"]=RatedSpeed
        RedisDataDict["WriteTime"]="2000-1-1 00:00:00"
        WriteDataToRedis(RedisParaname,RedisDataDict)
        
    return
        

def main():
    
    ChannelIDs=[int(key) for key in VibCoef]
    SpeedValidFlag,StopFlag=[True,False]
    StopFlag=AnalysisIfStop()
    MeanSpeed=RatedSpeed
    InitialRedis()
    
    
    while True:
        
        StopFlag=AnalysisIfStop()
        Gap,VibData=InitialVibData()
  
        if StopFlag==False:
            
            Speeds=[]
            
            SpeedValidFlag,RedisSpeed=ReadSpeedFromRedis()

            if SpeedValidFlag:
                MeanSpeed=RedisSpeed
            else:
                MeanSpeed=CalBaseSampleRate()
                
            PreSpeed=MeanSpeed
            
            SampleRate=TargetFixedSampleRate(PreSpeed)
            Speeds.append(PreSpeed)
            
            
            udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            udp_socket.bind((LocalIP,0))
            StopDaq(udp_socket)
            BroadCast(udp_socket)
            StartService(udp_socket)
            SendConfigToDevice(udp_socket,SampleRate)
            BadCount=0
            SpeedStableFlag=False
            
            
            #@@delete
            #TestDict={}
            #RestartConfig=5000
            
            for Count in range(RestartConfig):
                SpeedMean=np.array(Speeds).mean()
                WidthPoints_LowerLimit,WidthPoints_UpperLimit=CalUpLimitAndLowLimit(SampleRate)
               
                ChannelID,Data=[0,[]]
                recv_data=udp_socket.recvfrom(1033)
                if len(recv_data[0])==1033:
                    ChannelID,Data=ParseBytestring(recv_data[0])

                if ChannelID==1:
                    nowtime=datetime.datetime.now().strftime(time_format)
                    Data=ProcessPulseData(Data)
                    WidthCounts,PulseJumpIndex,JumpCount=[0,0,0]
                    if SpeedMean < 300:
                        WidthCounts,PulseJumpIndex,JumpCount=CalPositivePulseForSpeedBelow100(Data)
                    else:
                        WidthCounts,PulseJumpIndex=CalPositivePulse(Data)
                
                    #@@delete
                    #if SampleRate not in TestDict:
                        #TestDict[SampleRate]=[]
                    #TestDict[SampleRate].append(WidthCounts)
                        
                    if WidthCounts!=0:
                        NowSpeed=int(SampleRate/WidthCounts*60)
                    
                    if WidthCounts in range(WidthPoints_LowerLimit,WidthPoints_UpperLimit) and NowSpeed<SystemMaxSpeed:
                        BadCount=0
                        if abs(NowSpeed-SpeedMean)<SystemMaxSpeed*0.15:
                            Speeds.append(NowSpeed)
                            PreSpeed=NowSpeed
                        SampleRate=TargetFixedSampleRate(PreSpeed)
  
                    else:
                        if SpeedMean > 1000:
                            Gap,VibData=InitialVibData() 
                        BadCount+=1
                        NowSpeed=np.array(Speeds).mean()
                        SampleRate=TargetFixedSampleRate(NowSpeed)
                        if (BadCount>=2 and (SpeedMean<500 and SpeedMean >200)) or (BadCount>=4 and SpeedMean>=500):   
                            BadCount=0
                            NowSpeed=CalBaseSampleRate()
                            PreSpeed=NowSpeed
                            Speeds=[]
                            Speeds.append(NowSpeed)
                            SampleRate=TargetFixedSampleRate(NowSpeed)
                            
                            udp_socket.close()
                            udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                            udp_socket.bind((LocalIP,0))
                            StopDaq(udp_socket)
                            BroadCast(udp_socket)
                            StartService(udp_socket)
                            SendConfigToDevice(udp_socket,SampleRate)
                        elif SpeedMean<=200 and BadCount>=6:
                            BadCount=0
                            NowSpeed=CalBaseSampleRate()
                            if NowSpeed==0:
                                StopFlag=True
                                break
                            PreSpeed=NowSpeed
                            Speeds=[]
                            Speeds.append(NowSpeed)
                            SampleRate=TargetFixedSampleRate(NowSpeed)
                            
                            udp_socket.close()
                            udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                            udp_socket.bind((LocalIP,0))
                            StopDaq(udp_socket)
                            BroadCast(udp_socket)
                            StartService(udp_socket)
                            SendConfigToDevice(udp_socket,SampleRate)
                    
                        
                    if len(Speeds)>5:
                        SpeedStableFlag=(abs(max(Speeds[-5:])-np.array(Speeds).mean())<=5 and abs(min(Speeds[-5:])-np.array(Speeds).mean())<=5)
                    if len(Speeds)>15:
                        Speeds=Speeds[-15:]

                if (ChannelID in ChannelIDs) and (WidthCounts in range(WidthPoints_LowerLimit,WidthPoints_UpperLimit)):
                    if Gap[ChannelID]!=0:
                        GapMean=(np.array(Data).mean()+Gap[ChannelID])/2
                    else:
                        GapMean=np.array(Data).mean()
                        
                        
                    Gap[ChannelID]=float("%.4f"%GapMean)
                    Data=[float("%.4f"%((Data[i]-GapMean)*float(VibCoef["%s"%ChannelID]))) for i in range(len(Data))]
                    if PulseJumpIndex+WidthCounts<512:
                        Data=Data[PulseJumpIndex:PulseJumpIndex+WidthCounts]
                    elif PulseJumpIndex-WidthCounts >=0:
                        Data=Data[PulseJumpIndex-WidthCounts:PulseJumpIndex]

                    Data=ProcessDataTo256(Data)
                    PreWave=VibData[ChannelID]
                    PreWave=PreWave[-1024:]
                    if PreWave==[]:
                        VibData[ChannelID]=[Data[i] for i in range(0,len(Data),2)]*8
                    else:
                        RearWave=[Data[i] for i in range(0,len(Data),2)]
                        VibData[ChannelID]=PreWave[128:]+RearWave
                    
                    
                    PreWave=VibData[ChannelID]
                    if PreWave==[]:
                        VibData[ChannelID]=[Data[i] for i in range(0,len(Data),2)]*8
                    else:
                        RearWave=[Data[i] for i in range(0,len(Data),2)]
                        VibData[ChannelID]=PreWave[128:]+RearWave
                
                if ChannelID==ChannelIDs[-1]:
                    RedisDataDict={}
                    RedisDataDict['WriteTime']=nowtime
                    if (abs(PreSpeed-RatedSpeed)<20 or SpeedStableFlag) and SpeedMean>200:
                        RedisDataDict['Speed']=int(np.array(Speeds).mean()*0.998)
                    elif len(Speeds)>=3 :
                        RedisDataDict['Speed']=int(np.array(Speeds[-3:]).mean()*0.998)
                    else:
                        RedisDataDict['Speed']=int(PreSpeed)
                    RedisDataDict['Gap']=FloatArrayToString(list(Gap.values()))
                    SampleRate=TargetFixedSampleRate(RedisDataDict['Speed'])
                    
                    print("SampleRate:%s,RedisSpeed:%s,PreSpeed:%s,SpeedsLen:%s,WidthCounts:%s,BadCount:%s"%(SampleRate,RedisDataDict['Speed'],PreSpeed,len(Speeds),WidthCounts,BadCount))
                    
                    #@@delete
                    #if VibData[2]!=[]:
                        #plt.plot(VibData[2])
                        #plt.show()
                        
                    if (WidthCounts in range(WidthPoints_LowerLimit,WidthPoints_UpperLimit)):
                        for VibKey in VibData:
                            if VibData[VibKey]!=[]:
                                RedisDataDict["%s"%VibKey]=FloatArrayToString(VibData[VibKey])
                        
                    WriteDataToRedis(RedisParaname,RedisDataDict)
                    if SampleRate>2048:
                        time.sleep(0.3)
                    
                    
                if Count%((len(ChannelIDs)+1)*4)>(len(ChannelIDs)+1)*2 and ChannelID==ChannelIDs[-1]:
                    if SpeedMean<300:
                        Gap,VibData=InitialVibData()
                        
                    
                    WriteRunTimeRecord(RunTimeRecord,nowtime)
                    
                    udp_socket.close()
                    udp_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                    udp_socket.bind((LocalIP,0))
                    StopDaq(udp_socket)
                    BroadCast(udp_socket)
                    StartService(udp_socket)
                    SendConfigToDevice(udp_socket,SampleRate)
            
                if StopFlag==True:
                    print("The Power Unit is Stop now!")
                    time.sleep(10)
                    break
            
            #@@delete
            #filetag=datetime.datetime.now().strftime(filetag_format)
            #FilePath="./TestJson/Test_%s.json"%filetag
            #with open(FilePath,"w") as file:
                #json.dump(TestDict,file)
            #print("\n\n\nLLLLLLLLLLLLLLLLLLLLLLLLLLLL @@ Comeplete Saving Json!!\n\n\n")
        
            
    return
    
    

if __name__=='__main__':
    #pass
    #main()
    print(VibCoef)
    print(DaqConfig)
    print(PulsePositeiveFlag)
    print(RedisParaname)
    print(SystemMaxSpeed)
    print(MinSampleRate)
    print(MaxSampleRate)
    print(PulseGap)
    print(InitialVibData())
    print(RatedSpeed)
    print(SlotCount)
    print([int(key) for key in VibCoef])
    print(RestartConfig)