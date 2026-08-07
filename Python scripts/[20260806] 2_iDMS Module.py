#!/usr/bin/env python
# coding: utf-8

# # Module 2 - Building Neural Network with Input Data and Performing New Prediction
#
# Update on 2026-08-06
#
# Submitted with iDMS manuscript.
#
# Tested on Windows 10 and 11, 64-bit operating system, macOS 14+ on both Apple silicon and Intel chips.
#
# This module is designed to run in a virtual environment which has had all dependencies and libraries installed from the provided requirements.txt file. Without having done this, this module will not be able to proceed.
#
# In order to execute this module, files generated from Module 1 are needed:
#
## CombinedAnalysis.xlsx
## meanAllsigma.xlsx
## Intersected gauss.xlsx
## lipid_data.csv
##
# This module is used to perform predictions on novel lipid isomer pairs. Based on the information obtained from the training dataset, this module will make prediction of whether pairs of glycosphingolipid stereoisomer carrying the same backbone as those in the training dataset with different **N**-acyl chain length and number of unsaturation unit will be separable or not at each given SV and CoV combination. The SV and CoV range and step will be the same as that given in the training dataset.
#
# Users will be asked to navigate to the directory where their input data files are stored. Input data files are all contained in Module1_Outputs folder. Users need to navigate to the **folder** which contains the Module1_Outputs folder. Secondly, users also need to provide a file containing a list of lipids for which users wish to predict. Users must use the template provided on github, named **"Predlist_Lipids.csv"**, to provide a list of lipid identity for prediction. Please use a text editor (such as Notepad on Windows or TextEdit on MAC) when making changes to this file instead of Microsoft Excel.
#
# The output files are: **PredictionResult.csv, TrainingSet.csv, iDMS_params.csv, iDMS_training_history.csv**.
#
# The output plots are stored in folder **PredictedSetPlots**.
#
# The prediction output in the csv file "PredictionResult.csv" which lists all the lipids user wishes to perform predictions on. This output will also contain a column predicting the CoV at which the ionograms of the two isomers will intersect, and whether this intersection point is considered as "Separable" or "Inseparable".

# In[ ]:
# ## IMPORT LIBRARIES AND PACKAGES REQUIRED FOR IDMS NOTEBOOK


# Import basic system parameters and functions 
SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True  

import sys
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np
import csv
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from numpy import exp

# Added based on Emily GUI
import keras
keras.utils.set_random_seed(42)  # Emily added
from keras import layers
from keras import models
from keras.callbacks import EarlyStopping
pd.options.mode.chained_assignment = None
import warnings

# Added seeding
np.random.seed(42)

# Create function for function with messages to user:
def msg_to_users(func, *args, **kwargs):
    root = tk.Tk()
    root.lift()
    root.wm_attributes("-topmost",1)
    root.withdraw()
    result = []
    def msg_to_users():
        result.append(func(*args,**kwargs))
        root.destroy()
    root.after_idle(msg_to_users)
    root.mainloop()
    root.quit()
    return result.pop()

# Prompt users to navigate to the folder where outputs from Module 1 were stored

msg_to_users(messagebox.showinfo, "Message to user.", "In the next window, please select folder directory where output files from Module 1 (folder Module1_Outputs) are stored.")

InputDir = msg_to_users(filedialog.askdirectory,
                                    initialdir="/",
                                    title = "Browse to where Module 1 outputs are stored. ")
if len(InputDir) > 0:
    print ("You chose %s" % InputDir + ". This will also be where the outputs of this module is stored in.")

M1_Output = os.path.join(InputDir, 'Module1_Outputs')

# Set Directory Location
currentpath = InputDir
os.chdir(currentpath)

# Set up folder for outputs and plots
M2_top = './Module2_Outputs'
M2_PredPlots = './Module2_Outputs/PredictedSetPlots'

permissions = 0o777

if not os.path.exists(M2_PredPlots):
    os.makedirs(os.path.join('Module2_Outputs', 'PredictedSetPlots'), mode = permissions)
    os.chmod(M2_PredPlots,permissions)
