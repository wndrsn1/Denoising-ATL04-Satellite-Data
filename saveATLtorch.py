import os
import glob
import h5py
from numpy import pi as pi
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import concurrent.futures as futures
import torch
from tqdm import tqdm
from pyorbital import astronomy 

atl02_dir = '/nfsscratch/Users/wndrsn/atl02'


def gps_to_datetime(gps_seconds):
    gps_epoch = datetime(2018, 1, 1)
    gps_time = gps_epoch + timedelta(seconds=gps_seconds)
    return gps_time

def read_in_atl02(file):
    try:
        atl02 = pd.DataFrame()
        with h5py.File(file, 'r') as data:
            atl02['time']  = pd.DataFrame(np.array(data['/gpsr/navigation/delta_time']))
            atl02['time'] = atl02['time'].apply(gps_to_datetime)
            atl02['lat']  = pd.DataFrame(np.array(data['/gpsr/navigation/latitude']))
            atl02['long']  = pd.DataFrame(np.array(data['/gpsr/navigation/longitude']))
            atl02['zenith'] =  90-astronomy.sun_zenith_angle(atl02['time'], atl02['long'], atl02['lat'])
        return atl02
    except Exception as e:
        print(e)

def getBins(file):
    with h5py.File(file, 'r') as data:
        atm = {k: np.array(data[f'/atlas/pce1/atmosphere_s/{k}']) for k in data['/atlas/pce1/atmosphere_s'].keys()}
        atm_bins = atm['atm_bins']
        n_records = atm_bins.shape[0]
        atm_mean = atm_bins.mean(axis=1, keepdims=True)
        atm_bins_mybackg = atm_bins-atm_mean
        return pd.DataFrame(atm_bins_mybackg)
    
def get_back(df):
    atm_mean = df.mean(axis=1, keepdims=True)
    return pd.DataFrame(atm_mean)

def save_dataframe_to_tensor_file(df, file_path):
    df = pd.DataFrame(df)
    # Convert DataFrame to PyTorch tensor
    tensor_data = torch.tensor(df.values)
    
    # Save tensor and column names to file
    torch.save(tensor_data, file_path)

def make_dfs(file, df):
    night_data = []
    i = 0
    is_night = None
    for index, row in df.iterrows():
        if row['zenith'] <= 0:
            # It's night
            if is_night is False or is_night is None:
                # If we were in day or this is the first row, start a new night DataFrame
                night_data.append([])
            night_data[-1].append(row)
            is_night = True
        else:
            # It's day
            if is_night is True:
                i += 1
                # If we were in night, start a new day DataFrame
                night_save_path = f'/nfsscratch/Users/wndrsn/atl02Torch/{os.path.basename(file).replace(".h5", "")}_{i}_night.pth'
                night_dataset = pd.DataFrame(night_data[-1])
                save_dataframe_to_tensor_file(night_dataset, night_save_path)
                
                noisy_save_path = f'/nfsscratch/Users/wndrsn/atl02Torch/{os.path.basename(file).replace(".h5", "")}_{i}_noisy.pth'
                noisy_bg = np.full_like(night_dataset,40) 
                noisy_dataset = night_dataset + noisy_bg
                noisy_dataset = np.random.poisson(np.maximum(noisy_dataset,0))
                save_dataframe_to_tensor_file(noisy_dataset,noisy_save_path)
                
                bg_dataset = noisy_dataset.mean(axis=1, keepdims=True)
                bg_save_path = f'/nfsscratch/Users/wndrsn/atl02Torch/{os.path.basename(file).replace(".h5", "")}_{i}_bg.pth'
                save_dataframe_to_tensor_file(bg_dataset, bg_save_path)
                
            is_night = False

    return night_data

def create_dataset(file):
    try:
        df1 = read_in_atl02(file)
        df2 = getBins(file)
        zenith_values = df1['zenith'].tolist()
        repeated_zenith_values = [val for val in zenith_values for _ in range(25)]
        df2['zenith'] = repeated_zenith_values
        make_dfs(file,df2)
        return 'none'
    except:
        return file
        
datadir2 = atl02_dir
datafiles2 = sorted(glob.glob(os.path.join(datadir2, '**/*.h5'), recursive=True))
with futures.ProcessPoolExecutor() as executor:
    atl02_futures = [executor.submit(create_dataset, file) for file in datafiles2]   
    atl02_results = [future.result() for future in tqdm(atl02_futures)]  
    
fails = pd.DataFrame()
fails['files'] = pd.DataFrame(atl02_results)
fails.to_csv('fails.csv')
