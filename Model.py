import open3d as o3d
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
from os import listdir, getcwd, chdir, mkdir
from os.path import isfile, join, join, isdir, abspath, dirname
from re import search
from time import time
import cv2
import joblib
import pickle
from functions import flatten_extend, heatmapPlot
import time
import mmap
import scipy.stats as stats




class Model:
    
    def __init__(self,folder):
        self.folder = folder
        
        self.geomFile , self.dumpFile , self.stressFile = self.get_files()
        
        self.geomDataList = None
        self.pointCloudList , self.dimData = None , None
        self.pointCloudListWRealDims = None
        self.pointCloudListRealDimsAsXYZ = None
        self.strainList , self.stressList = None, None
        self.normStressList = None
  
        self.tsCount = None
        
        self.title=self.get_title()
        self.privateKey , self.hybrid , self.geom1 , self.geom2 , self.length , self.hybPerc , self.hybCellCnt , self.nonHybCellCnt = self.get_title_parameters()        
        self.kValue = self.get_kValue()
        self.dimLow , self.dimHigh = None, None
        self.atomCount = None
        self.volume = None
        self.density , self.normDens = None, None
        self.maxStress = None
        self.normStress = None
        self.strainAtMaxStress = None
        self.spesificStrainRate , self.stepNumAtSSR = None, None
        self.strainatSSR = None
        self.stressAtSSR = None
        self.youngModulus = None
        self.normYM = None
        self.elastic_strain_energy , self.strain_energy = None, None
        
        self.o3dPointCloud = None
        
    def getSingleData(self,xCol,yCol,dataList):
        return float(dataList[xCol-1][yCol-1])
    
    def get_files(self):
        allFiles = [f for f in listdir(self.folder) if isfile(join(self.folder,f))]
        for x in allFiles:
            if search("^{}.*{}$".format('\d','.dat'),x):
                geomFile = join(self.folder,x)
            elif search("^{}.*{}$".format('dump','lammpstrj'),x):
                dumpFile = join(self.folder,x)
            elif search("^{}.*{}$".format('stress','.out'),x):
                stressFile = join(self.folder,x)        
    
        return geomFile, dumpFile, stressFile
    
    def get_title(self):
        if (self.geomFile.split("/")[-2]==self.dumpFile.split("/")[-2]) & (self.stressFile.split("/")[-2]==self.dumpFile.split("/")[-2]):
            return self.stressFile.split("/")[-2]
        else:
            print('Geometry and data file names are not matched.')
    
    def get_title_parameters(self):
        privateKey=int(self.title.split('_')[0])
        hybrid=self.title.split('_')[1]=="Hybrid"
        geom1=self.title.split('_')[2]
        geom2=self.title.split('_')[3]
        length=int(self.title.split('_')[4])
        hybPerc=int(self.title.split('_')[6].replace("Perc",""))
        hybCellCnt=int(self.title.split('_')[7])
        nonHybCellCnt=int(self.title.split('_')[8])
        
        return privateKey,hybrid,geom1,geom2,length,hybPerc,hybCellCnt,nonHybCellCnt
    
    def get_kValue(self):
        k_str=self.title.split('_')[5]
        if float(k_str)==0:
            kvalue=0
        else:
            kvalue=int(k_str)/(10**(len(k_str)-1))
        return kvalue
    
    def get_big_data(self):
        
        self.geomDataList = self.get_geom_data()
        self.pointCloudList , self.dimData = self.get_point_data()
        self.pointCloudListWRealDims = self.get_real_dim_pcd()
        self.strainList ,self.stressList = self.get_ss_data()
        
        self.tsCount = self.get_ts_count()
        
        self.dimLow , self.dimHigh = self.get_Dims()
        self.atomCount = self.get_atomCount()
        self.volume = self.get_volume()
        self.density , self.normDens = self.get_density()
        self.maxStress = self.get_maxStress()
        self.normStress = self.get_normStress()
        self.strainAtMaxStress = self.get_strainMaxS()
        self.spesificStrainRate , self.stepNumAtSSR = self.define_SSR()
        self.strainatSSR = self.get_strainatSSR()
        self.stressAtSSR = self.get_stressatSSR()
        self.youngModulus = self.get_youngModulus()
        self.normYM = self.get_normYM()
        self.elastic_strain_energy , self.strain_energy = self.get_strain_energy()
        
        self.normStressList =  self.get_norm_ss_data()

    def set_ss_data(self):
        self.strainList ,self.stressList = self.get_ss_data()
        self.geomDataList = self.get_geom_data()
        self.dimLow , self.dimHigh = self.get_Dims()
        self.atomCount = self.get_atomCount()
        self.volume = self.get_volume()
        self.density , self.normDens = self.get_density()
        self.normStressList =  self.get_norm_ss_data()
        
        
    def set_ts_data(self):
        pass

    
    def get_Dims(self):
        return self.getSingleData(5,1,self.geomDataList),self.getSingleData(5,2,self.geomDataList)
    
    def get_atomCount(self):
        return int(self.getSingleData(2,1,self.geomDataList))

    
    def get_volume(self):
        return (self.dimHigh-self.dimLow)**3
        
    def get_point_data(self):
        dataFile=open(self.dumpFile,"r").read()
        dataList=[x.split(" ") for x in list(dataFile.split("\n"))]
                
        numberOfSteps=dataList.count(['ITEM:','TIMESTEP'])  
        dataLen=int((len(dataList)-1)/numberOfSteps)
                
        timeStepData=[[[int(x[0]),int(x[1]),float(x[2]),float(x[3]),float(x[4])] for x in dataList[(((timeStep)*dataLen)+9):(timeStep+1)*dataLen:]] for timeStep in range(numberOfSteps)]
        timeStepData=[sorted(tslist, key = lambda x:x[0]) for tslist in timeStepData]
        
        dimData = [[[float(x[0]),float(x[1])] for x in dataList[(((timeStep)*dataLen)+5):(((timeStep)*dataLen)+8):]] for timeStep in range(numberOfSteps)]
        return timeStepData , dimData
    
    def get_ts_count(self):
        return len(self.pointCloudList)
    
    def get_ss_data(self):
        dataFile=open(self.stressFile,"r").read()
        dataList=[x.split(" ") for x in list(dataFile.split("\n"))]
        strainList=[float(dataList[x][0])-float(dataList[1][0]) for x in range(1,len(dataList)-1)]
        stressList=[float(dataList[x][1])-float(dataList[1][1]) for x in range(1,len(dataList)-1)]
        return strainList, stressList
    
    def get_norm_ss_data(self):
        normstressList = [x/self.density for x in self.stressList]
        return normstressList
    
    def get_geom_data(self):
        dataFile=open(self.geomFile,"r",).read()
        return [x.split(" ") for x in list(dataFile.split("\n"))]
    
    def get_density(self):
        angstromToCm=10**(-24)
        atomicToMg=1.66053907*(10**(-21))
        carbonWe=12.011
        atomWei=carbonWe*self.atomCount
        densityMgCm3=(atomWei*atomicToMg)/((self.volume*angstromToCm))
        grapheneDens=2300
        return densityMgCm3,densityMgCm3/grapheneDens
    
    def get_maxStress(self):
        return max(self.stressList)
    
    def get_normStress(self):
        grapheneStre=130
        return float(self.maxStress)/grapheneStre
    
    def define_SSR(self):
        spesificStrainRate = 0.05
        return spesificStrainRate , int(len(self.strainList)/(max(self.strainList)/spesificStrainRate))
    
    def get_strainMaxS(self):
        return self.strainList[self.stressList.index(self.maxStress)]
    
    def get_strainatSSR(self):
        return self.strainList[self.stepNumAtSSR]

    def get_stressatSSR(self):
        return self.stressList[self.stepNumAtSSR]
    
    def get_youngModulus(self):
        return self.stressAtSSR/self.strainatSSR
        
    def get_normYM(self):
        grapheneYM = 1020
        return self.youngModulus/grapheneYM
    
    def get_strain_energy(self): 
        max_index=self.stressList.index(self.maxStress)

        strain_energy=0
        for ind in range(1,len(self.stressList)):
            ort_stress=(self.stressList[ind]+self.stressList[ind-1])/2
            thickness=(self.strainList[ind]-self.strainList[ind-1])
            
            strain_energy+=ort_stress*thickness
            
            if ind==max_index:
                elastic_strain_energy=strain_energy
            
        return elastic_strain_energy,strain_energy
    
    def get_real_dim_pcd(self):
        pcdList=list()
        for tsList,dimList in zip(self.pointCloudList,self.dimData):
            xDim = dimList[0][1] - dimList[0][0]
            yDim = dimList[1][1] - dimList[1][0]
            zDim = dimList[2][1] - dimList[2][0]
                        
            pcdList.append([[x[2]*xDim+dimList[0][0],x[3]*yDim+dimList[1][0],x[4]*zDim+dimList[2][0]] for x in tsList])
                    
        return pcdList
    
    def set_real_dim_pcd_xyz(self):
        real_dim_pcd_xyz_arr=list()
        for ts in range(self.tsCount):
            xyzValArr=self.pointCloudListWRealDims[ts]
            real_dim_pcd_xyz_arr.append([ [x[0] for x in xyzValArr] , [x[1] for x in xyzValArr] , [x[2] for x in xyzValArr]])
            
        self.pointCloudListRealDimsAsXYZ = real_dim_pcd_xyz_arr
        return real_dim_pcd_xyz_arr
    
    def set_real_dim_pcd_xyz_lowMem(self):
        dataFile=open(self.dumpFile,"r").read()
        dataList=[x.split(" ") for x in list(dataFile.split("\n"))]
                
        numberOfSteps=dataList.count(['ITEM:','TIMESTEP'])  
        dataLen=int((len(dataList)-1)/numberOfSteps)
                
        timeStepData=[[[float(x[0]),float(x[1]),float(x[2]),float(x[3]),float(x[4])] for x in dataList[(((timeStep)*dataLen)+9):(timeStep+1)*dataLen:]] for timeStep in range(numberOfSteps)]
        timeStepData=[sorted(tslist, key = lambda x:x[0]) for tslist in timeStepData]
        self.atomCount=len(timeStepData[0])
        self.tsCount=len(timeStepData)
        
        dimData = [[[float(x[0]),float(x[1])] for x in dataList[(((timeStep)*dataLen)+5):(((timeStep)*dataLen)+8):]] for timeStep in range(numberOfSteps)]
        
        self.dimData = dimData 
        
        pcdList=list()
        for tsList,dimList in zip(timeStepData,dimData):
            xDim = dimList[0][1] - dimList[0][0]
            yDim = dimList[1][1] - dimList[1][0]
            zDim = dimList[2][1] - dimList[2][0]
                        
            pcdList.append([[x[2]*xDim+dimList[0][0],x[3]*yDim+dimList[1][0],x[4]*zDim+dimList[2][0]] for x in tsList])
        
        pcdListAsXYZ=list()
        for pcdArr in pcdList:
            pcdListAsXYZ.append([ [x[0] for x in pcdArr] , [x[1] for x in pcdArr] , [x[2] for x in pcdArr]])
            
        self.pointCloudListRealDimsAsXYZ = pcdListAsXYZ
        
        #return pointCloudListRealDimsAsXYZ
            
    def set_o3d_Point_Cloud(self):
        pcdArr=list()
        for tsList in self.pointCloudListWRealDims:
            pcd=o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(np.array([[x[0],x[1],x[2]] for x in tsList]))
            pcdArr.append(pcd)
        
        self.o3dPointCloud = pcdArr
        
        return pcdArr
    
    def ss_curve(self, fig=None, label='' , ylabel=''):
        plt.style.use("_mpl-gallery")
                
        xvalues = self.stressList
        yvalues = self.strainList

        plt.plot(yvalues,xvalues,label=label)
        
        plt.xlabel("Strain")
        plt.ylabel(ylabel)
    
    
    def save_timestepViews(self, save_dir=None):
        if save_dir==None:
            save_dir=self.folder
        else:
            save_dir=join(save_dir,self.title)
            if not isdir(save_dir):
                mkdir(save_dir)
                    
        xyzVals=self.pointCloudListRealDimsAsXYZ
        
        col=[sum(i**2 for i in x)**0.5 for x in zip(*xyzVals[0])]
        
        for ts,xyzValArr in enumerate(xyzVals):
            
            fig=plt.figure(figsize=(16,10))
            ax=plt.axes()

            size=1e6/(self.atomCount)
            
            ax.scatter(xyzValArr[0], xyzValArr[1],s=size,c=col, alpha=0.8)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_aspect('equal', 'box')
            
            if not isdir(join(save_dir,'Time_Step_Views')):
                mkdir(join(save_dir,'Time_Step_Views'))
            
            plt.savefig(join(save_dir,'Time_Step_Views','ts{}_strain{}.png'.format(ts,str(round((0.5*ts)/self.tsCount,2)).replace('.',''))))
            plt.close()

    def save_timestepHeatMaps(self, s, bins=1000, save_dir=None):
        if save_dir==None:
            save_dir=self.folder
        else:
            save_dir=join(save_dir,self.title)
            if not isdir(save_dir):
                mkdir(save_dir)
        
        xyzVals=self.pointCloudListRealDimsAsXYZ
        all_values=[heatmapPlot(xyzVals[0], xyzVals[1], s, bins) for xyzVals  in xyzVals]
        flat_list=[flatten_extend(x[0]) for x in all_values]
        flat_list_min_max=[[min(x),max(x)] for x in flat_list]

        all_min=min([x[0] for x in flat_list_min_max])
        all_max=max([x[1] for x in flat_list_min_max])
        
        dimList=self.dimData

        if not isdir(join(save_dir,'Heat_Map_Views')):
            mkdir(join(save_dir,'Heat_Map_Views'))

        for ts,val in enumerate(all_values):
            img=val[0]
            extent=val[1]
            
            fig=plt.figure(figsize=(20,10))
            ax=plt.axes()
            
            ax.set_xlim(dimList[ts][0][0],dimList[ts][0][1])
            ax.set_ylim(dimList[ts][1][0],dimList[ts][1][1])
            
            cmap=cm.jet
            
            min_color = cmap(all_min / all_max)
            ax.set_facecolor(min_color)
        
            scat=ax.imshow(img, extent=extent, origin='lower',cmap=cmap,vmin=all_min,vmax=all_max)
            fig.colorbar(scat)
            

            plt.savefig(join(save_dir,'Heat_Map_Views','ts{}_strain{}_s{}.png'.format(ts,str(round((0.5*ts)/self.tsCount,2)).replace('.',''),s)))
            plt.close()
    
    def save_density_over_x(self, save_dir=None):
        if save_dir==None:
            save_dir=self.folder
        else:
            save_dir=join(save_dir,self.title)
            if not isdir(save_dir):
                mkdir(save_dir)
        
        x_size = 10
        y_size = 5

        dimlist=self.dimData

        initial_size = [dimlist[0][0][1]-dimlist[0][0][0],dimlist[0][1][1]-dimlist[0][1][0]]

        dim_arr=[(x_size*(x[0][1]-x[0][0])/initial_size[0],y_size*(x[1][1]-x[1][0])/initial_size[1]) for x in dimlist]

        if not isdir(join(save_dir,'1D_Dens')):
            mkdir(join(save_dir,'1D_Dens'))

        for ts,test_data in enumerate(self.pointCloudListRealDimsAsXYZ):
            fig=plt.figure(figsize=dim_arr[ts])
            ax=plt.axes()

            test_dat=test_data[0]
            bins=self.length*2

            density = stats.gaussian_kde(test_dat)
            n, x, _ = ax.hist(test_dat, bins=bins, histtype=u'step', density=True) 
            
            if ts==0:
                ylim_max=max(n)*1.1
            
            plt.plot(x, density(x))
            plt.ylim(0,ylim_max)
            plt.savefig(join(save_dir,'1D_Dens','ts{}_strain{}.png'.format(ts,str(round((0.5*ts)/self.tsCount,2)).replace('.',''))))
            plt.close()

    def save_combined_graphs(self, save_dir=None):
        if save_dir==None:
            save_dir=self.folder
        else:
            save_dir=join(save_dir,self.title)
            if not isdir(save_dir):
                mkdir(save_dir)
        s=16

        xyzVals=self.pointCloudListRealDimsAsXYZ

        col=[sum(i**2 for i in x)**0.5 for x in zip(*xyzVals[0])]

        height_ratios=[1, 4]
        x_size = height_ratios[0]
        y_size = height_ratios[1]

        dimlist=self.dimData
        bins=self.length*2

        initial_size = [dimlist[0][0][1]-dimlist[0][0][0],dimlist[0][1][1]-dimlist[0][1][0]]

        all_values=[heatmapPlot(xyzVal[0], xyzVal[1], s, bins=1000) for xyzVal  in xyzVals]
        flat_list=[flatten_extend(x[0]) for x in all_values]
        flat_list_min_max=[[min(x),max(x)] for x in flat_list]

        all_min=min([x[0] for x in flat_list_min_max])
        all_max=max([x[1] for x in flat_list_min_max])


        dim_arr=[(x_size*(x[1][1]-x[1][0])/initial_size[0],y_size*(x[0][1]-x[0][0])/initial_size[1]) for x in dimlist]
        box_dim_arr = [(x[0][1]-x[0][0])/initial_size[0] for x in dimlist]

        multiplier = 1.55

        heigh_size = 9
        width_size = height_ratios[1] * (heigh_size/sum(height_ratios)) * multiplier * 2  
        
        for ts,xyzValArr in enumerate(xyzVals):
            fig, axs = plt.subplots(2, 2,figsize=(width_size,heigh_size), gridspec_kw={'height_ratios': height_ratios, 'width_ratios': [1,1]})

            size=0.6*heigh_size*1e5/(self.atomCount)
            density = stats.gaussian_kde(xyzValArr[0])
            
            axs[1,0].scatter(xyzValArr[0], xyzValArr[1],s=size,c=col, alpha=0.8)
            axs[1,0].set_aspect('equal', 'box')
            fig.tight_layout()
            
            cmap=cm.jet

            img=all_values[ts][0]
            extent=all_values[ts][1]
            min_color = cmap(all_min / all_max)
            axs[1,1].set_facecolor(min_color)
            axs[1,1].imshow(img, extent=extent, origin='lower',cmap=cmap,vmin=all_min,vmax=all_max)
            
            _, x1, _ = axs[0,0].hist(xyzValArr[0], bins=bins, lw=2, histtype=u'step')
            _, x2, _ = axs[0,1].hist(xyzValArr[0], bins=bins, lw=2, histtype=u'step')
            axs[0,0].plot(x1, density(x1))
            axs[0,0].set_box_aspect(dim_arr[ts][0]/dim_arr[ts][1])
            axs[0,0].axis('off')

            axs[0,1].plot(x2, density(x2))
            axs[0,1].set_box_aspect(dim_arr[ts][0]/dim_arr[ts][1])
            axs[0,1].set_xlim(dimlist[ts][0][0],dimlist[ts][0][1])
            axs[0,1].axis('off')
            
            plt.subplots_adjust(left=0, right=1, bottom=0.03, top=1, wspace=0, hspace=0)
            
            plt.savefig(join(save_dir,'ts{}_strain{}.jpg'.format(ts,str(round((0.5*ts)/self.tsCount,2)).replace('.',''))),dpi=300)
            plt.close()