else:
    os.chmod(M2_PredPlots,permissions)
    shutil.rmtree(M2_PredPlots)
    os.makedirs(os.path.join("Module2_Outputs", "PredictedSetPlots"), mode = permissions)

# Check python version and output as text file
python_version = sys.version
with open('Module2_Outputs/python_version.txt', mode = 'w') as file:
    file.write(python_version)

# ## STEP 1. Import the required files
# 
# Files generated from Module 1 are imported. All lipids in files generated in Module 1 are used for Training Dataset. Users are then prompted to submit an excel file listing lipids which they wish to predict for. The excel file must contain only 1 column, with column heading (hence, cell A1 of excel sheet will be ignored). For convenience, user is advised to use the provided template to generate their list of lipids. 

# In[ ]:

meanAllsigma = pd.read_csv(os.path.join(M1_Output, 'meanAllsigma.csv'))
Intersected_gauss = pd.read_csv(os.path.join(M1_Output, 'Intersected gauss.csv'))
CombinedAnalysis = pd.read_csv(os.path.join(M1_Output, 'CombinedAnalysis.csv'))
lipid_data = pd.read_csv(os.path.join(currentpath, 'lipid_data.csv'), header = None).set_index(0)[1].to_dict()


# Grab isomer names
isomer1_name = lipid_data['isomer1']
isomer2_name = lipid_data['isomer2']


# Grab basic sphingolipid identification info from input files
backbone = pd.unique(CombinedAnalysis['sphingoidBackbone'])
backbone = ''.join(backbone)

titleisomer1Sph = isomer1_name + 'Sph(' + backbone + ')'
titleisomer2Sph = isomer2_name + 'Sph(' + backbone + ')'

# Grab the Lipid List and turn to a list
Trainlist_Lipids = list(pd.unique(CombinedAnalysis['lipidSpecies']))

# Output the number of unique lipid from this dataset
n_TrainLipids = len(Trainlist_Lipids)

# Talk to users
print("There are ", n_TrainLipids, "unique pairs of lipid isomers in your dataset." )
print("All of these pairs of lipid isomers will be used for training dataset.")

# Select excel file listing lipids to be predicted for.
## Files are read and stored as DataFrame.
msg_to_users(messagebox.showinfo, "Message to user.", "In the next window, please choose the .csv file listing Lipids to be predicted for.")
InputFile2 = msg_to_users(filedialog.askopenfile,
                                   mode = 'rb',
                                   title = "Please choose Predicted Lipids file.")
if InputFile2 != None:
    Predlist_Lipids = pd.read_csv(InputFile2) # Save as dataframe

# Turn the only column in dataframe to list

Predlist_Lipids = Predlist_Lipids.iloc[:,0].to_list()


# ## STEP 2: Set up the files and seeding
# 
# Create Input DataSet from Trainlist_Lipids and Predlist_Lipids. This step will create excel sheets of TrainingSet and PredictionSet, of lipids to be predicted for defined by user above, and information associated to them obtained from files generated from Module 1.

# In[ ]:


# Create TrainingSet dataframe and TrainingSet.xlsx
TrainingSet = []
for i in range(len(Trainlist_Lipids)):
    temp_TrainingSet = CombinedAnalysis.loc[CombinedAnalysis['lipidSpecies']==Trainlist_Lipids[i]]
    TrainingSet.append(temp_TrainingSet)
TrainingSet = pd.concat(TrainingSet)
TrainingSet.reset_index(drop = True, inplace = True)


if_na = TrainingSet["mu_" + isomer1_name].isnull().values.any() or TrainingSet["mu_" + isomer2_name].isnull().values.any()
total_na = (TrainingSet["mu_" + isomer1_name].isnull().sum().sum()) + (TrainingSet["mu_" + isomer2_name].isnull().sum().sum())

