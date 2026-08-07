#!/usr/bin/env python
# coding: utf-8

# # iDMS Module 1 - Parametric Modelling (Extracting Gaussian mu and sigma from preprocessed input data)

# *Updated on 2026-08-06*
#
# Submitted with iDMS manuscript.
#
# Tested on Windows 10 and 11, 64-bit operating system, macOS 14+ on both Apple silicon and Intel chips.
#
# This module is designed to run in a virtual environment which has had all dependencies and libraries installed from the provided requirements.txt file. Without having done this, this module will not be able to proceed.
#
# This Module is divided into five steps: 1) obtain the empirical data, 2) validate the empirical data, ensuring input has all necessary annotations and is composed of pairs of stereoisomers, 3) plot the measured data, normalize the data and create ionogram plots of all stereoisomers, 4) extract the Gaussian parameters of mu and sigma from the normalized data and plot the normalized ionograms, 5) find the intersection point of the stereoisomer ionograms.
#
# Users will be asked to navigate to the directory where their input data files are stored. Input data files must contain necessary information associated with the glycosphingolipid stereoisomers. The information will be extracted by iDMS Module 1 and formatted as training datasets for iDMS Module 2 (the iDMS neural network).
# Output csv files and plots will be stored in this same folder.
#
# The output files are: **CombinedAnalysis.csv, meanAllsigma.csv, Intersected gauss.csv, extractGalMaxCov.csv, extractGlcMaxCov.csv, norm_Gal.csv, norm_Glc.csv, norm_GalParameters.csv, norm_GlcParameters.csv, isomerName.csv, python_version.txt** .
#
# The output plots are stored in the folders: **ExtractIonograms, NormIonograms, Gal_GaussianPlots, Glc_GaussianPlots, GaussianIntersectPlots found in the folder plots** .
#

# In[ ]:
# ## IMPORT LIBRARIES AND PACKAGES REQUIRED FOR IDMS NOTEBOOK

# Import basic system parameters and functions
import sys
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from numpy import exp
from numpy import asarray as ar
import shutil
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import time
from tqdm.auto import tqdm
from lmfit import Model
import warnings

# Set global seed
np.random.seed(42)

# Create function to send messages to user:
def msg_to_users(func, *args, **kwargs):
    root = tk.Tk()
    root.lift()
    root.wm_attributes("-topmost", 1)
    root.withdraw()
    result = []
    def msg_to_users():
        result.append(func(*args,**kwargs))
        root.destroy()
    root.after_idle(msg_to_users)
    root.mainloop()
    root.quit()
    return result.pop()

# In[ ]:

# ## STEP 1a. Obtain empirical data and create directory

# In[ ]:

# Browse to file location
msg_to_users(messagebox.showinfo,"Message to user.", "In the next window, please select folder directory where training datasets are in.")

InputDir =  msg_to_users(filedialog.askdirectory,
                                    initialdir="/",
                                    title = "Browse to where files are stored")
if len(InputDir) > 0:
    print ("You chose %s" % InputDir)
else:
    print ("Dear User, you did not choose a folder. I will stop now. iDMS is exiting")
    exit()

# Select the files for each isomer.
## Files are read and stored as DataFrame.
msg_to_users(messagebox.showinfo,"Message to user.", "In the next window, please select training data for the first isomer.")

InputFile1 = msg_to_users(filedialog.askopenfile,
                                   mode = 'rb',
                                   title = "Upload training data for the first isomers.")
if InputFile1 != None:
    isomer1 = pd.read_csv(InputFile1, sep=',', header=0, usecols=[
            'COV', 'Intensity', 'SV', 'chainLength', 'unsaturationUnit', 'isomer', 'sphingoidBackbone', 'lipidSpecies'
        ])

msg_to_users(messagebox.showinfo,"Message to user.", "In the next window, please select training data for the second isomer.")

InputFile2 = msg_to_users(filedialog.askopenfile,
                                   mode = 'rb',
                                   title = "Upload training data for the second isomers.")
if InputFile2 != None:
    isomer2 = pd.read_csv(InputFile2, sep=',', header=0, usecols=[
            'COV', 'Intensity', 'SV', 'chainLength', 'unsaturationUnit', 'isomer', 'sphingoidBackbone', 'lipidSpecies'
        ])


# ## STEP 1b. Prompt users for location to save all files.
msg_to_users(messagebox.showinfo,"Message to user.", "In the next window, please select folder directory to save all outputs.")

folder_path = msg_to_users(filedialog.askdirectory, title = "Please select folder directory to save all outputs.")

if folder_path:
    print(f"The folder where all outputs are saved is: {folder_path} ")
else:
    print("No folder selected.")

root = tk.Tk()
root.destroy()

currentpath = folder_path
os.chdir(currentpath)

# ## STEP 1c. Setting variables for data.
isomerName = {"isomer1": (str(isomer1['isomer'].unique()).replace("['","").replace("']","")),
              "isomer2" : (str(isomer2['isomer'].unique()).replace("['","").replace("']",""))}

isomer1_name = isomerName['isomer1']
isomer2_name = isomerName['isomer2']

# Reformat the above files to round CoV to 1 decimals
isomer1['COV']=isomer1['COV'].round(1)
isomer2['COV']=isomer2['COV'].round(1)

# Set up folder for outputs and plots

M1_RawPlots = './Module1_Outputs/Plots/ExtractIonograms'
M1_NormPlots = './Module1_Outputs/Plots/NormIonograms'
M1_isomer1_GaussPlots = './Module1_Outputs/Plots/' + isomer1_name + '_GaussianPlots'
M1_isomer2_GaussPlots = './Module1_Outputs/Plots/' + isomer2_name + '_GaussianPlots'
M1_Intersect_GaussPlots = './Module1_Outputs/Plots/GaussianIntersectPlots'

permissions = 0o777

if not os.path.exists(M1_RawPlots):
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', 'ExtractIonograms'), mode = permissions)
    os.chmod(M1_RawPlots,permissions)
else:
    os.chmod(M1_RawPlots,permissions)
    shutil.rmtree(M1_RawPlots)
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', 'ExtractIonograms'), mode = permissions)
    
if not os.path.exists(M1_NormPlots):
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', 'NormIonograms'), mode = permissions)
    os.chmod(M1_NormPlots,permissions)
else:
    os.chmod(M1_NormPlots,permissions)
    shutil.rmtree(M1_NormPlots)
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', 'NormIonograms'), mode = permissions)

