import pandas as pd
import numpy as np
from os import chdir,getcwd,listdir,makedirs
from os.path import dirname,abspath,join,isdir,isfile
from math import sin,cos,pi
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

import time
from itertools import product
import shutil
import multiprocessing
import scipy.spatial as spatial
from datetime import datetime
import heapq

def now():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def get_work_dir():
    chdir(dirname(abspath(__file__)))
    return getcwd()

def all_coor_files():
    return [dir for dir in listdir(join(get_work_dir(),'base_coords')) if str(dir).split('_')[0]=='base']

def list_to_str(arr,sep):
    return str(sep).join([str(x) for x in arr])

# Geometry Function
def gyroid(x,y,z,lengt):
    #return sin(2*pi*x/lengt)*cos(2*pi*y/lengt)+sin(2*pi*y/lengt)*cos(2*pi*z/lengt)+sin(2*pi*z/lengt)*cos(2*pi*x/lengt)
    #return sin(2*pi*x/lengt)*sin(2*pi*y/lengt)*sin(2*pi*z/lengt)+sin(2*pi*x/lengt)*cos(2*pi*y/lengt)*cos(2*pi*z/lengt)+cos(2*pi*x/lengt)*sin(2*pi*y/lengt)*cos(2*pi*z/lengt)+cos(2*pi*x/lengt)*cos(2*pi*y/lengt)*sin(2*pi*z/lengt)
    return cos(2*pi*x/lengt)+cos(2*pi*y/lengt)+cos(2*pi*z/lengt)


def range_list(start,end,step):
    if (end-start)/step==int((end-start)/step):
        return [x*step+start for x in range(1+int((end-start)/step))]
    else:
        print('Error : The step value does not divide the range exactly.')

def text_to_df(filename):
    full_arr=[]
    with open(join(get_work_dir(),'base_coords/{}'.format(filename))) as mytxt:
        for line in mytxt:
            newline = line.replace("\ufeff",'').replace('','')
            newline = newline.rstrip("\n").split(' ')
            full_arr.append([float(x) for x in newline])
    return pd.DataFrame(full_arr)

def duplicate_multi(df,ntime,boxlen):
    fin_boxlen=ntime*boxlen
    movelen=fin_boxlen-boxlen

    move_steps=range_list(-0.5*movelen,0.5*movelen,boxlen)

    new_df=pd.DataFrame()
    for x in move_steps:
        for y in move_steps:
            for z in move_steps:
                temp_df=df+[x,y,z]
                new_df = pd.concat([new_df, temp_df], ignore_index=True, sort=False)
    return new_df

def opt_df(df,arr):
    return df+arr

def duplicate_multi_opti(df,ntime,boxlen):
    fin_boxlen=ntime*boxlen
    movelen=fin_boxlen-boxlen

    move_steps=range_list(-0.5*movelen,0.5*movelen,boxlen)

    df_arr=list(map(opt_df,[df for x in range(len(move_steps)**3)],product(move_steps,move_steps,move_steps)))
    new_df = pd.concat(df_arr, ignore_index=True, sort=False)
    return new_df

def filter_maingeom(point_df,mainlen,maincnt,isoval):
    if isoval==0:
        result = point_df
    else:
        point_df['cond']=list(map(gyroid, point_df[0], point_df[1], point_df[2], [mainlen/maincnt for x in range(len(point_df))]))
        result = point_df[(point_df['cond']<isoval) & (point_df['cond']>-1*isoval)].drop(['cond'],axis=1)
    
    return result

def inputstr(df,maxCoordinate):
    input_file="#TPMS  structure\n"+str(len(df))+" atoms\n1 atom types\n\n"+str(-1*maxCoordinate)+" "+str(maxCoordinate)+" xlo xhi\n"+str(-1*maxCoordinate)+" "+str(maxCoordinate)+" ylo yhi\n"+str(-1*maxCoordinate)+" "+str(maxCoordinate)+" zlo zhi\n\nMasses\n\n1 12.0\nAtoms\n\n"

    df_final=pd.DataFrame()
    df_final['number']=[x+1 for x in range(len(df))]
    df_final['atom_number']=[1 for x in range(len(df))]
    df_final['0']=list(df[0])
    df_final['1']=list(df[1])
    df_final['2']=list(df[2])

    finalPntsStr=df_final.to_string(header=None,index=False)

    return input_file+finalPntsStr

