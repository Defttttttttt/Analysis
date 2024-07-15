# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 15:33:59 2019

@author: 11100027
"""


import pymysql
import os
import json

import MySQLDBInitial
import GenCalFlagFile
import GenCalcParaFromCSV

DBConfig=GenCalcParaFromCSV.DBConfig
CalConfig=GenCalcParaFromCSV.CalConfig
VibSensorInfo=GenCalcParaFromCSV.VibSensorInfo
CalFlagInfo=GenCalcParaFromCSV.CalFlagInfo
VibLimitInfo=GenCalcParaFromCSV.VibLimitInfo
#FaultDetectResult=GenCalcParaFromCSV.FaultDetectResult
MySQLPsw=DBConfig['MySQLPsw'][0]    
MySQLDBName=DBConfig['MySQLDBName'][0]
MySQLInitialFilePath=DBConfig['MySQLInitialFilePath'][0] 

MySQLDBInitial.GenMySQLInitialCSV(MySQLInitialFilePath,VibSensorInfo)
BearingInfo=list(set([VibSensorInfo[key][1] for key in VibSensorInfo]))
BearingInfo.sort()


def ConnectDB():
    #db=pymysql.connect("localhost","root",MySQLPsw)
    #db = pymysql.connect("localhost", "root", 'gmy934146')
    db = pymysql.connect(host="localhost", user="root", password="gmy934146")
    #@@
    #db=pymysql.connect("192.168.8.133","admin","Ziyun615")
    LCur=db.cursor()
    return db,LCur

def main():
    
    
    db,LCur=ConnectDB()
    MySQLDBInitial.DBInitialMain(LCur,MySQLDBName,MySQLInitialFilePath)
    LCur.close()
    db.close()

    #ThermalDBInitialFilePath=DBConfig['ThermalDBInitialFilePath'][0]
    #db=pymysql.connect("localhost","root",LocalPsw,MySQLDBName)
    #LCur=db.cursor()
    #MySQLDBInitial.ThermalDBInitialMain(LCur,MySQLDBName,ThermalDBInitialFilePath)
    #LCur.close()
    #db.close()
    

    FlagFilePath=CalConfig['FlagFilePath'][0]
    VibChannelLimitFilePath=CalConfig['VibChannelLimitFilePath'][0]
    #GapsRecordPath=CalConfig['GapsRecordPath'][0]
    #WavesRecordPath=CalConfig['WavesRecordPath'][0]
    ParametersPath=CalConfig['ParametersPath'][0]
    #FaultDetectResultFilePath=CalConfig['FaultDetectResultFilePath'][0]
    DBWriteFlagFilePath=CalConfig['DBWriteFlagFilePath'][0]
    

    GenCalFlagFile.GenFlagFile(FlagFilePath,CalFlagInfo)
    GenCalFlagFile.GenDBWriteFlagFile(DBWriteFlagFilePath,CalFlagInfo)
    GenCalFlagFile.GenVibLimitFile(VibSensorInfo,VibLimitInfo,VibChannelLimitFilePath)
    #GenCalFlagFile.GenBearingGapsFile(BearingInfo,GapsRecordPath)
    #GenCalFlagFile.GenBearingWavesFile(BearingInfo,WavesRecordPath)
    #GenCalFlagFile.GenFaultDetectResultFile(FaultDetectResult,FaultDetectResultFilePath)
    print("**************************************")
    print("Flag initial files have been created!")
    print("**************************************")
    print("The End of Initial!")
    return
    
if __name__ == '__main__':
    #pass
    main()
       
    