if not os.path.exists(M1_isomer1_GaussPlots):
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', (isomer1_name + '_GaussianPlots')), mode = permissions)
    os.chmod(M1_isomer1_GaussPlots,permissions)
else:
    os.chmod(M1_isomer1_GaussPlots,permissions)
    shutil.rmtree(M1_isomer1_GaussPlots)
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', (isomer1_name + '_GaussianPlots')), mode = permissions)

if not os.path.exists(M1_isomer2_GaussPlots):
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', (isomer2_name + '_GaussianPlots')), mode = permissions)
    os.chmod(M1_isomer2_GaussPlots,permissions)
else:
    os.chmod(M1_isomer2_GaussPlots,permissions)
    shutil.rmtree(M1_isomer2_GaussPlots)
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', (isomer2_name + '_GaussianPlots')), mode = permissions)

if not os.path.exists(M1_Intersect_GaussPlots):
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', 'GaussianIntersectPlots'), mode = permissions)
    os.chmod(M1_Intersect_GaussPlots,permissions)
else:
    os.chmod(M1_Intersect_GaussPlots,permissions)
    shutil.rmtree(M1_Intersect_GaussPlots)
    os.makedirs(os.path.join('Module1_Outputs', 'Plots', 'GaussianIntersectPlots'), mode = permissions)

# Check python version and output as text file
python_version = sys.version
with open('Module1_Outputs/python_version.txt', mode = 'w') as file:
    file.write(python_version)


# ## STEP 2. Checking empirical data and extracting important parameters

# In[ ]:


# i) Extract sphingoid backbone information from dataset.
if isomer2['sphingoidBackbone'].unique() == isomer1['sphingoidBackbone'].unique():
    backbone = pd.unique(isomer2['sphingoidBackbone'])
    backbone = ''.join(backbone)
    print("The sphingoid backbone of the lipids used in this experiment is " + backbone)
else:
    print(f"Input dataset contains different sphingoid backbone for {isomer2_name} and {isomer1_name} isomers. Please recheck input datafile.")
    print(input("We will now exit the code. Please check your input datafiles, and restart the code with the correct input files. Type 'EXIT' "))
    exit()

titleisomer1Sph = isomer1_name + 'Sph(' + backbone + ')'
titleisomer2Sph = isomer2_name + 'Sph(' + backbone + ')'

# ii) The number of unique lipid species in the input files must equal one another.
nisomer2 = len(pd.unique(isomer2['lipidSpecies']))
isomer2_unique = set(isomer2['lipidSpecies'])
sorted(isomer2_unique)
print(f"Number of unique {isomer2_name} species are", nisomer2, "; and they are ", isomer2_unique)

nisomer1 = len(pd.unique(isomer1['lipidSpecies']))
isomer1_unique = set(isomer1['lipidSpecies'])
sorted(isomer1_unique)
print(f"Number of unique {isomer1_name} species are", nisomer1, "; and they are ", isomer1_unique)

lipid_unique = isomer2_unique.intersection(isomer1_unique)

# In this step, the code will check that the number of unique isomer2 species does equal the number of isomer1 species.
# If they equal each other, code will continue.
# If not, code will stop. User is asked to check their input dataset before retrying the code.
if (nisomer2 == nisomer1):
    nLipids = nisomer2
    list_Lipids = isomer2_unique
    print(f"The number of unique {isomer2_name} isomer equals the number of unique {isomer1_name} isomer. We will proceed!")
elif (nisomer2 > nisomer1):
    nLipids = nisomer1
    list_Lipids = list(isomer2_unique.intersection(isomer1_unique))
    print(f"The number of {isomer2_name} lipid species DOES NOT MATCH the number of {isomer1_name} lipid species. There are more {isomer2_name} species than {isomer1_name} species. Algorithm can proceed but only for the common lipids between the two isomers. Please make sure this is correct for your dataset.")
elif (nisomer2 < nisomer1):
    nLipids = nisomer2
    list_Lipids = list(isomer2_unique.intersection(isomer1_unique))
    print(f"The number of {isomer2_name} lipid species DOES NOT MATCH the number of {isomer1_name} lipid species. There are more {isomer1_name} species than {isomer2_name} species. Algorithm can proceed but only for the common lipids between the two isomers. Please make sure this is correct for your dataset.")

# Create lipid_data file

lipid_data = isomerName
lipid_data.update({"backbone":backbone,
              "lipids" : list(list_Lipids)
              })

with open("lipid_data.csv", "w", newline =                                                                                                                          "", encoding = "utf-8") as file:
    writer = csv.writer(file)
    for key, value in lipid_data.items():
        writer.writerow([key, value])

# ## STEP 3. Assess the original data, normalize and create ionogram plots of the two isomers together

# In[ ]:


# a) A dictionary is created for all dataframes generated for each lipid species for each isomer.
dataisomer1 = {}
for x in lipid_unique:
    dataisomer1[x] = pd.DataFrame()
    dataisomer1[x] = isomer1.loc[isomer1['lipidSpecies'] == x]

dataisomer2 = {}
for x in lipid_unique:
    dataisomer2[x] = pd.DataFrame()
    dataisomer2[x] = isomer2.loc[isomer2['lipidSpecies'] == x]
   
keys_dataisomer1 = list(dataisomer1.keys())
keys_dataisomer1.sort()
keys_dataisomer2 = list(dataisomer2.keys())
keys_dataisomer2.sort()

# b) Normalize the raw data of each isomer by the maximum intensity at each SV. Then plot the normalized data.
raw_isomer1PeakCoV = pd.DataFrame()
raw_isomer2PeakCoV = pd.DataFrame()
norm_rawisomer1 = pd.DataFrame()
norm_rawisomer2 = pd.DataFrame()

pd.options.mode.chained_assignment = None

## Widget for progress
root = tk.Tk()
root.wm_attributes("-topmost", 1)
root.title("Please wait...")
messageFrame = tk.Frame(root, width = 200, height = 100, bd = 3, relief=tk.FLAT)
messageFrame.pack(padx=20, pady=20)
message = "Extracting, normalizing and plotting are happening. This will take a moment. Perhaps, you would want to grab a hot beverage?"
label = tk.Label(messageFrame, text = message)              
label.pack(pady=20)
root.geometry("")
root.update_idletasks()
root.update()