def text_to_in_export(filename):
    text_arr=filename.split('_')
    maxCoordinate=int(text_arr[-1])*int(text_arr[-2])
    with open(join(get_work_dir(),'input_files',filename), "w") as f:
        f.write(inputstr(text_to_df(filename),maxCoordinate))

def export_input(input_dir,multicnt,maincnt,isoval,scatterplot=False,overwrite=False):
    export_dir=str(input_dir+'_'+str(multicnt)+'_'+str(maincnt)+'_'+str(isoval).replace('.','')+'.in')

    if export_dir in listdir(join(get_work_dir(),'input_files')) and not overwrite and not scatterplot:
        print(f'{export_dir} already exist.')
    else:
        boxlen=int(input_dir.split('_')[-1])*int(input_dir.split('_')[-2])
        df=duplicate_multi_opti(text_to_df(input_dir),multicnt,boxlen)
        df=filter_maingeom(df,boxlen*multicnt,maincnt,isoval)

        if export_dir in listdir(join(get_work_dir(),'input_files')) and not overwrite:
            pass
        else:
            duplicated_rows=list(df.duplicated()).count(True)
            if duplicated_rows==0:
                pass
            else:
                print(f'{duplicated_rows} duplicated rows find!')

            with open(join(get_work_dir(),'input_files',export_dir), "w") as f:
                f.write(inputstr(df,boxlen*multicnt/2))

    if scatterplot:
        df = df.rename(columns={0: 'x', 1: 'y', 2: 'z'})
        print(len(df))
        
        neigh_arr=find_neigh(df,1.7)
        
        #fig=plt.figure()
        #ax=fig.add_subplot(projection='3d')

        #ax.scatter(xs=[arr[0] for arr in neigh_arr],ys=[arr[1] for arr in neigh_arr],zs=[arr[2] for arr in neigh_arr])
        #plt.show()

        fig = px.scatter_3d(df, x='x', y='y', z='z', opacity=1)
        #print(len(neigh_arr))
        #for neigh in neigh_arr[0:500]:
        #    fig.add_trace(go.Scatter3d(x=neigh[0],y=neigh[1],z=neigh[2],mode='lines',showlegend=False ,marker=dict(color='black')))
        fig.update_traces(marker=dict(size=1))
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        fig.show()
    
    return export_dir

def find_neigh(df,cutoff):
    df_array=df.to_numpy()
    point_tree = spatial.cKDTree(df_array)

    line_arr=[]
    for point in df_array:
        connect_arr=df_array[point_tree.query_ball_point(point, r=cutoff)]

        for line in connect_arr:
            line_arr.append([[point[0],line[0]],[point[1],line[1]],[point[2],line[2]]])

    return line_arr


def multi_run(dir_arr,multicnt_arr,maincnt_arr,isoval_arr,overwrite=False,productlist=True):
    if productlist:
        full_product=list(product(dir_arr,multicnt_arr,maincnt_arr,isoval_arr))
    elif not productlist:
        full_product=[(d,m,ma,i) for d,m,ma,i in zip(dir_arr,multicnt_arr,maincnt_arr,isoval_arr)]
        if max([len(dir_arr),len(multicnt_arr),len(maincnt_arr),len(isoval_arr)])!=min([len(dir_arr),len(multicnt_arr),len(maincnt_arr),len(isoval_arr)]):
            print(f'Warning! All spec arrays not in same length. Only these geometries are created: {full_product}')
    else:
        print('"product" value must be True or False.')

    print(full_product)
    startTime_g = time.time()
    export_dir_arr=[]
    for full_arr in full_product:
        export_dir=export_input(full_arr[0],full_arr[1],full_arr[2],full_arr[3],False,overwrite=overwrite)
        export_dir_arr.append(export_dir)
    executionTime = (time.time() - startTime_g)
    print(f'Done! General execution time in seconds: {str(executionTime)}')
    return export_dir_arr

def create_input(fin_dir_arr,export_dir_arr):
    inMulti=open(join(get_work_dir(),'data','in.Multi')).read()

    inMultiRep=inMulti.replace('klasorlerBuraya',list_to_str(fin_dir_arr,' '))
    inMultiRep=inMultiRep.replace('datafilesBuraya ',list_to_str(export_dir_arr,' '))

    return inMultiRep

