import numpy as np
from scipy.ndimage.filters import gaussian_filter
import string
import unicodedata
import matplotlib.pyplot as plt
from os.path import isdir, join
from os import mkdir


def create_datadict(keyList):
    return {x:[] for x in keyList}


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
        flat_list.extend(row)
    return flat_list

def heatmapPlot(x, y, s, bins=1000):
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=s)

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return heatmap.T, extent

def clean_filename(filename, whitelist="-_() %s%s" % (string.ascii_letters, string.digits),char_limit=255, replace=' '):
    # replace spaces
    for r in replace:
        filename = filename.replace(r,'_')
    
    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    
    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename)>char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]    

def list_to_str(arr):
    ret_str=''
    for i,string in enumerate(arr):
        if i==0:
            string="%03d" % (string,)
        ret_str+=str(string)+'_'
    return ret_str[0:-1]

def save_ss_graph(model,model_Arr,kZeroArr,stress_name, save_dir=None):
    
    if save_dir==None:
        save_dir=model.folder
    else:
        save_dir=join(save_dir,model.title)
        if not isdir(save_dir):
            mkdir(save_dir)
    
    plt.style.use("_mpl-gallery")
    plt.figure(figsize=(10,5))

    geom1 = [x for x in kZeroArr if (model.geom1==x.geom1) & (model.length==x.length) & (x.kValue == 0)][0]
    geom2 = [x for x in kZeroArr if (model.geom2==x.geom1) & (model.length==x.length) & (x.kValue == 0)][0]

    
    if stress_name=='Stress':
        plt.plot(model.strainList, model.stressList, label = "Hybrid") 
        plt.plot(geom1.strainList, geom1.stressList, label = "Type-1") 
        plt.plot(geom2.strainList, geom2.stressList, label = "Type-2")
        plt.ylabel('Stress [GPa]')
    elif stress_name=='Normalized Stress':
        plt.plot(model.strainList, model.normStressList, label = "Hybrid") 
        plt.plot(geom1.strainList, geom1.normStressList, label = "Type-1") 
        plt.plot(geom2.strainList, geom2.normStressList, label = "Type-2")
        plt.ylabel('Normalized Stress [GPa cm^3/mg]')

    plt.legend()
    plt.xlim(0,)
    plt.ylim(0,)
    
    plt.xlabel("Strain")
    #plt.ylabel('{} [GPa]'.format(stress_name))
    
    plt.title('PK: {}; Type-1:{}; Type-2:{}; Length:{}; k Value:{}; Hyb-Perc:{}'.format(model.privateKey,model.geom1,model.geom2,model.length,model.kValue,model.hybPerc))
    
    if not isdir(join(save_dir,'ss_Curves')):
        mkdir(join(save_dir,'ss_Curves'))
    
    plt.savefig(join(save_dir,'ss_Curves','{}.png'.format(stress_name)),bbox_inches='tight', dpi=150)
    plt.close()