if if_na == True:
    print("You have NA for CoV values in your dataset. There are ", total_na, " instances of NA values.")
    print("At the SV where there are NAs for CoV values of either " + isomer1_name + " or" + isomer2_name + " isomer, the entire SV will be removed for that pair of lipid isomers.")
    print("TrainingSet is now generated without any NAs.")
    TrainingSet.dropna(subset = ["mu_" + isomer1_name], inplace = True)
    TrainingSet.dropna(subset = ["mu_" + isomer2_name], inplace = True)
    TrainingSet.reset_index(drop = True, inplace = True)

TrainingSet.to_csv('Module2_Outputs/TrainingSet.csv', index=None)

# Create PredictionSet dataframe and PredictionSet.xlsx. The lipids here were specified by users as Predlist_Lipids. The columns are
# empty and will be occupied with predicted value after running through the neural net.

PredictionSet = pd.DataFrame()                                                      
for lipid in range(len(Predlist_Lipids)):
    temp_PredictionSet = pd.DataFrame({'lipidSpecies' : Predlist_Lipids[lipid],
                                       'SV' : meanAllsigma['SV'],
                                       'chainLength' : ((Predlist_Lipids[lipid]).split(':'))[0],
                                       'unsaturationUnit' : ((Predlist_Lipids[lipid]).split(':'))[1]
                                       })  
    PredictionSet = pd.concat([PredictionSet, temp_PredictionSet])

PredictionSet['mu_' + isomer1_name]  = ''
PredictionSet['mu_' + isomer2_name]  = ''
PredictionSet['sigma_' + isomer1_name]  = ''
PredictionSet['sigma_' + isomer2_name]  = ''
PredictionSet.reset_index(drop = True, inplace = True)

# ## STEP 3. Standardize training dataset and set up hyperparameters
# 
# Training Dataset will be standardized for lipid features by performing z-scoring. Lipid features are lipids' chain length and degree of unsaturation.
# Hyperparameters for the neural network are defined here based on previous optimization work. Hyperparameters may be changed by users if wished to, to test out other parameters applicable to neural networks.

# In[ ]:


# i. Set up the Trainining files and standardize training data input
(nInstances, nCols) = TrainingSet.shape
LipidFeatures = {'chainLength', 'unsaturationUnit'}
nLipidFeatures= len(LipidFeatures)
LipidIsomers = {isomer1_name, isomer2_name}
nLipidIsomers = len(LipidIsomers)

## Set up file for X and Y variables of training dataset
TrainX = np.zeros(shape=(nInstances, nLipidFeatures+1))
TrainY = np.zeros(shape=(nInstances, 2))

for i in range(nInstances):
    Temp = TrainingSet.loc[i,'lipidSpecies']
    Temp2 = Temp.split(':')
    
    for j in range(nLipidFeatures):
        TrainX[i, j] = float(Temp2[j])
        
    TrainX[i, nLipidFeatures] = TrainingSet.loc[i,'SV']
    TrainY[i, 0] = TrainingSet.loc[i, 'mu_' + isomer1_name]
    TrainY[i, 1] = TrainingSet.loc[i, 'mu_' + isomer2_name]

## Standardize lipid features by z-scoring
FeatureMeans = np.mean(TrainX, axis=0)
FeatureSD = np.std(TrainX, axis=0)
for i in range(nLipidFeatures+1):
    TrainX[:,i] = TrainX[:,i]-FeatureMeans[i]
    TrainX[:,i] = TrainX[:,i]/FeatureSD[i]
    
TrainX_rounded = np.round(TrainX, decimals=3)
TrainY_rounded = np.round(TrainY, decimals=3)

# ii. Set up Prediction file and standardize input data required for prediction
(nPredInstances, nCols) = PredictionSet.shape
PredX = np.zeros(shape=(nPredInstances, nLipidFeatures+1))

for i in range(nPredInstances):
    Temp = PredictionSet.loc[i,'lipidSpecies']
    Temp2 = Temp.split(':')
    
    for j in range(nLipidFeatures):
        PredX[i, j] = float(Temp2[j])
        PredX[i, nLipidFeatures] = PredictionSet.loc[i,'SV']      
    
