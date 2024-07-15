# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:04:56 2019

@author: 11100027
"""
#############################################
import time
import datetime
import GenCalcParaFromCSV
import pymysql
import json
import redis

CalConfig=GenCalcParaFromCSV.CalConfig
DBConfig=GenCalcParaFromCSV.DBConfig
#VibProcessParm=GenCalcParaFromCSV.VibProcessParm
VibSensorInfo=GenCalcParaFromCSV.VibSensorInfo
CalFlagInfo=GenCalcParaFromCSV.CalFlagInfo
RunTimeRecordPath=GenCalcParaFromCSV.RunTimeRecordPath

RunTimeRecord=RunTimeRecordPath['RunTimeRecord2'][0]

   
MySQLPsw=DBConfig['MySQLPsw'][0]
MySQLDBName=DBConfig['MySQLDBName'][0]

VibWaveWriteSleepTimeInterval=120
   

VibWaveRedisIP=DBConfig['VibWaveRedisIP'][0]
VibWaveRedisPort=DBConfig['VibWaveRedisPort'][0]
VibWaveRedisDB=int(DBConfig['VibWaveRedisDB'][0])

ChannelInfo=[VibSensorInfo[key][2]  for key in VibSensorInfo]
ChannelCount=len(ChannelInfo)


def FloatArrayToString(array):
    data_str=""
    for i in range(len(array)):
        data_str=data_str+str(array[i])+","
    return data_str[:-1]

            



def GenRedisKeyListByChannelCounts():
    KeyList=[]
    KeyList.append("Speed")
    for i in range(2,ChannelCount+2):
        KeyList.append("%s"%i)
    return KeyList

def ReadRedisWave():
    #@@
    #r=redis.Redis(VibWaveRedisIP,VibWaveRedisPort,db=VibWaveRedisDB)
    #@@
    #r=redis.Redis(host="192.168.8.136",port=9071,db=1)
    r = redis.Redis(host="localhost", port=6379, db=1)
    
    RedisParaName="VibDaq"
    RedisKeyList=GenRedisKeyListByChannelCounts()
    DataArray=r.hmget('%s'%RedisParaName,RedisKeyList)
    Speed=int(DataArray[0])
    WavePoint=[128]*ChannelCount
    VibData=[]
    print("Speed:%s"%Speed)

    for i in range(1,len(DataArray)):
        OneVibs=list(eval(str(DataArray[i],encoding="utf-8")))
        VibData.append(OneVibs)
        
    r.close()
        
    return Speed,WavePoint,VibData

  

def SaveWaveToDB(LCur,nowtime,ReadSMData):
    
    (Speed,WavePoint,VibData)=ReadSMData
    sql_talk="insert into CHNWave values('%s',%d,"%(nowtime,Speed)
    sql_talk+="'%s',"%(FloatArrayToString(WavePoint))
    for OneData in VibData:
        sql_talk+="'%s',"%(FloatArrayToString(OneData)) 
    sql_talk=sql_talk[:-1]+')'
    LCur.execute(sql_talk)        
    LCur.execute("commit")       
    
    return

def WriteRunTimeRecord(TimeString):
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
        WriteRunTimeRecord(nowtime)
        #db=pymysql.connect("localhost","root",MySQLPsw,MySQLDBName)
        db = pymysql.connect(host="localhost", user="root", password="gmy934146", db=MySQLDBName)
        LCur=db.cursor()
        ReadSMData=ReadRedisWave()
        if ReadSMData[0]>100:
            SaveWaveToDB(LCur,nowtime,ReadSMData)
            print("Wave Comeplete Saving!")
        LCur.close()
        time.sleep(VibWaveWriteSleepTimeInterval)
        
    return
    
if __name__ == '__main__':
    #pass
    #main()
    print(ChannelCount)
    