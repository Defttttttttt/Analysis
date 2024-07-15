# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:04:56 2019

@author: 11100027
"""
#############################################
import time
import datetime
import pymysql
import numpy as np
import thinkdsp
import thinkplot
import GenCalcParaFromCSV
import redis


VibSensorInfo=GenCalcParaFromCSV.VibSensorInfo
DBConfig=GenCalcParaFromCSV.DBConfig
CalConfig=GenCalcParaFromCSV.CalConfig
RunTimeRecordPath=GenCalcParaFromCSV.RunTimeRecordPath


MySQLPsw=DBConfig['MySQLPsw'][0]
MySQLDBName=DBConfig['MySQLDBName'][0]

VibWaveRedisIP=DBConfig['VibWaveRedisIP'][0]
VibWaveRedisPort=int(DBConfig['VibWaveRedisPort'][0])
VibWaveRedisDB=int(DBConfig['VibWaveRedisDB'][0])

RunTimeRecord1=RunTimeRecordPath['RunTimeRecord1'][0]

ChannelInfo=[VibSensorInfo[key][2]  for key in VibSensorInfo]
ChannelCount=len(ChannelInfo)



def FloatArrayToString(array): 
    data_str=""
    for i in range(len(array)):
        data_str=data_str+str(array[i])+","
    return data_str[:-1]



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
    amp=[float("%.2f"%amps[index]) for index in Indexs]
    angle=[float("%.2f"%angles[index]) for index in Indexs]

        
    return f,amp,angle


def GenRedisKeyListByChannelCounts():
    KeyList=[]
    KeyList.append("Speed")
    KeyList.append("Gap")
    for i in range(2,ChannelCount+2):
        KeyList.append("%s"%i)
    return KeyList

def ReadRedisPPandSPEC():

    #r=redis.Redis(VibWaveRedisIP,VibWaveRedisPort,db=VibWaveRedisDB)
    #r=redis.Redis("192.168.8.136",VibWaveRedisPort,db=VibWaveRedisDB)
    r = redis.Redis(host="localhost", port=6379, db=1)
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
        VibPP.append(float("%.2f"%(max(OneVibs)-min(OneVibs))))
        SPEC.append(EigenSPEC)
    r.close()
        
    return Speed,Gap,VibPP,SPEC

       
  
def SavePPToDB(LCur,nowtime,ReadSMData):
    (Speed,Gap,VibPP,SPEC)=ReadSMData
    sql_talk="insert into CHNVib values('%s',%d,"%(nowtime,Speed)
    sql_talk+="'%s',"%(FloatArrayToString(Gap))
    sql_talk+="'%s',"%(FloatArrayToString(VibPP))
    SPECString=""
    for OneCHNSPEC in SPEC:
        sql_talk+="'%s',"%(FloatArrayToString(OneCHNSPEC))
    sql_talk=sql_talk[:-1]+")"
    LCur.execute(sql_talk)        
    LCur.execute("commit")       
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
    while True:
        
        nowtime=datetime.datetime.now().strftime(CalConfig['time_format'][0])
        WriteRunTimeRecord(RunTimeRecord1,nowtime)

        #db=pymysql.connect("localhost","root",MySQLPsw,MySQLDBName)
        MySQLDBName='vfdmysqldb'
        db=pymysql.connect(host="10.9.70.170",user="root",password="TDEVib",db=MySQLDBName)
        LCur=db.cursor()

        ReadSMData=ReadRedisPPandSPEC()
        if ReadSMData[0]>45:
            
            SavePPToDB(LCur,nowtime,ReadSMData)
            print("PP and SPEC Complete Saving!")
        
        LCur.close()
        db.close()
        #time.sleep(1)

    return
    
if __name__ == '__main__':
    #pass
    main()
    #print(GenRedisKeyListByChannelCounts())
    