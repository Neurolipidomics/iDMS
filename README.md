# iDMS
iDMS is an algorithm designed to predict instrumental parameter on a Differential Mobility Spectrometer that are required to separate a pair of monoglycosphingolipid epimers. The predicted instrumental parameter is Compensation Voltage (CoV) at any specified Separation Voltage (SV). The algorithm requires inputs of features associated to the lipid structure and the SV to be predicted for.

# Setup

## Installation
iDMS contains two modules, written in Python and can be executed as a Python script using a Pythin IDE, or from the provided Jupyter Notebook. iDMS requires python version 3.12.7. All packages and libraries required will be installed once the modules are executed.

Users advised to create a folder containing both modules of iDMS as well as the required input files. Templates for input files are provided below with guidance steps.

### Setup JupyterLab
Below will describe two ways to install Jupyter, either as a terminal-launched application, or as a desktop application. While users who are more fluent with package management system may opt for the first option, JupyerLab Desktop as a desktop application may be more straight-forward for other users.

A) JupyterLab as Terminal-launched application

**conda**
```
conda install -c conda-forge jupyterlab
```
**mamba**
```
mamba install -c conda-forge jupyterlab
```
**pip**
```
pip install jupyterlab
```


B) JupyterLab Desktop
Based on your operating system, click on the appropriate option to install JupyterLab Desktop.

| Windows (10, 11) |	Mac (macOS 10.15+) |	Linux |
| ---------------- | ------------------- | ------ |
| [x64 Installer](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-Windows-x64.exe) |	[arm64 Installer (Apple silicon)](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-macOS-arm64.dmg) 	| [Snap Store [recommended]](https://snapcraft.io/jupyterlab-desktop) |
| | [x64 Installer (Intel chip)](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-macOS-x64.dmg) | [.deb x64 Installer (Debian, Ubuntu)](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-Debian-x64.deb)  |
| | | [.rpm x64 Installer (Red Hat, Fedora, SUSE)](https://github.com/jupyterlab/jupyterlab-desktop/releases/latest/download/JupyterLab-Setup-Fedora-x64.rpm) |

### Working Folder

The code embedded within iDMS will make whatever folder the code is in its working directory. Therefore, please make sure that in this folder, the following files and documents are present:

- Module1.ipynb
- Module3.ipynb
- b-GalCers_iDMS_InputTemplate.xlsx
- b-GlcCers_iDMS_InputTemplate.xlsx
- Predlist_Lipids.xlsx

If opening the Jupyter notebooks in JupyterLab Desktop, users only need to double click on the module notebook to open it in the application.

If opening the Jupyter notebooks from Terminal, users first need to start JupyterLab using a terminal. 

**Command Prompt on Windows** or **Terminal on macOS/Linux**
```
jupyter lab
```

JupyterLab will open its local server on a web browser. On the web browser, navigate to your working folder and start iDMS module notebooks. Leave the terminal window opens throughout the entire time using iDMS.

# Bug Report:
For bug report, please contact Dr. Steffany Bennett at SteffanyAnn.Bennett@uottawa.ca and Thao Nguyen-Tran at tnguy224@uottawa.ca. Please also send an example dataset which did not run successfully on iDMS.

# Citing
Nguyen-Tran, T., Shi, XX., Taylor, G.P., Lavallée-Adam, M., Perkins, T. J. & Bennett, S.A.L. (2025). Intelligent differential ion mobility spectrometry (iDMS) for lipidomics: A machine learning algorithm that predicts the optimal space -resolved ion mobility parameters for isomeric glycosphingolipids 

