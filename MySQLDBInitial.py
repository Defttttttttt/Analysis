# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 08:38:57 2019

@author: 11100027
"""

   
import os,sys



def GenMySQLInitialCSV(Path,VibSensorInfo):

    CsvStr=""
    ChannelInfo=[VibSensorInfo[key][2]  for key in VibSensorInfo]  
    CsvStr+="tablename,CHNWave\n"
    CsvStr+="colname,Time,coltype,datetime primary key\n"
    CsvStr+="colname,Speed,coltype,int\n"
    CsvStr+="colname,WavePoint,coltype,blob\n"
    
    for ChannelId in ChannelInfo:
        CsvStr+="colname,%sWave,coltype,blob\n"%ChannelId
    CsvStr+="$$$\n"

    CsvStr+="tablename,CHNVib\n"
    CsvStr+="colname,Time,coltype,datetime primary key\n"
    CsvStr+="colname,Speed,coltype,int\n"
    CsvStr+="colname,Gap,coltype,blob\n"
    CsvStr+="colname,VibPP,coltype,blob\n"
    for ChannelId in ChannelInfo:
        CsvStr+="colname,%sSPEC,coltype,blob\n"%ChannelId
    CsvStr+="$$$\n"
        
    if os.path.exists(Path):
        os.remove(Path)
    
    with open(Path,'w') as file:
        file.write(CsvStr)
        
    return



def CreateDatabase(DatabaseName,cursor):
    cursor.execute("show databases")
    DBNames=[tuple[0] for tuple in cursor.fetchall()]
    #Linux Sys: if DatabaseName in DBNames:
    if DatabaseName.lower() in DBNames:
        cursor.execute("drop database %s"%DatabaseName)  
    cursor.execute("create database %s"%DatabaseName)
    print("*********************************************")
    print("The new database %s has been created!"%DatabaseName)
    print("*********************************************")
    return

def CreateNewTable(Tablename,ColumnName,ColumnType,cursor):
    length=len(ColumnName)
    sql_talk='create table '+ "%s"%Tablename+' ('
    for i in range(0,length):
        sql_talk=sql_talk+"`%s`"%ColumnName[i]+' '+"%s"%ColumnType[i]+','
        continue
    sql_talk=sql_talk[:-1]
    sql_talk=sql_talk+')'
    cursor.execute(sql_talk)
    print("The table %s has been created!"%Tablename)    
    return

def DBInitialMain(cursor,MySQLDBName,MySQLInitialFilePath): 
    CreateDatabase(MySQLDBName,cursor)  
    cursor.execute("use %s"%MySQLDBName)    
    with open(MySQLInitialFilePath,'r') as file:
        colname=[]
        coltype=[]
        for line in file:
            if line.find("tablename")!=-1:
                tablename=line.replace("\n","").split(",")[1]
            if line.find("colname")!=-1:
                colname.append(line.replace("\n","").split(",")[1])
                coltype.append(line.replace("\n","").split(",")[3])
            if line.find("$$$")!=-1:
                CreateNewTable(tablename,colname,coltype,cursor)
                colname=[]
                coltype=[]
    return


def ThermalDBInitialMain(cursor,MySQLDBName,ThermalDBInitialFilePath): 
    import pandas as pd
    import os
    
    cursor.execute("use %s"%MySQLDBName)    
    for sheetid in [0,1,2,3]:
            
        df=pd.read_excel(ThermalDBInitialFilePath,sheetid)
        #df.to_csv('temp.csv',encoding='ISO-8859-1')
        df.to_csv('temp.csv',encoding='gbk')
        
        with open('temp.csv','r') as file:
            colname=[]
            coltype=[]
            for line in file:
                if line.find("tablename")!=-1:
                    tablename=line.replace("\n","").split(",")[2]
                if line.find("colname")!=-1:
                    colname.append(line.replace("\n","").split(",")[2])
                    coltype.append(line.replace("\n","").split(",")[4])
                if line.find("$$$")!=-1:
                    CreateNewTable(tablename,colname,coltype,cursor)
                    colname=[]
                    coltype=[]
                if line=="":
                    break
        
    os.remove('temp.csv')
    return
