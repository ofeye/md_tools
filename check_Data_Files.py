import pandas as pd
from os import listdir, getcwd, chdir
from os.path import isfile, join, realpath, join, isdir, pardir, abspath, dirname
from re import X, search
from sys import displayhook
import numpy as np; np.random.seed(1)

def findFilePath(startWith,endWith):
    chdir(dirname(abspath(__file__)))
    mypath=getcwd()
    subFolders=[x for x in list(listdir()) if isdir(x)]
    filePathArr=[]
    for fol in range(len(subFolders)):
        subPath=join(mypath,subFolders[fol])
        allFiles = [f for f in listdir(subPath) if isfile(join(subPath,f))]
        for x in allFiles:
            if search("^{}.*{}$".format(startWith,endWith),x):
                fileName=x
                filePathArr.append(join(mypath,subFolders[fol],fileName))
    return filePathArr

def getSingleData(xCol,yCol,FilePath):
    dataFile=open(FilePath,"r").read()
    dataList=[x.split('\t') for x in list(dataFile.split("\n"))]
    return float(dataList[xCol-1][yCol-1])

def checkData(GeomFilePathArr):
    for i,filePath in enumerate(GeomFilePathArr):
        titleName=str(filePath.split("\\")[-2]).split('_')[0]
        try:
            getSingleData(15,1,GeomFilePathArr[i])
        except:
            print("{} bütün verilere sahip değil".format(titleName))

GeomfilePathArr=findFilePath('','dat')
#print(GeomfilePathArr[0])
checkData(GeomfilePathArr)

