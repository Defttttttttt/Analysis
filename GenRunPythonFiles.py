# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 14:35:21 2020

@author: 11100027
"""
import os

FileListPath="./filelist.txt"
DestFilePath="./RunPythonFiles"

if os.path.exists(FileListPath):
    with open(FileListPath,"r") as file:
        for line in file:
            FilenameList.append(line.split(".")[0])
    FilenameList=[filename for filename in os.listdir() if filename[:3]==".py"]
if os.path.isdir(DestFilePath)==True:
    for filename in os.listdir(DestFilePath):
        os.remove("%s/%s"%(DestFilePath,filename))
else:
    os.mkdir(DestFilePath)
FilenameList=["ReadThermalDataFromSIS"]

    
for filename in FilenameList:
    if filename not in ["Utility","thinkdsp","thinkplot","RunningStateRecognize",\
                        "GenCalcParaFromCSV","GenCalFlagFile","MySQLDBInitial",\
                        "GenRunPythonFiles","filelist"]:
        print(filename)
        ToWriteString=""
        RunPythonFilePath="%s/RunPython%s.py"%(DestFilePath,filename)
        ToWriteString+="import %s\n"%filename
        ToWriteString+="%s.main()"%filename
        with open(RunPythonFilePath,'w') as file:
            file.write(ToWriteString)
    