for i in tqdm(range(len(list_Lipids)), desc="Processing..."):
    print(f"Completing extracting, normalizing and plotting stereoisomers with N-acyl chain {keys_dataisomer1[i]}")
    isomer1temp = isomer1[isomer1['lipidSpecies']==keys_dataisomer1[i]]
    isomer2temp = isomer2[isomer2['lipidSpecies']==keys_dataisomer2[i]]
    titleisomer1Cer = isomer1_name + 'Cer(' + backbone + '/' + str(keys_dataisomer1[i]) + ')'
    titleisomer2Cer = isomer2_name + 'Cer(' + backbone + '/' + str(keys_dataisomer2[i]) + ')'
    
    isomer1_listSV = (isomer1temp['SV'].unique()).tolist()
    isomer2_listSV = (isomer2temp['SV'].unique()).tolist()
    listSV = list(set(isomer1_listSV).intersection(isomer2_listSV))
    listSV = [int(item) for item in listSV]
    listSV.sort() 
    
    listCoV = (dataisomer1[keys_dataisomer1[i]]['COV'].unique()).tolist()
    listCoV.sort
    maxCoV = max(listCoV)
    minCoV = min(listCoV)
    numCoV = len(listCoV)-1
    
    for SV in listSV:
        isomer1tempSV = isomer1temp[(isomer1temp['SV']==SV)]
        isomer2tempSV = isomer2temp[(isomer2temp['SV']==SV)]
        if (isomer1tempSV['Intensity'].max()) != 0 and (isomer1tempSV['Intensity'].max()) > 100 : # Intensity Criteria
            raw_isomer1tempPeakCoV = isomer1tempSV.loc[isomer1tempSV['Intensity']==isomer1tempSV['Intensity'].max()]
            raw_isomer1PeakCoV = pd.concat([raw_isomer1PeakCoV, raw_isomer1tempPeakCoV])
            raw_isomer1PeakCoV.reset_index(drop = True, inplace = True)
            
        if (isomer2tempSV['Intensity'].max()) != 0 and (isomer2tempSV['Intensity'].max()) > 100 : # Intensity Criteria
            raw_isomer2tempPeakCoV = isomer2tempSV.loc[isomer2tempSV['Intensity']==isomer2tempSV['Intensity'].max()]
            raw_isomer2PeakCoV = pd.concat([raw_isomer2PeakCoV, raw_isomer2tempPeakCoV])
            raw_isomer2PeakCoV.reset_index(drop = True, inplace = True)
            
        raw_isomer1PeakCoV.sort_values(by = ['lipidSpecies', 'SV'], ascending=[True, True], inplace=True, 
                                   na_position='first', ignore_index=True, key=None)
        
        raw_isomer2PeakCoV.sort_values(by = ['lipidSpecies', 'SV'], ascending=[True, True], inplace=True,
                                   na_position='first', ignore_index=True, key=None)                

        
        # Plot raw data
        ## isomer2 first
        plt.figure()
        plt.plot(isomer2tempSV['COV'],isomer2tempSV['Intensity'], 'o', color='grey', alpha=0.75) #linewidth=1, markersize=5)
        plt.ylabel('Intensity', fontsize = 12)
        plt.yticks(fontsize=10)
        plt.xlabel('CoV at SV ' + str(SV) + ' V', fontsize = 12)
        plt.xticks([minCoV, minCoV/2, 0, maxCoV/2, maxCoV],
                   fontsize=10)
                   
        if (keys_dataisomer2[i] == '0:0'):
            plot_title = titleisomer2Sph
        else:
            plot_title = titleisomer2Cer
        
        plt.title(plot_title)
        
        plt.legend(["Signal Intensity"],
                   frameon = True,           
                   loc='best')                                             
        temp_isomer2 = plt.gcf()
        
        if (keys_dataisomer2[i] == '0:0'):
            plotname = titleisomer2Sph + '_SV' + str(SV)
        else:
            plotname = titleisomer2Cer + '_SV' + str(SV)
        
        plotname = plotname.replace(":","-").replace("/","_")                               
        plotpath = os.path.join(currentpath, M1_RawPlots,plotname)
        temp_isomer2.savefig(plotpath)
        plt.close()
        
        ## isomer1
        plt.figure()
        plt.plot(isomer1tempSV['COV'],isomer1tempSV['Intensity'], 'o', color='grey', alpha=0.75) #linewidth=1, markersize=5)
        plt.ylabel('Intensity', fontsize = 12)
        plt.yticks(fontsize=10)
        plt.xlabel('CoV at SV ' + str(SV) + ' V', fontsize = 12)
        plt.xticks([minCoV, minCoV/2, 0, maxCoV/2, maxCoV],
                   fontsize=10)
                   
        if (keys_dataisomer1[i] == '0:0'):
            plot_title = titleisomer1Sph
        else:
            plot_title = titleisomer1Cer
            
        plt.title(plot_title)
        plt.legend(["Signal Intensity"],
                   frameon = True,           
                   loc='best')
        temp_isomer1 = plt.gcf()
        
        if (keys_dataisomer1[i] == '0:0'):
            plotname = titleisomer1Sph + '_SV' + str(SV)
        else:
            plotname = titleisomer1Cer + '_SV' + str(SV)
        
        plotname = plotname.replace(":","-").replace("/","_")
        plotpath = os.path.join(currentpath, M1_RawPlots,plotname)
        temp_isomer1.savefig(plotpath)
        plt.close()
        time.sleep(0.05)
            
        #Normalize the raw data
        isomer1tempSV['NormPeakIntensity'] = isomer1tempSV["Intensity"]/isomer1tempSV["Intensity"].max()
        norm_rawisomer1 = pd.concat([norm_rawisomer1, isomer1tempSV])
        norm_rawisomer1.reset_index(drop = True, inplace = True)
        
        isomer2tempSV['NormPeakIntensity'] = isomer2tempSV["Intensity"]/isomer2tempSV["Intensity"].max()
        norm_rawisomer2 = pd.concat([norm_rawisomer2, isomer2tempSV])
        norm_rawisomer2.reset_index(drop = True, inplace = True)

        
        # Plot normalized data
        ## isomer2 first
        plt.plot(isomer2tempSV['COV'],isomer2tempSV['NormPeakIntensity'], 'o', color='grey', alpha=0.75) #linewidth=1, markersize=5)
        plt.plot(isomer2tempSV['COV'],isomer2tempSV['NormPeakIntensity'],color='grey')
        plt.ylabel('Normalized  Intensity', fontsize = 12)
        plt.xlabel('CoV at SV ' + str(SV) + ' V', fontsize = 12)
        plt.xticks([minCoV, minCoV/2, 0, maxCoV/2, maxCoV],
                   fontsize=10)
        
        if (keys_dataisomer2[i] == '0:0'):
            plot_title = titleisomer2Sph
        else:
            plot_title = titleisomer2Cer
            
        plt.title(plot_title)
        
        plt.legend(["Normalized Intensity"],
                   frameon = True,           
                   loc='best')                
        temp_isomer2 = plt.gcf()

        if (keys_dataisomer2[i] == '0:0'):
            plotname = titleisomer2Sph + '_SV' + str(SV)
        else:
            plotname = titleisomer2Cer + '_SV' + str(SV)
        
        plotname = plotname.replace(":","-").replace("/","_")
        plotpath = os.path.join(currentpath, M1_NormPlots, plotname)
        temp_isomer2.savefig(plotpath)
        plt.close()

        ## isomer1
        plt.plot(isomer1tempSV['COV'],isomer1tempSV['NormPeakIntensity'], 'o', color='grey', alpha=0.75) #linewidth=1, markersize=5)
        plt.plot(isomer1tempSV['COV'],isomer1tempSV['NormPeakIntensity'],color='grey')
        plt.ylabel('Normalized  Intensity', fontsize = 12)
        plt.xlabel('CoV at SV ' + str(SV) + ' V', fontsize = 12)
        plt.xticks([minCoV, minCoV/2, 0, maxCoV/2, maxCoV],
                   fontsize=10)
        
        if (keys_dataisomer1[i] == '0:0'):
            plot_title = titleisomer1Sph
        else:
            plot_title = titleisomer1Cer
            
        plt.title(plot_title)
        
        plt.legend(["Normalized Intensity"],
                   frameon = True,           
                   loc='best')
        temp_isomer1 = plt.gcf()

        if (keys_dataisomer1[i] == '0:0'):
            plotname = titleisomer1Sph + '_SV' + str(SV)
        else:
            plotname = titleisomer1Cer + '_SV' + str(SV)
        
        plotname = plotname.replace(":","-").replace("/","_")
        plotpath = os.path.join(currentpath, M1_NormPlots, plotname)
        temp_isomer1.savefig(plotpath)
        plt.close()
