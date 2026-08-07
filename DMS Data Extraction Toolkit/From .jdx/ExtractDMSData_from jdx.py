# -*- coding: utf-8 -*-
"""
Created on Thu Jul 31 12:20:20 2025

@author: thaon
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 15:05:36 2025

@author: thaon
"""
# This processing script only works for .jdx files converted from .wiff files by Analyst software.
# This script will process DMS datafiles for each lipid located in folders specified by users.

# Import basic system parameters and functions
import sys
import subprocess
import pkg_resources

# Several packages needed to be installed. We first will check to see if your environment has already had these packages installed.
required = {'pandas', 'numpy', 'jcamp'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout = subprocess.DEVNULL)

# Import other packages
import os
import re
import jcamp
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
import numpy as np
import pandas as pd

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


# Function FileCompile to extract intensity from each SV

def FileCompiler (file_Dir):
    df_total = pd.DataFrame()
    for dirnames in os.listdir(file_Dir):
        subfolderpath = os.path.join(file_Dir, dirnames)
        
        lipidInfo_prompt = simpledialog.askstring(dirnames, "Lipid Chain Length, # of Unsaturation Unit, Replicate Number\t\t\t\t\t",
                                                  parent = root)
        if lipidInfo_prompt:
            lipidInfo = [item.strip() for item in lipidInfo_prompt.split(',')]
            print(lipidInfo)  
            chainLength = lipidInfo[0]
            unsatUnit = lipidInfo[1]
            repNum = lipidInfo[2]           
        
        for filename in os.listdir(subfolderpath):
            if filename.endswith(".jdx") and "SV" in filename:
                filepath = os.path.join(subfolderpath, filename)        
                #df1 = pd.read_csv(filepath, sep='##')
                CoV_list = []
                CoV = StartCoV
                SV_list = []
                basepeakIntensity = []
                df_temp  = pd.DataFrame()
                        
                with open(filepath) as f:
                    # Check point
                    # The range of CoV must match the number of scans in each DMS file.
                    scanCounter = 0
                    for line in f:
                        if "SCAN NUMBER" in line:
                            scanCounter += 1
                        
                        if "BASE PEAK INTENSITY" in line:
                            CoV_list.append(CoV)
                            CoV = np.around(CoV + StepCoV, decimals = 1)
                            basepeakIntensity.append(float(line.rsplit('=')[-1][0:-1]))
                            SV_split1, SV_split2 = filename.split("_",1)
                            SV_list.append(float(SV_split2.split("_",1)[0]))
                        
                    if scanCounter == len(CoV_range):
                        print("The number of scans in your datafile matches the CoV range. Proceed")
                    else:
                        print("The number of scans in your datafile DOES NOT match the CoV range. Please recheck your data and input information for CoV.")
                        sys.exit()
                
                df_temp['COV'] = CoV_list
                df_temp['Intensity'] = basepeakIntensity
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


lipidInfo_prompt = simpledialog.askstring("Input", "Isomer, Sphingoid Backbone")
lipidInfo = [item.strip() for item in lipidInfo_prompt.split(',')]
isomer = lipidInfo[0]
sphingoidBackbone = lipidInfo[1]
print(lipidInfo)

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

 

   
    
        
        
        
        
        
                
                
           
    
    