def create_multi_in(size_arr,multicnt_arr,maincnt_arr,isoval_arr,overwrite=False,productlist=True):
    dir_arr=[f'base_coor_{str(size[0])}_{str(size[1])}' for size in size_arr]
    export_dir_arr=multi_run(dir_arr,multicnt_arr,maincnt_arr,isoval_arr,overwrite=False,productlist=productlist)
    isoval_arr_edit=[str(iso).replace('.','') for iso in isoval_arr]

    size_arr_txt=[list_to_str(size,'x') for size in size_arr]

    folder_name=list_to_str([list_to_str(arr,'_') for arr in [size_arr_txt,multicnt_arr,maincnt_arr,isoval_arr_edit]],'-')
    forder_dir=join(get_work_dir(),'multi_in_folders',folder_name)

    if isdir(forder_dir) and overwrite:
        shutil.rmtree(forder_dir)
    elif isdir(forder_dir) and not overwrite:
        print('This combination already exist.')
        return None

    makedirs(forder_dir)

    airebo_dir=join(get_work_dir(),'data','CH_Mod.airebo')
    fin_dir_arr=[]
    for fol_dir in export_dir_arr:
        fin_dir_name=str(fol_dir).split('.')[0]
        fin_dir=join(forder_dir,fin_dir_name)
        fin_dir_arr.append(fin_dir_name)
        makedirs(fin_dir)
        shutil.copyfile(airebo_dir, join(fin_dir,'CH_Mod.airebo'))
        shutil.copyfile(join(get_work_dir(),'input_files',fol_dir), join(fin_dir,fol_dir))

    open(join(forder_dir,'in.Multi'),'w').write(create_input(fin_dir_arr,export_dir_arr))

    return forder_dir

def uhem_input(chunk_size,size_arr,multicnt_arr,maincnt_arr,isoval_arr):
    #cost_size_arr=[(float(s[0])**2)*float(s[1])*float(m)*float(i) for s,m,i in zip(size_arr,multicnt_arr,isoval_arr)]
    #print(cost_size_arr)

    uhem_folder=join(get_work_dir(),'uhem_in_folders',now())
    makedirs(uhem_folder)
    sh_dir=join(get_work_dir(),'data','lammps.sh')
    command_file=open(join(uhem_folder,'command.txt'),'w')
    for index,(sizes,mltcnt,mncnt,isoval) in enumerate(zip(size_arr,multicnt_arr,maincnt_arr,isoval_arr)):
        folder_dir=create_multi_in([sizes],[mltcnt],[mncnt],[isoval],overwrite=True,productlist=False)
        fin_fol_dir=join(uhem_folder,str(index+1))
        shutil.copytree(folder_dir, fin_fol_dir)
        shutil.copyfile(sh_dir, join(fin_fol_dir,'lammps.sh'))
        if index+1<len(size_arr):
            command_file.write(f'sbatch ./{index+1}/lammps.sh && ')
        else:
            command_file.write(f'sbatch ./{index+1}/lammps.sh')



'''
if __name__ == "__main__":
    startTime = time.time()
    full_product=list(product(all_coor_files(),[10],[1],[0.3,0.5,0.7]))

    manager = multiprocessing.Manager()
    processes = []

    for i in full_product:
        p = multiprocessing.Process(target=export_input, args=i)
        processes.append(p)
        p.start()

    for process in processes:
        process.join()
    
    executionTime = (time.time() - startTime)
    print(f'Execution time in seconds: {str(executionTime)}')
'''

if __name__ == "__main__":
    #print(all_coor_files())
    #export_input('base_coor_40_1',10,1,0.15,True,overwrite=False)
    #multi_run(all_coor_files(),[5],[1],[0.3,0.5])
    ez_arr=[[100,5,0]]

    size_arr=[[x[0],1] for x in ez_arr]
    multicnt_arr=[x[1] for x in ez_arr]
    maincnt_arr=[1 for x in ez_arr]
    isoval_arr=[x[2] for x in ez_arr]
    
    uhem_input(1,size_arr,multicnt_arr,maincnt_arr,isoval_arr)
    #create_multi_in(size_arr,multicnt_arr,maincnt_arr,isoval_arr,overwrite=True,productlist=False)
    #text_to_in_export('base_coor_80_1')