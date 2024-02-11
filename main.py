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
    save_dir=''
    #save_dir=None
    model.set_real_dim_pcd_xyz_lowMem()
    
    try:
        model.save_combined_graphs(save_dir=save_dir)
    except:
        print(model.title, 'cannot saved.')
    plt.close()

fold=''
subfolds = [join(fold,x) for x in list(listdir(fold)) if isdir(join(fold,x))]
model_Arr=[Model(fol) for fol in subfolds]

if __name__ == '__main__':
    pool=Pool(6)
    for _ in tqdm.tqdm(pool.imap_unordered(save_tsViews, model_Arr), total=len(model_Arr)):
        pass