## Standardize lipid features by z-scoring
for i in range(nLipidFeatures+1):
    PredX[:,i] = PredX[:,i]-FeatureMeans[i]
    PredX[:,i] = PredX[:,i]/FeatureSD[i]

PredX_rounded = np.round(PredX, decimals=3)

# iii. Hyperparameter Setup. Users can change if wished but iDMS work has shown that the followings are the most optimal parameters. 
Initializer_name = 'glorot_uniform'           
Initializer = keras.initializers.glorot_uniform(seed=42)
HiddenLayers = 5
InnerActivation = 'softplus'
OuterActivation = 'linear'
LossFunction = 'MAE'
StopLoss = 1E-10

print("The optimal network used here has " +str(HiddenLayers)+ " layers, with " +InnerActivation+ " as activation function for all layers, " 
      +LossFunction+ " or 'mean absolute error' as the loss function, initialized weights basd on the " +Initializer_name+ 
      " method, and an early stopping loss of 1E-10 " )

parameters = Initializer_name + "_" + str(HiddenLayers) + "_" + InnerActivation + "_" + OuterActivation + "_" + LossFunction

# iv. Define the EarlyStopping callback
early_stopping = EarlyStopping(
    monitor = 'loss',
    min_delta = StopLoss,
    patience = 50, 
    verbose = 0,
    mode = "min"
    )

# ## STEP 4. Model Initialization
# 
# Creating a neural network model based on the optimal hyperparameters

# In[ ]:


# Define the number of units in each hidden layer. This has been optimized and determined to be 10.
nUnitsPerHiddenLayer = 10

# Create the model
ourModel = models.Sequential()

# Add the hidden layers. The first layer input are lipid features (acyl chain, # of unsaturation) and SV.
ourModel.add(layers.Dense(units = nUnitsPerHiddenLayer, kernel_initializer = Initializer, input_dim = nLipidFeatures+1, 
                          activation = InnerActivation))

# Remaining hidden layers are similar, but have NUnitsPerHiddenLayer input dimension
for i in range(HiddenLayers-1):
    ourModel.add(layers.Dense(units = nUnitsPerHiddenLayer, kernel_initializer = Initializer, input_dim = nUnitsPerHiddenLayer, 
                              activation = InnerActivation))

# Create Output layer with two output units (isomer2_name Peak CoV(or isomer2_name_mu), and isomer1_name Peak CoV(or isomer1_name_mu))
ourModel.add(layers.Dense(units = 2, kernel_initializer = Initializer, input_dim = nUnitsPerHiddenLayer, 
                          activation = OuterActivation))

# Add loss function and optimizer to our model
ourModel.compile(optimizer='adam', loss=LossFunction, metrics=['accuracy'])

# Train our model on the training dataset
history = ourModel.fit(TrainX_rounded, 
                       TrainY_rounded, 
                       epochs=2000, 
                       callbacks = [early_stopping], 
                       verbose = 2,
                       shuffle = False)

# ## STEP 5. Prediction
# 
# This code block calculates predictions for the PredictionInputs and outputs them to file PredictionSet

# In[ ]:


# Make the predictions
PredY = ourModel.predict(PredX_rounded)

# Insert into dataframe
PredictionSet.loc[:,'mu_' + isomer1_name] = PredY[:,0]
PredictionSet['mu_' + isomer1_name] = (PredictionSet['mu_' + isomer1_name].astype(float)).round(3)

PredictionSet.loc[:,'mu_' + isomer2_name] = PredY[:,1]
PredictionSet['mu_' + isomer2_name] = (PredictionSet['mu_' + isomer2_name].astype(float)).round(3)

# Evaluate the model. Score output is [the loss (MAE), accuracy]
score = ourModel.evaluate(TrainX_rounded, TrainY_rounded, verbose =0)

#  ## STEP 6. From predicted value, apply Gaussian functions, predict separation and construct confusion matrix

# In[ ]:


# Add sigma values from mean sigma sheet
minSV = meanAllsigma['SV'].min()
maxSV = meanAllsigma['SV'].max()
stepSV = int((maxSV - minSV) / ((meanAllsigma['SV'].nunique())-1))

