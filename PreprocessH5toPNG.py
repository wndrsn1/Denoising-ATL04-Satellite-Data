import os
import glob
import h5py
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import zipfile
datadir2 = '/nfsscratch/Users/wndrsn/2019_atl02'
datadir4 = '/nfsscratch/Users/wndrsn/2019_atl04'
save_path = '/nfsscratch/Users/wndrsn/saved_pngs'
datafiles2 = sorted(glob.glob(os.path.join(datadir2, "*.h5")))
datafiles4 = sorted(glob.glob(os.path.join(datadir4, "*.h5")))
if not os.path.exists(save_path):
  os.makedirs(save_path)
  print(f"Created directory: {save_path}")
zip_path = '/Users/wndrsn'
for i in tqdm(range(4)):
  file_out = f"{os.path.splitext(os.path.basename(datafiles2[i]))[0]}.png"
  
  data = h5py.File(datafiles2[i], 'r')
  atm = {k: np.array(data[f'/atlas/pce1/atmosphere_s/{k}']) for k in data['/atlas/pce1/atmosphere_s'].keys()}
  atm_bins = atm['atm_bins']
  n_records = atm_bins.shape[0]
  data.close()
  # def get_atl04():
  
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
  plt.savefig(os.path.join(save_path,file_out))
  print(f'Saved {file_out}')


# Create a ZIP file containing the saved PNGs using glob
zip_filename = 'saved_pngs.zip'
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for file_path in glob.glob(os.path.join(save_path, "*.png")):
        zipf.write(file_path, os.path.relpath(file_path, save_path))

print(f"Saved PNGs compressed to {zip_filename}")
