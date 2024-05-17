import os
import glob
import h5py
import numpy as np
import concurrent.futures as futures
from tqdm import tqdm
import matplotlib.pyplot as plt

def getBins(file):
    try:
        with h5py.File(file, 'r') as data:
            atm = {k: np.array(data[f'/atlas/pce1/atmosphere_s/{k}']) for k in data['/atlas/pce1/atmosphere_s'].keys()}
            atm_bins = atm['atm_bins']
            atm_bins_mybackg = atm_bins 
            return calculate_SNR(np.array(atm_bins_mybackg))
    except Exception as e:
        print(e)

def calculate_SNR(dataframe):
    average_signal = np.array(dataframe).mean().mean()
    background_signal = average_signal**(1/2)
    SNR = (average_signal-background_signal)/background_signal
    return SNR, background_signal

def histogram_and_average(atl02_results):
    snr_averages = []
    background_averages = []
    for result in atl02_results:
        snr, background_signal = result
        snr_averages.append(snr)
        background_averages.append(background_signal)
    snr_averages = np.array(snr_averages)
    background_averages = np.array(background_averages)
    plt.plot(snr_averages)
    plt.title(snr_averages.mean())
    plt.savefig('snr_averages.png')
    plt.plot(background_averages)
    plt.title(background_averages.mean())
    plt.savefig('background_averages.png')

datadir2 = '/nfsscratch/Users/wndrsn/atl02'
datafiles2 = sorted(glob.glob(os.path.join(datadir2, '**/*.h5'), recursive=True))
with futures.ProcessPoolExecutor() as executor:
    atl02_futures = [executor.submit(getBins, file) for file in datafiles2]   
    atl02_results = [future.result() for future in tqdm(atl02_futures)] 
atl02_results = [atl02 for atl02 in atl02_results if atl02!= None]
histogram_and_average(atl02_results)
