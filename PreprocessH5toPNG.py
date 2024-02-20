import os
import glob
import h5py
import numpy as np
import matplotlib.pyplot as plt
import zipfile

def h5toPNGs():
  datadir2 = '/nfsscratch/Users/wndrsn/2019_atl02'
  save_path = '/nfsscratch/Users/wndrsn/saved_pngs'
  # file = os.path.join(datadir2,'ATL02_20190125212731_04340210_006_01.h5')
  datafiles2 = glob.glob(os.path.join(datadir2, "*.h5"))
  zip_path = '/Users/wndrsn'

  if not os.path.exists(save_path):
    os.makedirs(save_path)
    print(f"Created directory: {save_path}")

  for file in datafiles2:
    try:
      file_out = f"{os.path.splitext(os.path.basename(file))[0]}_vmax50.png"
      data = h5py.File(file, 'r')
      atm = {k: np.array(data[f'/atlas/pce1/atmosphere_s/{k}']) for k in data['/atlas/pce1/atmosphere_s'].keys()}
      atm_bins = atm['atm_bins']
      n_records = atm_bins.shape[0]
      data.close()

      
      atm_mean = atm_bins.mean(axis=1, keepdims=True)
      atm_bins_mybackg = atm_bins-atm_mean

      #reduce vmax to 25 to get more noise to show up
      plt.imshow(atm_bins_mybackg.T, aspect='auto', cmap='nipy_spectral', vmin=0, vmax=50)
      

      plt.savefig(os.path.join(save_path,file_out))
      print(f'Saved {file_out}')
    except Exception as e:
      print(e)  

  # Create a ZIP file containing the saved PNGs using glob
  zip_filename = 'saved_pngs.zip'
  with zipfile.ZipFile(zip_filename, 'w') as zipf:
      for file_path in glob.glob(os.path.join(save_path, "*.png")):
          zipf.write(file_path, os.path.relpath(file_path, save_path))

  print(f"Saved PNGs compressed to {zip_filename}") 


h5toPNGs()