plt.close()
root.destroy()

# Drop old index column
raw_isomer1PeakCoV.drop(raw_isomer1PeakCoV.columns[raw_isomer1PeakCoV.columns.str.contains('unnamed', case=False)], axis = 1, inplace = True)
raw_isomer2PeakCoV.drop(raw_isomer2PeakCoV.columns[raw_isomer2PeakCoV.columns.str.contains('unnamed', case=False)], axis = 1, inplace = True)
norm_rawisomer1.drop(norm_rawisomer1.columns[norm_rawisomer1.columns.str.contains('unnamed', case=False)], axis = 1, inplace = True)
norm_rawisomer2.drop(norm_rawisomer2.columns[norm_rawisomer2.columns.str.contains('unnamed', case=False)], axis = 1, inplace = True)

# Output Extracted Ionograms to csv file
isomer1_filename = "Module1_Outputs/extract" + isomer1_name + "MaxCov.csv"
isomer2_filename = "Module1_Outputs/extract" + isomer2_name + "MaxCov.csv"
raw_isomer1PeakCoV.to_csv(isomer1_filename, index = None)
raw_isomer2PeakCoV.to_csv(isomer2_filename, index = None)

# Output Normalized Ionograms to csv file
norm_isomer1_filename = "Module1_Outputs/norm_" + isomer1_name + ".csv"
norm_isomer2_filename = "Module1_Outputs/norm_" + isomer2_name + ".csv"
norm_rawisomer1.to_csv(norm_isomer1_filename, index = None)
norm_rawisomer2.to_csv(norm_isomer2_filename, index = None)
# In[ ]:

# Message to users
print("All plots from original extracted data are saved in folder called 'ExtractIonograms'.")
print("All plots from normalized input data are saved in folder called 'NormIonograms'. ")


# ## STEP 4. Gaussian fit the normalized data, then obtain gaussian features (sigma and mu) from the fitting

# In[ ]:

# a) Gaussian fit to normalized data. As well, extract Gaussian features at each SV.

norm_isomer1Parameters = pd.DataFrame()
norm_isomer2Parameters = pd.DataFrame()

pd.options.mode.chained_assignment = None
lipid_isomer = ["isomer1", "isomer2"]

## Define Gaussian function
def gaussian(x, mu, sigma):
   y = 1 * exp(-0.5*((x-mu)/sigma)**2)
   return y

## Widget for progress
root = tk.Tk()
root.wm_attributes("-topmost", 1)
root.title("Please wait...")
messageFrame = tk.Frame(root,width = 200, height = 100, bd = 3, relief=tk.FLAT)
messageFrame.pack(padx=20, pady=20)
message = "Gaussian modeling and parameters extracting are happening. This will take awhile. But hey, just remember, if you hang in there long enough, good things can happen in this world!"
label = tk.Label(messageFrame, text = message)              
label.pack(pady=20)
root.geometry("")
root.update_idletasks()
root.update()


