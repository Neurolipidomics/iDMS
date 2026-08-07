# -*- coding: utf-8 -*-
"""
Created on Fri Aug  1 09:48:59 2025

@author: thaon
"""
# This processing script only works for .mzML files converted from .wiff files by MSConvert (ProteoWizard).
# This script will process DMS datafiles for each lipid located in folders specified by users.

# Import basic system parameters and functions
import sys
import subprocess
import pkg_resources

# Several packages needed to be installed. We first will check to see if your environment has already had these packages installed.
required = {'pandas', 'numpy', 'jcamp', 'pyopenms'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout = subprocess.DEVNULL)

# Import other packages
import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
import numpy as np
import pandas as pd
import pyopenms as oms

currentpath = os.getcwd()
os.chdir(currentpath)
###############################################################################################
# Prompt Users to enter CoV range
def input_CoV():
    root = tk.Tk()
    root.withdraw()
    
    CoV_prompt = simpledialog.askstring("Input", "Start CoV, Stop CoV, Step CoV\t\t\t")
    
    if CoV_prompt:
        params = [item.strip() for item in CoV_prompt.split(',')]
        return params
    else:
        return[]

CoV_params = [float(s) for s in input_CoV()]
print(CoV_params)

# Compute full range of CoV and count
StartCoV = CoV_params[0]
StopCoV = CoV_params[1]
StepCoV = CoV_params[2]

CoV_range = np.arange(StartCoV, StopCoV+StepCoV, StepCoV)
np.around(CoV_range, decimals=1)


# Promp Users to navigate to folder where DMS files are stored

root = tk.Tk()
InputDir = filedialog.askdirectory(parent= root,
                                    initialdir="/",
                                    title = "Browse to the folder where DMS files are stored")
if len(InputDir) > 0:
    file_Dir = InputDir

root.withdraw() #use to hide tkinter window ; this line is important to prevent tkinter from hanging
root.update()

# Function mzMLFileCompile to extract intensity from each SV

def FileCompiler (file_Dir):
    df_total = pd.DataFrame()
    for dirnames in os.listdir(file_Dir):
        subfolderpath = os.path.join(file_Dir, dirnames)
        #lipidInfo = input_lipidInfo(dirnames)
        
        lipidInfo_prompt = simpledialog.askstring(dirnames, "Lipid Chain Length, # of Unsaturation Unit, Replicate Number\t\t\t\t\t",
                                                  parent = root)
        root.withdraw()
        root.update()
        if lipidInfo_prompt:
            lipidInfo = [item.strip() for item in lipidInfo_prompt.split(',')]
            print(lipidInfo)
            chainLength = lipidInfo[0]
            unsatUnit = lipidInfo[1]
            repNum = lipidInfo[2]
                
        for filename in os.listdir(subfolderpath):
            if filename.endswith(".mzML") and "SV" in filename:
                filepath = os.path.join(subfolderpath, filename)        
                SV_list = []
                df_temp  = pd.DataFrame()
                
                exp = oms.MSExperiment()
                oms.MzMLFile().load(filepath, exp)

                chromatogram_data = exp.getChromatogram(0).get_peaks()
                scanNum = chromatogram_data[0]
                Intensity = chromatogram_data[1]
                
                #the size of chromatogram_data has to equal the range of CoV
                if len(scanNum) == len(CoV_range):
                    print("The number of scans in your datafile matches the CoV range. Proceed.")
                    for i in range(len(CoV_range)):        
                        SV_split1, SV_split2 = filename.split("_",1)
                        SV_list.append(float(SV_split2.split("_",1)[0]))
                else:
                    print("The number of scans in your datafile DOES NOT match the CoV range. Please recheck your data and input information for CoV.")
                    sys.exit()
                
                df_temp['COV'] = CoV_range
                df_temp['Intensity'] = Intensity
                df_temp['SV'] = SV_list
                df_temp['chainLength'] = chainLength
                df_temp['unsaturationUnit'] = unsatUnit
                df_temp['replicateNumber'] = repNum
                df_total = pd.concat([df_total, df_temp])
    return df_total

# Execute Compiling Function
df_new = pd.DataFrame()
df_new = pd.concat([FileCompiler(file_Dir), df_new])

# Complete the output dataframe
# Prompt Users
root = tk.Tk()

backboneInfo_prompt = simpledialog.askstring("Input", "Isomer, Sphingoid Backbone")
backboneInfo = [item.strip() for item in backboneInfo_prompt.split(',')]
isomer = backboneInfo[0]
sphingoidBackbone = backboneInfo[1]
print(backboneInfo)

df_new['isomer'] = isomer
df_new['sphingoidBackbone'] = sphingoidBackbone
df_new['lipidSpecies'] = df_new['chainLength'].astype(str) + ':' + df_new['unsaturationUnit'].astype(str)

root.withdraw()
root.update()    

# Saving file
save_path = filedialog.asksaveasfilename(
    parent= root,
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")])

df_new.to_csv(save_path, index=False)
print(f"DataFrame saved to: {save_path}")

root.withdraw()
root.update()






