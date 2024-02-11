from Model import Model
from functions import printProgressBar , clean_filename , list_to_str, save_ss_graph

from os import listdir
from os.path import isdir, join
from multiprocessing import Pool
import sys
import tqdm
import matplotlib.pylab as plt

import time

def save_tsViews(model):
    save_dir='/Users/osmanfurkanyilmaz/Desktop/output_graphs_combined'
    #save_dir=None
    model.set_real_dim_pcd_xyz_lowMem()
    model.save_combined_graphs(save_dir=save_dir)
    #try:
    #    model.save_combined_graphs(save_dir=save_dir)
    #except:
    #    print(model.title, 'cannot saved.')
    plt.close()

fold='/Volumes/ofeye/05. Tez - 3 Boyutlu Hibrit TPMS Grafen Köpükler/04. Analysis Files/02. Tamamlanmış'
#fold='/Users/osmanfurkanyilmaz/Desktop/Test_Analysis'

subfolds = [join(fold,x) for x in list(listdir(fold)) if isdir(join(fold,x))]
subfolds = [x for x in subfolds if x.split('/')[-1].split('_')[4]=='30']

l=len(subfolds)
model_Arr=[Model(fol) for fol in subfolds]


if __name__ == '__main__':
    #for model in model_Arr:
    #    save_tsViews(model)
    pool=Pool(6)
    for _ in tqdm.tqdm(pool.imap_unordered(save_tsViews, model_Arr), total=len(model_Arr)):
        pass