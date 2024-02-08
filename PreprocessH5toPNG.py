import os
import glob
import h5py
import tqdm
import datetime as DT
import numpy as np
import matplotlib.pyplot as plt

datadir2 = '/nfsscratch/Users/wndrsn/2019_atl02'
datadir4 = '/nfsscratch/Users/wndrsn/2019_atl04'
datafiles2 = sorted(glob.glob(os.path.join(datadir2, "*.h5")))
datafiles4 = sorted(glob.glob(os.path.join(datadir4, "*.h5")))
for i in range(len(datafiles2)):
  file_out = f"{os.path.splitext(os.path.basename(datafiles2[i]))[0]}.png"
  print("Loading: ", datafiles2[i])
  data = h5py.File(datafiles2[i], 'r')
  atm = {k: np.array(data[f'/atlas/pce1/atmosphere_s/{k}']) for k in data['/atlas/pce1/atmosphere_s'].keys()}
  atm_bins = atm['atm_bins']
  n_records = atm_bins.shape[0]
  data.close()
  # def get_atl04():
  print("Loading: ", datafiles4[i])
  data = h5py.File(datafiles4[i], 'r')
  nrb = np.array(data['profile_1/nrb_profile'])
  backg_select = np.array(data['ancillary_data/atmosphere/backg_select'])
  backg = np.array(data[f'profile_1/backg_method{backg_select[0]}'])
  range_to_top = np.array(data['profile_1/range_to_top'])
  z = np.array(data['profile_1/ds_va_bin_h'])
  nrb_top_bin = np.array(data['profile_1/nrb_top_bin'])
  nrb_bot_bin = np.array(data['profile_1/nrb_bot_bin'])
  mol_scatter = np.array(data['meteorology_molec_bkscat/mol_backs_folded'])
  atm_bins_back = atm_bins-backg[:n_records].reshape(-1, 1)
  atm_bins_back_mask = np.ma.array(atm_bins_back, mask=atm_bins_back<0)
  nrb_mask = np.ma.array(nrb, mask=nrb>1e38)
  adj_z = z[0] - z
  adj_z = adj_z.reshape(1, -1)
  range_to_top = range_to_top.reshape(-1, 1)
  r = range_to_top + adj_z
  r2 = (r/1000)**2
  #plt.imshow(atm_bins.T, aspect='auto', cmap='nipy_spectral', vmin=0, vmax=2000)
  plt.imshow(atm_bins_back.T, aspect='auto', cmap='nipy_spectral', vmin=0, vmax=2000)
  plt.colorbar()
  plt.savefig(f'/Users/wndrsn/{file_out}')
  print(f'Saved {file_out}')
  break
  