'''
model1=Model('/Users/osmanfurkanyilmaz/Desktop/Test_Analysis/10_Hybrid_SchwarzD_SchwarzP_30_09_Perc50_1_2_29_142_202208220508')
s=16

model1.set_real_dim_pcd_xyz_lowMem()
xyzVals=model1.pointCloudListRealDimsAsXYZ

col=[sum(i**2 for i in x)**0.5 for x in zip(*xyzVals[0])]

height_ratios=[1, 4]
x_size = height_ratios[0]
y_size = height_ratios[1]

dimlist=model1.dimData
bins=model1.length*2

initial_size = [dimlist[0][0][1]-dimlist[0][0][0],dimlist[0][1][1]-dimlist[0][1][0]]

all_values=[heatmapPlot(xyzVal[0], xyzVal[1], s, bins=1000) for xyzVal  in xyzVals]
flat_list=[flatten_extend(x[0]) for x in all_values]
flat_list_min_max=[[min(x),max(x)] for x in flat_list]

all_min=min([x[0] for x in flat_list_min_max])
all_max=max([x[1] for x in flat_list_min_max])


dim_arr=[(x_size*(x[1][1]-x[1][0])/initial_size[0],y_size*(x[0][1]-x[0][0])/initial_size[1]) for x in dimlist]
box_dim_arr = [(x[0][1]-x[0][0])/initial_size[0] for x in dimlist]

multiplier = 1.55

heigh_size = 9
width_size = height_ratios[1] * (heigh_size/sum(height_ratios)) * multiplier * 2

for ts,xyzValArr in enumerate(xyzVals):
    fig, axs = plt.subplots(2, 2,figsize=(width_size,heigh_size), gridspec_kw={'height_ratios': height_ratios, 'width_ratios': [1,1]})# [(1+(ts/25)*0.5)*(1/1.7),(1+(ts/25)*0.5)*(1/1.7)] })

    size=0.6*heigh_size*1e5/(model1.atomCount)
    density = stats.gaussian_kde(xyzValArr[0])
    
    axs[1,0].scatter(xyzValArr[0], xyzValArr[1],s=size,c=col, alpha=0.8)
    axs[1,0].set_aspect('equal', 'box')
    #axs[1,0].axis('off')
    fig.tight_layout()
    
    cmap=cm.jet

    img=all_values[ts][0]
    extent=all_values[ts][1]
    min_color = cmap(all_min / all_max)
    axs[1,1].set_facecolor(min_color)    
    scat=axs[1,1].imshow(img, extent=extent, origin='lower',cmap=cmap,vmin=all_min,vmax=all_max)
    #fig.colorbar(scat)    
    #axs[1,1].axis('off')
    
    n1, x1, _ = axs[0,0].hist(xyzValArr[0], bins=bins, lw=2, histtype=u'step')#, density=True) 
    n2, x2, _ = axs[0,1].hist(xyzValArr[0], bins=bins, lw=2, histtype=u'step')#, density=True) 
    axs[0,0].plot(x1, density(x1))
    axs[0,0].set_box_aspect(dim_arr[ts][0]/dim_arr[ts][1])
    axs[0,0].axis('off')

    axs[0,1].plot(x2, density(x2))
    axs[0,1].set_box_aspect(dim_arr[ts][0]/dim_arr[ts][1])
    axs[0,1].set_xlim(dimlist[ts][0][0],dimlist[ts][0][1])
    axs[0,1].axis('off')
    
    for i in range(2):
        for j in range(2):
            axs[i,j].get_xaxis().set_visible(False)
            axs[i,j].get_yaxis().set_visible(False)
    
    box_x_size=box_dim_arr[ts]/(2*multiplier)
    rect1 = plt.Rectangle(
        (0.25-box_x_size/2, 0), box_x_size, 1, fill=False, color="k", lw=1, 
        zorder=1000, transform=fig.transFigure, figure=fig
    )
    
    rect2 = plt.Rectangle(
        (0.25-box_x_size/2, 0), box_x_size, height_ratios[1]/sum(height_ratios), fill=False, color="k", lw=1, 
        zorder=1000, transform=fig.transFigure, figure=fig
    )
    rect3 = plt.Rectangle(
        (0.75-box_x_size/2, 0), box_x_size, 1, fill=False, color="k", lw=1, 
        zorder=1000, transform=fig.transFigure, figure=fig
    )
    
    rect4 = plt.Rectangle(
        (0.75-box_x_size/2, 0), box_x_size, height_ratios[1]/sum(height_ratios), fill=False, color="k", lw=1, 
        zorder=1000, transform=fig.transFigure, figure=fig
    )    
    fig.patches.extend([rect1,rect2,rect3,rect4])
    plt.subplots_adjust(left=0, right=1, bottom=0.03, top=1, wspace=0, hspace=0)
    
    plt.savefig(join('/Users/osmanfurkanyilmaz/Desktop/test_frame','ts{}_strain{}.png'.format(ts,str(round((0.5*ts)/model1.tsCount,2)).replace('.',''))))
    plt.close()
    
    #plt.show()

for ts,xyzValArr in enumerate(xyzVals):
    fig, axs = plt.subplots(2, 1,figsize=(width_size,heigh_size), gridspec_kw={'height_ratios': height_ratios, 'width_ratios': [1]})# [(1+(ts/25)*0.5)*(1/1.7),(1+(ts/25)*0.5)*(1/1.7)] })

    size=0.6*heigh_size*1e5/(model1.atomCount)
    density = stats.gaussian_kde(xyzValArr[0])
    
    axs[1].scatter(xyzValArr[0], xyzValArr[1],s=size,c=col, alpha=0.8)
    axs[1].set_aspect('equal', 'box')
    axs[1].axis('off')
    fig.tight_layout()
    
    n1, x1, _ = axs[0].hist(xyzValArr[0], bins=bins, lw=3, histtype=u'step')#, density=True) 
    #n2, x2, _ = axs[0,1].hist(xyzValArr[0], bins=bins, histtype=u'step', density=True) 
    axs[0].plot(x1, density(x1))
    axs[0].set_box_aspect(dim_arr[ts][0]/dim_arr[ts][1])
    axs[0].axis('off')
    #axs[0].plot(x2, density(x2))
    
    #axs[0,0].set_ylim(0,ylim_max)
    #axs[0,0].set_aspect('equal')
    
    for i in range(2):
        #for j in range(2):
        axs[i].get_xaxis().set_visible(False)
        axs[i].get_yaxis().set_visible(False)
    
    box_x_size=box_dim_arr[ts]/multiplier
    rect1 = plt.Rectangle(
        (0.5-box_x_size/2, 0), box_x_size, 1, fill=False, color="k", lw=1, 
        zorder=1000, transform=fig.transFigure, figure=fig
    )
    
    rect2 = plt.Rectangle(
        (0.5-box_x_size/2, 0), box_x_size, height_ratios[1]/sum(height_ratios), fill=False, color="k", lw=1, 
        zorder=1000, transform=fig.transFigure, figure=fig
    )
    
    fig.patches.extend([rect1,rect2])

    
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    plt.show()'''