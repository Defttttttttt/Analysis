# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 15:04:45 2019
@author: 11100027
"""
ParameterCSVPath="/home/admin/Analysis/ConfigFiles/calparm.csv"
ParameterCSVPath="D:\布连\轴系振动监测\笔记本轴系资料\Analysis\ConfigFiles\calparm.csv"
global parmdict
parminfo=[]
parmdict=[]
with open(ParameterCSVPath,'r') as file:
    for line in file:
        if line.find("parmname")==0:
            parmname=line.split(r",")[1]
            exec("global %s"%parmname)     
        if line.find("parmtype")==0:
            parmtype=line.replace("\n","").split(r",")[1]                         
        if line.find("colname")==0:
            tempstring=line.replace("\n","").split(r",")[1:]
            colname=[tempstring[i] for i in range(len(tempstring)) if tempstring[i]!=""]
            colname=tuple(colname)              
        if line.find("info")==0:
            parminfo.append(line.replace("\n","").split(r",")[1:len(colname)+1])                    
        if line.find("$$$")==0:
            #处理第一列数据，str->int     
            if parmtype=="tuple":         
                exec("%s"%parmname+'='+"%s"%parminfo)  #给参数变量赋值,只能列表赋值
                exec("%s"%parmname+'=tuple(%s)'%parmname) #由列表转换为元组          
            if parmtype=="dict":
                parminfo1=[[parminfo[j][0],parminfo[j][1:]] for j in range(len(parminfo))]
                exec("%s"%parmname+"=dict(%s)"%parminfo1)              
            parminfo=[]
            parmdict.append((parmname,eval(parmname)))  
parmdict=dict(parmdict) #所有参数的信息