## Looping to derive function and features from data
for isomer in tqdm(lipid_isomer, desc = "Processing..."):
    if isomer == "isomer1":
        for i in range(len(list_Lipids)):
            print(f"Gaussian-modelling and plotting for stereoisomer {isomer1_name} with N-acyl chain {keys_dataisomer1[i]}")
            isomer1temp = (norm_rawisomer1[norm_rawisomer1['lipidSpecies']==keys_dataisomer1[i]])
            isomer1tempmu = raw_isomer1PeakCoV[raw_isomer1PeakCoV['lipidSpecies']==keys_dataisomer1[i]]
            titleisomer1Cer = isomer1_name + 'Cer(' + backbone + '/' + str(keys_dataisomer1[i]) + ')'
            titleisomer2Cer = isomer2_name + 'Cer(' + backbone + '/' + str(keys_dataisomer2[i]) + ')'
            
            listCoV = (dataisomer1[keys_dataisomer1[i]]['COV'].unique()).tolist()
            listCoV.sort
            maxCoV = max(listCoV)
            minCoV = min(listCoV)
            numCoV = len(listCoV)-1
            
            listSV = (isomer1temp['SV'].unique()).tolist()
            listSV = [int(item) for item in listSV]
            listSV.sort() 
            
            for SV in listSV:
                isomer1tempSV = isomer1temp[(isomer1temp['SV']==SV)]
                isomer1tempmuSV = isomer1tempmu[(isomer1tempmu['SV']==SV)]
                
                if isomer1tempmuSV.shape[0] != 0:                   
                    xisomer1data = ar(isomer1tempSV["COV"])
                    yisomer1data = ar(isomer1tempSV["NormPeakIntensity"])
                    mu_isomer1 = float(sum(isomer1tempmuSV['COV'])/(isomer1tempmuSV.shape[0])) #this will be the start point
                    
                    # Use Model fit to fit data. Here we use Lmfit to build a Model wrapping the gaussian model function
                    # We assign initial values for this model with mu as the average mu across all CoV for a specific SV (peakCoV)
                    # and sigma at 1.
                    # As well, here, we use method 'fit' of the model to fit data to this model with the initial parameters
                    gmodel = Model(gaussian)
                    isomer1_result = gmodel.fit(yisomer1data, x=xisomer1data, mu = mu_isomer1, sigma = 1)
                    isomer1_uncertain = isomer1_result.eval_uncertainty(sigma = 3)

                    # Modified parameters set 1 for less optimal fit_FOR isomer1
                    modified_isomer1_params1 = isomer1_result.init_params.copy()
                    modified_isomer1_params1['mu'].value = mu_isomer1
                    modified_isomer1_params1['sigma'].value = 0.75
                    
                    # Calculate new model 1 with modified parameters set 1_FOR isomer1
                    y_isomer1_modified1 = gmodel.eval(modified_isomer1_params1, x=xisomer1data)
                    
                    # Modified parameters set 2 for less optimal fit_FOR isomer1
                    modified_isomer1_params2 = isomer1_result.init_params.copy()
                    modified_isomer1_params2['mu'].value = mu_isomer1
                    modified_isomer1_params2['sigma'].value = 0.25
                    
                    # Calculate new model 2 with modified parameters set 2_FOR isomer1
                    y_isomer1_modified2 = gmodel.eval(modified_isomer1_params2, x=xisomer1data)
                    
                    # The ModelResult methods provide fit parameters and results from the model. We use 'summary' method
                    # to output the statistics and attributes of the model's results. This is a dictionary.
                    # We then derive the value for key "best_values" from the summary, which are mu and sigma
                    gmodel_report = isomer1_result.fit_report()
                    gmodel_summary = isomer1_result.summary()
                    bestfit_features = gmodel_summary["best_values"]
                    bestfit_features_list = list(bestfit_features.values())
                    r_squared = gmodel_summary["rsquared"]
                    
                    
                    # The best fit values are now derived from feature list above and assigned to mu, sigma
                    isomer1_fit_mu = bestfit_features_list[0]
                    isomer1_fit_sigma = bestfit_features_list[1]
                    
                    # Now, we will use method 'eval' to evalute our model function. Here, we will calculate
                    # confidence interval of the fitted variable parameters, determine the uncertainties of our model,
                    # and plot the uncertainties as number of sigma away from the fit parameters
                    
                    # a) Confidence interval: Use F-test method. The optimized/fit parameters are compared to a specific value.
                    # Read: lmfit.github.io/lmfit-py/confidence.html#confidence-chapter
                    # b) Uncertainty: Calculate the uncertainties of the fitted parameters. This means, given a specific value
                    # of sigma away from the fitted parameters, what are the predicted y values. We get to see how far the
                    # predictions are from the actual data, and the fitted curve.
                    ci = isomer1_result.conf_interval()
                    isomer1_uncertain = isomer1_result.eval_uncertainty(sigma = 3)
                    
                                       
                    # Compile Peak Features for isomer1
                    isomer1tempmuSV['NormPeakIntensity'] = yisomer1data.max()
                    isomer1tempmuSV['Empirical mu'] = mu_isomer1
                    isomer1tempmuSV[isomer1_name + '_Gaussian_mu'] = round(isomer1_fit_mu,1)
                    isomer1tempmuSV[isomer1_name + '_Gaussian_sigma'] = round(isomer1_fit_sigma,3)
                    isomer1tempmuSV[isomer1_name + '_Rsquared'] = r_squared
                    norm_isomer1Parameters = pd.concat([norm_isomer1Parameters,isomer1tempmuSV])
                    norm_isomer1Parameters.reset_index(drop = True, inplace = True)
                       
                      # Plot fit over original data. We will display original data, initial fit with given initial 
                      # parameters and best fit values. 

                    plt.figure()
                    plt.ylabel('Normalized  Intensity', fontsize = 12)
                    plt.xlabel('CoV at SV ' + str(SV) + ' V', fontsize = 12)
                    
                    if (keys_dataisomer1[i] == '0:0'):
                        plot_title = titleisomer1Sph
                    else:
                        plot_title = titleisomer1Cer
                        
                    plt.title(plot_title)
                
                    plt.plot(xisomer1data, yisomer1data, 'o', color='grey', label='Normalized Intensity',alpha=0.75, markersize=5)
                    plt.plot(xisomer1data, isomer1_result.init_fit, '--', color='darkorange', label='Initial fit',linewidth=1)
                    plt.plot(xisomer1data, y_isomer1_modified1, '--', label='Less Optimal Fit 1', color = 'goldenrod',linewidth=1)
                    plt.plot(xisomer1data, y_isomer1_modified2, '--', label='Less Optimal Fit 2', color = 'gold',linewidth=1)
                    plt.plot(xisomer1data, isomer1_result.best_fit, '-', color='green', label='Optimal Gaussian Model',linewidth=1)
                    plt.xticks([minCoV, minCoV/2, 0, maxCoV/2, maxCoV])
                    plt.legend(frameon = True,           
                                loc='best')
                    temp_isomer1 = plt.gcf()
                                            
                    if (keys_dataisomer1[i] == '0:0'):
                        plotname = titleisomer1Sph + '_SV' + str(SV)
                    else:
                        plotname = titleisomer1Cer + '_SV' + str(SV)
                    
                    plotname = plotname.replace(":","-").replace("/","_")
                    plotpath = os.path.join(currentpath, M1_isomer1_GaussPlots, plotname)
                    temp_isomer1.savefig(plotpath)
                    plt.close()
                    
    elif isomer == "isomer2":
        for i in range(len(list_Lipids)):
            print(f"Gaussian-modelling and plotting for stereoisomer {isomer2_name} with N-acyl chain {keys_dataisomer2[i]}")
            isomer2temp = (norm_rawisomer2[norm_rawisomer2['lipidSpecies']==keys_dataisomer2[i]])
            isomer2tempmu = raw_isomer2PeakCoV[raw_isomer2PeakCoV['lipidSpecies']==keys_dataisomer2[i]]
            titleisomer1Cer = isomer1_name + 'Cer(' + backbone + '/' + str(keys_dataisomer1[i]) + ')'
            titleisomer2Cer = isomer2_name + 'Cer(' + backbone + '/' + str(keys_dataisomer2[i]) + ')'
            
            listCoV = (dataisomer1[keys_dataisomer2[i]]['COV'].unique()).tolist()
            listCoV.sort
            maxCoV = max(listCoV)
            minCoV = min(listCoV)
            numCoV = len(listCoV)-1
            
            listSV = (isomer2temp['SV'].unique()).tolist()
            listSV = [int(item) for item in listSV]
            listSV.sort() 

            for SV in listSV:
                isomer2tempSV = isomer2temp[(isomer2temp['SV']==SV)]
                isomer2tempmuSV = isomer2tempmu[(isomer2tempmu['SV']==SV)]
                
                if isomer2tempmuSV.shape[0] != 0:
                
                    xisomer2data = ar(isomer2tempSV["COV"])
                    yisomer2data = ar(isomer2tempSV["NormPeakIntensity"])
                    mu_isomer2 = float(sum(isomer2tempmuSV['COV'])/(isomer2tempmuSV.shape[0])) #this will be the start point
                    
                    # Use Model fit to fit data. Here we use Lmfit to build a Model wrapping the gaussian model function
                    # We assign initial values for this model with mu as the average mu across all CoV for a specific SV (peakCoV)
                    # and sigma at 1.
                    # As well, here, we use method 'fit' of the model to fit data to this model with the initial parameters
                    gmodel = Model(gaussian)
                    isomer2_result = gmodel.fit(yisomer2data, x=xisomer2data, mu = mu_isomer2, sigma = 1)

                    # Modified parameters set 1 for less optimal fit_FOR isomer2
                    modified_isomer2_params1 = isomer2_result.init_params.copy()
                    modified_isomer2_params1['mu'].value = mu_isomer2
                    modified_isomer2_params1['sigma'].value = 0.75
                    
                    # Calculate new model 1 with modified parameters set 1_FOR isomer2
                    y_isomer2_modified1 = gmodel.eval(modified_isomer2_params1, x=xisomer2data)
                    
                    # Modified parameters set 2 for less optimal fit_FOR isomer2
                    modified_isomer2_params2 = isomer2_result.init_params.copy()
                    modified_isomer2_params2['mu'].value = mu_isomer2
                    modified_isomer2_params2['sigma'].value = 0.25
                    
                    # Calculate new model 2 with modified parameters set 2_FOR isomer2
                    y_isomer2_modified2 = gmodel.eval(modified_isomer2_params2, x=xisomer2data)
                    
                    # The ModelResult methods provide fit parameters and results from the model. We use 'summary' method
                    # to output the statistics and attributes of the model's results. This is a dictionary.
                    # We then derive the value for key "best_values" from the summary, which are mu and sigma
                    gmodel_report = isomer2_result.fit_report()
                    gmodel_summary = isomer2_result.summary()
                    bestfit_features = gmodel_summary["best_values"]
                    bestfit_features_list = list(bestfit_features.values())
                    r_squared = gmodel_summary["rsquared"]

                    # The best fit values are now derived from feature list above and assigned to mu, sigma
                    isomer2_fit_mu = bestfit_features_list[0]
                    isomer2_fit_sigma = bestfit_features_list[1]
                    
                    # Now, we will use method 'eval' to evalute our model function. Here, we will calculate
                    # confidence interval of the fitted variable parameters, determine the uncertainties of our model,
                    # and plot the uncertainties as number of sigma away from the fit parameters
                    
                    # a) Confidence interval: Use F-test method. The optimized/fit parameters are compared to a specific value.
                    # Read: lmfit.github.io/lmfit-py/confidence.html#confidence-chapter
                    # b) Uncertainty: Calculate the uncertainties of the fitted parameters. This means, given a specific value
                    # of sigma away from the fitted parameters, what are the predicted y values. We get to see how far the
                    # predictions are from the actual data, and the fitted curve.
                    ci = isomer2_result.conf_interval()
                    isomer2_uncertain = isomer2_result.eval_uncertainty(sigma = 3)

                    # Compile Peak Features for isomer2
                    isomer2tempmuSV['NormPeakIntensity'] = yisomer2data.max()
                    isomer2tempmuSV['Empirical mu'] = mu_isomer2
                    isomer2tempmuSV[isomer2_name + '_Gaussian_mu'] = round(isomer2_fit_mu,1)
                    isomer2tempmuSV[isomer2_name + '_Gaussian_sigma'] = round(isomer2_fit_sigma,3)
                    isomer2tempmuSV[isomer2_name + '_Rsquared'] = r_squared
                    norm_isomer2Parameters = pd.concat([norm_isomer2Parameters,isomer2tempmuSV])
                    norm_isomer2Parameters.reset_index(drop = True, inplace = True)
                       
                    # Plot fit over original data. We will display original data, initial fit with given initial 
                    # parameters and best fit values. 
                    plt.figure()
                    plt.ylabel('Normalized  Intensity', fontsize = 12)
                    plt.xlabel('CoV at SV ' + str(SV) + ' V', fontsize = 12)
                    
                    plt.plot(xisomer2data, yisomer2data, 'o', color='grey', label='Normalized Intensity', alpha=0.75, markersize=5)
                    plt.plot(xisomer2data, isomer2_result.init_fit, '--', color='darkorange', label='Initial fit',linewidth=1)
                    plt.plot(xisomer2data, y_isomer2_modified1, '--', label='Less Optimal Fit 1', color = 'goldenrod',linewidth=1)
                    plt.plot(xisomer2data, y_isomer2_modified2, '--', label='Less Optimal Fit 2', color = 'gold',linewidth=1)
                    plt.plot(xisomer2data, isomer2_result.best_fit, '-', color='blue', label='Optimal Gaussian Model',linewidth=1)
                    plt.xticks([minCoV, minCoV/2, 0, maxCoV/2, maxCoV])
                    
                    if (keys_dataisomer2[i] == '0:0'):
                        plot_title = titleisomer2Sph
                    else:
                        plot_title = titleisomer2Cer
                        
                    plt.title(plot_title)
                    
                    plt.legend(frameon = True,           
                                loc='best')
                    
                    temp_isomer2 = plt.gcf()
                                            
                    if (keys_dataisomer2[i] == '0:0'):
                        plotname = titleisomer2Sph + '_SV' + str(SV)
                    else:
                        plotname = titleisomer2Cer + '_SV' + str(SV)
                    
                    plotname = plotname.replace(":","-").replace("/","_")
                    plotpath = os.path.join(currentpath, M1_isomer2_GaussPlots, plotname)
                    temp_isomer2.savefig(plotpath)
                    plt.close()
