# I AM HUMAN
# I AM ROBOT
# I AM GAIA
import xarray as xr
import numpy as np
import pandas as pd
import json 
import os
from esmvaltool.diag_scripts.shared import run_diagnostic, get_cfg, group_metadata
import glob
import netCDF4
import random

def main(config):
    """Run the diagnostic."""
    cfg=get_cfg(os.path.join(config["run_dir"],"settings.yml"))
    #print(cfg)
    meta_dataset = group_metadata(config["input_data"].values(), "dataset")
    meta = group_metadata(config["input_data"].values(), "alias")
    rd_list_models = []
    models = []
    regressors_members = {}
    for dataset, dataset_list in meta_dataset.items(): ####DATASET es el modelo
        if dataset != "GISS-E2-1-G":
            print(f"Preparing data for regression for {dataset}\n")
            models.append(dataset)
            rd_list_members = []
            for alias, alias_list in meta.items(): ###ALIAS son los miembros del ensemble para el modelo DATASET
                ts_dict = {m["variable_group"]: xr.open_dataset(m["filename"])[m["short_name"]].sel(time=slice('2070','2099')).mean(dim='time') - xr.open_dataset(m["filename"])[m["short_name"]].sel(time=slice('1950','1979')).mean(dim='time') for m in alias_list if (m["dataset"] == dataset)}
                if 'gw' in ts_dict.keys():
                    rd_list_members.append(ts_dict)
                else:
                    a = 'nada'
        else:
            continue
                    
        #Across model regrssion - create data array
        regressor_names = rd_list_members[0].keys()
        regressors_members[dataset] = {}
        for rd in regressor_names:
            list_values = [rd_list_members[m][rd].values for m,model in enumerate(rd_list_members)]
            regressors_members[dataset][rd] = np.array(list_values)

    
    #Across model regrssion - create data array 
    regressors = {}
    for rd in regressor_names:
        print('model',dataset)
        print('rd',rd)
        list_values = [np.mean(regressors_members[dataset][rd]) for dataset, dataset_list in meta_dataset.items() if dataset != 'GISS-E2-1-G']
        print(len(list_values))
        regressors[rd] = np.array(list_values)
    
    regressors['model'] = models
    
    #Find index limits
    spv_gw = regressors['spv'] / regressors['gw']
    regressors['spv_gw'] = spv_gw
    mean = np.mean(spv_gw)
    std = np.std(spv_gw)
    low_limit = mean - std*1.28
    high_limit = mean + std*1.28
    index_limits = {'low_spv':low_limit,'mean_spv':mean,'high_spv':high_limit}

    #Create directories to store results
    os.chdir(config["work_dir"])
    os.getcwd()
    os.makedirs("remote_drivers",exist_ok=True)
    os.chdir(config["plot_dir"])
    os.getcwd()
    os.makedirs("remote_drivers",exist_ok=True)
    df = pd.DataFrame(regressors)
    df.to_csv(config["work_dir"]+'/remote_drivers_stratospheric_polar_vortex_global_warming.csv')
    df = pd.DataFrame(index_limits,index=[0])
    df.to_csv(config["work_dir"]+'/remote_drivers_stratospheric_polar_vortex_global_warming_bounds.csv')

if __name__ == "__main__":
    with run_diagnostic() as config:
        main(config)
                              