# Create a dictionary of the mean sigmas
isomer1_meanSigma = meanAllsigma['sigma_'+ isomer1_name].values
isomer2_meanSigma = meanAllsigma['sigma_'+ isomer2_name].values

isomer1_name_sigma_dict = pd.Series(isomer1_meanSigma, index = meanAllsigma.SV).to_dict()
isomer2_name_sigma_dict = pd.Series(isomer2_meanSigma, index = meanAllsigma.SV).to_dict()

# Combine
PredictionSet["sigma_" + isomer1_name] = PredictionSet["SV"].map(isomer1_name_sigma_dict)
PredictionSet["sigma_" + isomer2_name] = PredictionSet["SV"].map(isomer2_name_sigma_dict)

# Apply Gaussian functions
## Copy dataframe from PredictionSet and add a new column for climax intensity
Gauss_PredictionSet = PredictionSet.copy()

# Predict Intersection Point by Sigma and Gaussian
pred_Intersected_gauss = pd.DataFrame()

def gaussian(x, mu, sigma):
   y = 1 * exp(-0.5*((x-mu)/sigma)**2)  #Y=Amplitude*exp(-0.5*((X-Mean)/SD)^2)
   return y

def solve(mu_isomer1,mu_isomer2,sig_isomer1,sig_isomer2): 
  a = 1/(2*sig_isomer1**2) - 1/(2*sig_isomer2**2)
  b = mu_isomer2/(sig_isomer2**2) - mu_isomer1/(sig_isomer1**2)
  c = mu_isomer1**2 /(2*sig_isomer1**2) - mu_isomer2**2 / (2*sig_isomer2**2) - np.log(sig_isomer2/sig_isomer1)
  return np.roots([a,b,c])