plt.close()
root.destroy()

## Output Gaussian files
norm_isomer1Parameters_filename = "Module1_Outputs/norm_" + isomer1_name + "Parameters.csv"
norm_isomer2Parameters_filename = "Module1_Outputs/norm_" + isomer2_name + "Parameters.csv"
norm_isomer1Parameters.to_csv(norm_isomer1Parameters_filename, index = None)
norm_isomer2Parameters.to_csv(norm_isomer2Parameters_filename, index = None)

# Message to users
print("All plots from Gaussian model of your data are saved in folder called 'GaussianPlots', preceded by the name of your stereoisomer.")


# In[ ]:

# b) Combined Gaussian features extracted from isomer1 and isomer2

isomer1features = pd.DataFrame()
isomer1features_combined = pd.DataFrame()
isomer2features = pd.DataFrame()
isomer2features_combined = pd.DataFrame()

## Widget for progress
root = tk.Tk()
root.wm_attributes("-topmost", 1)
root.title("Please wait...")
messageFrame = tk.Frame(root, width = 200, height = 100, bd = 3, relief=tk.FLAT)
messageFrame.pack(padx=20, pady=20)
message = "iDMS is combining data from the two stereoisomers. This will not take long. Don't leave. "
label = tk.Label(messageFrame, text = message)              
label.pack(pady=20)
root.geometry("")
root.update_idletasks()
root.update()

