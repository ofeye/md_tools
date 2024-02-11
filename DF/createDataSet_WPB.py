import pandas as pd
from os import listdir, getcwd, chdir
from os.path import isfile, join, realpath, join, isdir, pardir, abspath, dirname
from re import X, search
import numpy as np

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()

def findFilePath(startWith,endWith,current_dir=None):
    if current_dir==None:
        chdir(dirname(abspath(__file__)))
        mypath=getcwd()
    else:
        mypath=current_dir
    subFolders=[x for x in list(listdir(mypath)) if isdir(join(mypath,x))]
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
    dataList=[x.split(" ") for x in list(dataFile.split("\n"))]
    return float(dataList[xCol-1][yCol-1])

def converKValue(text):
    if len(text)==len(str(int(text))):
        kValue=int(text)
    else:
        kValue=int(text)/(10**(len(text)-1))
    return kValue

def normYMCalc(youngModulus):
    return youngModulus/1020

def calculateVol(dimLow,dimHigh):
    return (dimHigh-dimLow)**3

def normDensityCalc(volumeInA,atomCount):
    angstromToCm=10**(-24)
    atomicToMg=1.66053907*(10**(-21))
    carbonWe=12.011
    atomWei=carbonWe*atomCount
    densityMgCm3=(atomWei*atomicToMg)/((volumeInA*angstromToCm))
    grapheneDens=2300
    return densityMgCm3,densityMgCm3/grapheneDens

def normStressCalc(actualStress):
    grapheneStre=130
    return float(actualStress)/grapheneStre

def getData(dataDict,StressFilePathArr,GeomFilePathArr,spesificStrainRate):
    l=len(StressFilePathArr)
    for i,filePath in enumerate(StressFilePathArr):
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        titleName=filePath.split("/")[-2]
        dataFile=open(filePath,"r").read()
        dataList=[x.split(" ") for x in list(dataFile.split("\n"))]
        parentPath=join(filePath, pardir)
        parPath=realpath(parentPath)
        strainList=[float(dataList[x][0])-float(dataList[1][0]) for x in range(1,len(dataList)-1)]
        stressList=[float(dataList[x][1])-float(dataList[1][1]) for x in range(1,len(dataList)-1)]
        stepNumAtSSR=round(len(strainList)/(max(strainList)/spesificStrainRate))
        try:
            privateKey=int(titleName.split('_')[0])
            hybrid=titleName.split('_')[1]=="Hybrid"
            geom1=titleName.split('_')[2]
            geom2=titleName.split('_')[3]
            length=titleName.split('_')[4]
            kValue=converKValue(titleName.split('_')[5])
            hybPerc=int(titleName.split('_')[6].replace("Perc",""))
            hybCellCnt=int(titleName.split('_')[7])
            nonHybCellCnt=int(titleName.split('_')[8])
            dimLow=getSingleData(5,1,GeomFilePathArr[i])
            dimHigh=getSingleData(5,2,GeomFilePathArr[i])
            maxStress=max(stressList)
            strainAtMaxStress=strainList[stressList.index(maxStress)]
            atomCount=getSingleData(2,1,GeomFilePathArr[i])
            strainatSSR=strainList[stepNumAtSSR]
            stressAtSSR=stressList[stepNumAtSSR]
            volume=calculateVol(dimLow,dimHigh)
            density,normDens=normDensityCalc(volume,atomCount)
            normStress=normStressCalc(maxStress)
            youngModulus=stressAtSSR/strainatSSR
            normYM=normYMCalc(youngModulus)
            

            dataDict["Private_Key"].append(privateKey)
            dataDict["Hybrid"].append(hybrid)
            dataDict["Geom1"].append(geom1)
            dataDict["Geom2"].append(geom2)
            dataDict["length"].append(length)
            dataDict["k_Value"].append(kValue)
            dataDict["Hybrid_Perc"].append(hybPerc)
            dataDict["NonHyb_Cell_Count"].append(nonHybCellCnt)
            dataDict["Hyb_Cell_Count"].append(hybCellCnt)
            dataDict["TotalAtom"].append(atomCount)
            dataDict["DimLow"].append(dimLow)
            dataDict["DimHigh"].append(dimHigh)
            dataDict["Volume"].append(volume)
            dataDict["Density"].append(density)
            dataDict["Norm_Density"].append(normDens)
            dataDict["Max_Stress"].append(maxStress)
            dataDict["Norm_Stress"].append(normStress)
            dataDict["Strain_At_Max_Stress"].append(strainAtMaxStress)
            dataDict["Strain_At_SSR"].append(strainatSSR)
            dataDict["Stress_At_SSR"].append(stressAtSSR)
            dataDict["Young_Modulus"].append(youngModulus)
            dataDict["Norm_Young_Modulus"].append(normYM)
            dataDict["Folder"].append(parPath)
            dataDict["Geom_File"].append(GeomFilePathArr[i])
            dataDict["Stress_File"].append(parentPath)
            

        except:
            print("{} does not have all data.".format(titleName))
    return dataDict

keyList = ["Private_Key","Hybrid","Geom1","Geom2","length","k_Value","Hybrid_Perc","NonHyb_Cell_Count","Hyb_Cell_Count","TotalAtom",
            "DimLow","DimHigh","Volume","Density","Norm_Density","Max_Stress","Norm_Stress","Strain_At_Max_Stress","Strain_At_SSR",
            "Stress_At_SSR","Young_Modulus","Norm_Young_Modulus","Folder","Geom_File","Stress_File"]
dataDict = {}

for i in keyList:
    dataDict[i] = []

chdir(dirname(abspath(__file__)))
absPath=getcwd()

workin_dir=''
filePathArr=findFilePath('stress','out',workin_dir)
GeomfilePathArr=findFilePath('','dat',workin_dir)

dataDict=getData(dataDict,filePathArr,GeomfilePathArr,0.05)

dataDictDF=pd.DataFrame(dataDict,columns=keyList,index=dataDict["Private_Key"])
dataDictDF=dataDictDF.sort_values(by=['Private_Key'])
dataDictDF.to_csv(join(absPath,"out.csv"))