for i in range(len(Predlist_Lipids)):
    pred_intersect_temp = (Gauss_PredictionSet[Gauss_PredictionSet['lipidSpecies']==Predlist_Lipids[i]])   
    titleisomer1Cer = isomer1_name + 'Cer(' + backbone + '/' + str(Predlist_Lipids[i]) + ')'
    titleisomer2Cer = isomer2_name + 'Cer(' + backbone + '/' + str(Predlist_Lipids[i]) + ')'
    
    listSV = (pred_intersect_temp['SV'].unique()).tolist()
    listSV.sort() 
    
    for SV in listSV:
        pred_intersectSV_temp = pred_intersect_temp[pred_intersect_temp['SV']==SV]
        
        if pred_intersectSV_temp["mu_" + isomer1_name].notna() is False:
            continue
        else:
            mu_isomer1 = pred_intersectSV_temp["mu_" + isomer1_name]
            mu_isomer1 = round(mu_isomer1.iloc[0],3)
            sig_isomer1 = pred_intersectSV_temp["sigma_" + isomer1_name]
            sig_isomer1 = sig_isomer1.iloc[0]
        
        if pred_intersectSV_temp["mu_" + isomer2_name].notna() is False:
            continue
        else:
            mu_isomer2 = pred_intersectSV_temp["mu_" + isomer2_name]
            mu_isomer2 = round(mu_isomer2.iloc[0],3)
            sig_isomer2 = pred_intersectSV_temp["sigma_" + isomer2_name]
            sig_isomer2 = sig_isomer2.iloc[0]
        
        pred_gauss_features = [mu_isomer1, mu_isomer2, sig_isomer1, sig_isomer2] 
     
        if any(pd.isna(pred_gauss_features)) is True:
            continue
        else:
            pred_resultCombined = solve(mu_isomer1, mu_isomer2, sig_isomer1, sig_isomer2)
        
        
        x = np.linspace(-10,10,10000)
        y_isomer1_pred = gaussian(x, mu_isomer1, sig_isomer1)
        y_isomer2_pred = gaussian(x, mu_isomer2, sig_isomer2)
        
        # Intersection point is limited to only that lies between mu of isomer1 and isomer2
        mu_range_max = max(mu_isomer1, mu_isomer2)
        mu_range_min = min(mu_isomer1, mu_isomer2)
        
        pred_intersect = max([point for point in pred_resultCombined if mu_range_min < point < mu_range_max], default = None)
        
        if pred_intersect is None:
            y_at_intersect = pred_intersect            
        else:
            pred_intersect = round(pred_intersect,3)
            y_at_intersect = round(gaussian(pred_intersect, mu_isomer1, sig_isomer1),3)
          
        if pred_intersect != None and (y_at_intersect < 0.5 ):
           pred_intersectSV_temp["Valley CoV"] = pred_intersect
        else:
            pred_intersectSV_temp["Valley CoV"] = None
        
        pred_intersectSV_temp["Intersection point"] = pred_intersect
        pred_intersectSV_temp["Norm Intensity at Intersection"] = y_at_intersect
         
          
        fig,ax = plt.subplots()
        #ax.set_xlim([-10, 10])
        
        plt.ylabel('Normalized  Intensity', fontsize = 12)
        plt.xlabel('CoV at SV ' + str(SV) + ' V', fontsize = 12)
        plot1 = ax.plot(x, y_isomer1_pred, color='green', label= isomer1_name + ' Gaussian Model')
        plot2 = ax.plot(x, y_isomer2_pred, color='blue', label= isomer2_name + 'Gaussian Model')

        if pred_intersect != None:
          plot3 = ax.plot(pred_intersect, y_at_intersect, 'ro', fillstyle='full', label = 'Intersection point')
          
        if (Predlist_Lipids[i] == '0:0'):
            plot_title = "Separability of " + titleisomer1Sph + " and " + titleisomer2Sph
        else:
            plot_title = "Separability of " + titleisomer1Cer + " and " + titleisomer2Cer   
        plt.title(plot_title)
         
        ax.legend(loc='best')
        temp_plot = plt.gcf()
        plt.draw()
        
        plotname = 'Separability' + isomer1_name + str(Predlist_Lipids[i]) + '_' + isomer2_name + str(Predlist_Lipids[i]) + '_SV' + str(SV)
        plotname = plotname.replace(":","-")
        plotpath = os.path.join(currentpath, 'Module2_Outputs/PredictedSetPlots',plotname)
        temp_plot.savefig(plotpath)
        plt.close()           
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category = FutureWarning)
            pred_Intersected_gauss = pd.concat([pred_Intersected_gauss, pred_intersectSV_temp])
        
        pred_Intersected_gauss.reset_index(drop = True, inplace = True)
        plt.close()

plt.close()

pred_Intersected_gauss["lipidSpecies"] = pred_Intersected_gauss['chainLength'].astype(str) + ':' + pred_Intersected_gauss['unsaturationUnit'].astype(str)

# Binary Separation Column

pred_Intersected_gauss['Sep or InSep'] = np.where(pred_Intersected_gauss['Valley CoV'].isnull(), "Inseparable", "Separable")

        
# Output intersection point to files
pred_Intersected_gauss = pred_Intersected_gauss.replace('NAN','')
pred_Intersected_gauss.to_csv('Module2_Outputs/PredictionResult.csv', index=None)

# Output Model Information
iDMS_params = history.params

# Convert Model Information Dictionary to CSV
iDMS_params_csv = f'{M2_top}/iDMS_params.csv'

with open(iDMS_params_csv, mode = 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(iDMS_params.keys())
    writer.writerow(iDMS_params.values())

iDMS_training_history = pd.DataFrame({
    'loss': history.history['loss'],
    'accuracy': history.history['accuracy']
    })

iDMS_training_history.to_csv(f'{M2_top}/iDMS_training_history.csv', index=None)


# In[ ]:

print("Module 2 of iDMS has finished. You can find all output files and plots in the folder directory you selected in the beginning. Have a nice day.")
msg_to_users(messagebox.showinfo,"Message to user.", "Module 2 of iDMS has finished. You can find all output files and plots in the folder directory you selected in the beginning. Live well and prosper.")