for i in tqdm(range(len(list_Lipids)), desc="Processing..."):
    print(f"Combining data and Gaussian parameters for stereoisomers with N-acyl chain {keys_dataisomer1[i]}")
    isomer1features_temp = (norm_isomer1Parameters[norm_isomer1Parameters['lipidSpecies']==keys_dataisomer1[i]])
    isomer2features_temp = (norm_isomer2Parameters[norm_isomer2Parameters['lipidSpecies']==keys_dataisomer2[i]])
    
    isomer1_listSV = (isomer1features_temp['SV'].unique()).tolist()
    isomer2_listSV = (isomer2features_temp['SV'].unique()).tolist()
    listSV = list(set(isomer1_listSV).intersection(isomer2_listSV))
    listSV = [int(item) for item in listSV]
    listSV.sort() 
    
    for SV in listSV:
        isomer1featuresSV = isomer1features_temp[isomer1features_temp['SV']==SV]
        isomer2featuresSV = isomer2features_temp[isomer2features_temp['SV']==SV]
        
        cols = ["lipidSpecies", "SV", "chainLength", "unsaturationUnit", "sphingoidBackbone"]
        isomer1features = isomer1featuresSV[cols]
        isomer1features.drop_duplicates(inplace = True)
        
        isomer2features = isomer2featuresSV[cols]
        isomer2features.drop_duplicates(inplace = True)
        
        isomer1features['mu_' + isomer1_name] =  isomer1featuresSV.loc[:,(isomer1_name + '_Gaussian_mu') ]
        isomer1features['sigma_' + isomer1_name] = isomer1featuresSV.loc[:,(isomer1_name + '_Gaussian_sigma')]
        isomer1features['Intensity_at_mu_' + isomer1_name] = isomer1featuresSV.loc[:,'Intensity']
        
        isomer2features['mu_' + isomer2_name] =  isomer2featuresSV.loc[:,(isomer2_name + '_Gaussian_mu')]
        isomer2features['sigma_' + isomer2_name] = isomer2featuresSV.loc[:,(isomer2_name + '_Gaussian_sigma')]
        isomer2features['Intensity_at_mu_' + isomer2_name] = isomer2featuresSV.loc[:,'Intensity']
                
        isomer1features_combined = pd.concat([isomer1features_combined, isomer1features])
        isomer2features_combined = pd.concat([isomer2features_combined, isomer2features])
        
        if isomer1features_combined.shape[0] > isomer2features_combined.shape[0]:
            CombinedAnalysis = pd.merge(isomer1features_combined, isomer2features_combined, how = "outer", on = ["lipidSpecies", "SV", "chainLength", "unsaturationUnit", "sphingoidBackbone"])
            
        else:
            CombinedAnalysis = pd.merge(isomer1features_combined, isomer2features_combined, how = "outer", on = ["lipidSpecies", "SV", "chainLength", "unsaturationUnit", "sphingoidBackbone"])
            
        CombinedAnalysis.reset_index(drop = True, inplace = True)
        CombinedAnalysis.drop(CombinedAnalysis.columns[CombinedAnalysis.columns.str.contains('unnamed', case=False)], axis = 1, inplace = True)
root.destroy()
                              
## Output Gaussian files
CombinedAnalysis.to_csv('Module1_Outputs/CombinedAnalysis.csv', index=None)

## Calculate average sigma across all lipids, at each SV
meanAllsigma = CombinedAnalysis.groupby('SV').mean(('sigma_' + isomer1_name), ('sigma_' + isomer2_name)).reset_index()
meanAllsigma['sigma_' + isomer1_name] = round(meanAllsigma['sigma_' + isomer1_name],3)
meanAllsigma['sigma_' + isomer2_name] = round(meanAllsigma['sigma_' + isomer2_name],3)
meanAllsigma.to_csv('Module1_Outputs/meanAllsigma.csv', columns =['SV',('sigma_' + isomer1_name), ('sigma_' + isomer2_name)], index=None)


# ## STEP 5. Find the intersection point of isomer2 and isomer1

# In[ ]:

Intersected_gauss = pd.DataFrame()

def solve(mu_isomer1,mu_isomer2,sig_isomer1,sig_isomer2): 
  a = 1/(2*sig_isomer1**2) - 1/(2*sig_isomer2**2)
  b = mu_isomer2/(sig_isomer2**2) - mu_isomer1/(sig_isomer1**2)
  c = mu_isomer1**2 /(2*sig_isomer1**2) - mu_isomer2**2 / (2*sig_isomer2**2) - np.log(sig_isomer2/sig_isomer1)
  return np.roots([a,b,c])

## Widget for progress
root = tk.Tk()
root.wm_attributes("-topmost", 1)
root.title("Please wait...")
messageFrame = tk.Frame(root, width = 200, height = 100, bd = 3, relief=tk.FLAT)
messageFrame.pack(padx=20, pady=20)
message = "Determining the intersection point of the two stereoisomers. This will take some time, but remember, 'Good things come to those who wait'!"
label = tk.Label(messageFrame, text = message)              
label.pack(pady=20)
root.geometry("")
root.update_idletasks()
root.update()

for i in tqdm(range(len(list_Lipids)), desc="Processing..."):
    print(f"Determining the intersection point betweent the two stereoisomers with N-acyl chain {keys_dataisomer1[i]}")
    intersect_temp = (CombinedAnalysis[CombinedAnalysis['lipidSpecies']==keys_dataisomer1[i]])
    titleisomer1Cer = isomer1_name + 'Cer(' + backbone + '/' + str(keys_dataisomer1[i]) + ')'
    titleisomer2Cer = isomer2_name + 'Cer(' + backbone + '/' + str(keys_dataisomer2[i]) + ')'
    
    listSV = (intersect_temp['SV'].unique()).tolist()
    listSV = [int(item) for item in listSV]
    listSV.sort()
    
    listCoV = (dataisomer1[keys_dataisomer1[i]]['COV'].unique()).tolist()
    listCoV.sort
    maxCoV = max(listCoV)
    minCoV = min(listCoV)
    numCoV = len(listCoV)-1
    
    sig_isomer2 = np.linspace(minCoV, maxCoV, 10000)
    sig_isomer1 = np.linspace(minCoV, maxCoV, 10000)

    for SV in listSV:
        intersectSV_temp = intersect_temp[intersect_temp['SV']==SV]
        
        if intersectSV_temp[("mu_" + isomer1_name)].notna() is False:
            continue
        else:
            mu_isomer1 = intersectSV_temp["mu_" + isomer1_name]
            mu_isomer1 = mu_isomer1.iloc[0]
            sig_isomer1 = intersectSV_temp["sigma_" + isomer1_name]
            sig_isomer1 = sig_isomer1.iloc[0]
        
        if intersectSV_temp[("mu_" + isomer2_name)].notna() is False:
            continue
        else:
            mu_isomer2 = intersectSV_temp["mu_" + isomer2_name]
            mu_isomer2 = mu_isomer2.iloc[0]
            sig_isomer2 = intersectSV_temp["sigma_" + isomer2_name]
            sig_isomer2 = sig_isomer2.iloc[0]
        
        gauss_features = [mu_isomer1, mu_isomer2, sig_isomer1, sig_isomer2] 
     
        if any(pd.isna(gauss_features)) is True:
            continue
        else:
            resultCombined = solve(mu_isomer1, mu_isomer2, sig_isomer1, sig_isomer2)
        
        
        # Based on peak CoV, this step we predict the intensity by refitting X back to the gaussian function.
        x = np.linspace(minCoV,maxCoV,10000) 
        y_isomer1 = gaussian(x, mu_isomer1, sig_isomer1)
        y_isomer2 = gaussian(x, mu_isomer2, sig_isomer2)
        
        # Intersection point is limited to only that lies between mu of isomer2 and isomer1
        mu_range_max = max(mu_isomer1, mu_isomer2)
        mu_range_min = min(mu_isomer1, mu_isomer2)
        
        intersect = max([point for point in resultCombined if mu_range_min < point < mu_range_max], default = None)
        
        if intersect is None:
            y_at_intersect = intersect
        else:
            intersect = round(intersect,3)
            y_at_intersect = gaussian(intersect, mu_isomer1, sig_isomer1) 
         
        if intersect != None and (y_at_intersect < 0.5 ):
            intersectSV_temp["Valley CoV"] = intersect # Valley is defined as separation
        else:
            intersectSV_temp["Valley CoV"] = None

        intersectSV_temp["Intersection point"] = intersect
        intersectSV_temp["Norm Intensity at Intersection"] = y_at_intersect        
        
        #############
        
        fig,ax = plt.subplots()
        #ax.set_xlim([minCoV, maxCoV])

        plt.ylabel('Normalized  Intensity', fontsize = 12)
        plt.xlabel('CoV at SV ' + str(SV) + ' V', fontsize = 12)
        plot1 = ax.plot(x, y_isomer1, color='green', label= isomer1_name + ' Gaussian Model')
        plot2 = ax.plot(x, y_isomer2, color='blue', label= isomer2_name + ' Gaussian Model')
        plt.xticks([minCoV, minCoV/2, 0, maxCoV/2, maxCoV])

        if intersect != None:
          plot3 = ax.plot(intersect, y_at_intersect, 'ro', fillstyle='full', label = 'Intersection point')
          
        if (keys_dataisomer2[i] == '0:0'):
            plot_title = "Separability of " + titleisomer1Sph + " and " + titleisomer2Sph
        else:
            plot_title = "Separability of " + titleisomer1Cer + " and " + titleisomer2Cer   
        plt.title(plot_title)
         
        ax.legend(loc='upper right')
        temp_plot = plt.gcf()

        plotname = 'Separability' + isomer1_name + keys_dataisomer1[i] + '_' + isomer2_name + keys_dataisomer2[i] + '_SV' + str(SV)
        
        if (keys_dataisomer1[i] == '0:0'):
            plotname = 'Separability' + titleisomer1Sph + '_' + titleisomer2Sph + '_SV' + str(SV)
        else:
            plotname = 'Separability' + titleisomer1Cer + '_' + titleisomer2Cer + '_SV' + str(SV)
            
        plotname = plotname.replace(":","-").replace("/","_")
        plotpath = os.path.join(currentpath, M1_Intersect_GaussPlots, plotname)
        temp_plot.savefig(plotpath)
        plt.close()

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category = FutureWarning)   
            Intersected_gauss = pd.concat([Intersected_gauss, intersectSV_temp])

        Intersected_gauss.reset_index(drop = True, inplace = True)
plt.close()
root.destroy()

# Binary Separation Column

Intersected_gauss['Sep or InSep'] = np.where(Intersected_gauss['Valley CoV'].isnull(), "Inseparable", "Separable")
        
# Output intersection point to files

Intersected_gauss = Intersected_gauss.replace('NAN','')
Intersected_gauss.to_csv('Module1_Outputs/Intersected gauss.csv', index=None)

# In[ ]:


print("Module 1 has finished. You can find all output files and plots in the folder directory you selected in the beginning. Please proceed to Module 2")
msg_to_users(messagebox.showinfo,"Message to user.", "Module 1 has finished. You can find all output files and plots in the folder directory you selected in the beginning. We know you have waited for awhile to get to this point. Remember, 'Initiative comes to thems that wait'. Now, please proceed to Module 2.")
