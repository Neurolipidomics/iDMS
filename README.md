# iDMS
iDMS is an in silico supervised neural network model that learns the field asymmetric (differential) ion mobility spectrometry (FAIMS/DMS) relationships between separation voltage (SV), compensation voltage (CoV) and the monoglycosphingolipid structural features of sugar headgroup, _N_-acyl chain length, and _N_-acyl degree of unsaturation. 
iDMS predicts the SV and CoV combinations capable of resolving any monoglycoceramide stereoisomer pair and can be trained using a dataset composed of empirically determined signal intensities for 12 or more stereoisomers (6 or more pairs of epimers) measured across a range of SVs and CoVs. It is recommended to acquire the training dataset using a CoV ramp step of 0.2 V.

# Setup
iDMS is implemented in two modules executed as two separate Python scripts using a Python IDE or from two Jupyter notebooks. Please install Python 3.12.10, which is the last version of Python 3.12 maintained with security. [Download Python](https://www.python.org/downloads/release/python-31210/) for your operating system.  All packages and libraries will be installed once the modules are executed.

To execute iDMS successfully, manuals are provided for the installation of Python or JupyterLab, setting up virtual environment, and installation of the required libraries and packages on both Mac and Windows operating systems. Assembly module scripts and Jupyter notebooks that automate the preprocessing of measured signal intensities from .wiff or other proprietary format after conversion to .jdx or .mzml format to accelerate user generation of their training datasets can be found [here](https://github.com/neurolipidomics/DMSDataExtractionToolkit).


# Quick Start
Sample training dataset files are provided for a quick start of running iDMS.  These files also serve as templates for users to modify in the generation of their own platform-specific training datasets. A .csv file is provided for each set of Glycosphingolipid isomers: GalactosylCeramides (as isomer 1) and GlucosylCeramides (as isomer 2) with varying *N*-acyl chain lengths and either zero or one unit of unsaturation.  Sample data were obtained from experiments performed on a using a SCIEX SelexION® differential ion mobility device interfaced to a QTRAP 5500 triple quadrupole-linear ion trap mass spectrometer. 

Please use these two files when testing Module 1_Parametric Modelling.

For Module 2_iDMS, users input a list of lipids for which they wish to predict resolving SV and CoV paramaters. Please use the provided file **Prediction_template.csv** to enter the identity of the lipids of interest. Identities must be entered in this format **chainlength:unsaturationUnit**. For example, if a user wishes to predict the SV and CoV that resolve the glycosphingolipid isomers Glc/GalCer(d18:1/15:1), they should enter 15:1. 

NOTE: Please edit the file **Prediction_template.csv** using a text editor such as Notepad (on a Windows) or TextEdit (on a MAC) and NOT in Microsoft Excel as the proprietary software will alter the format of the prediction list such that it will not function in iDMS.

# Bug Report
For bug report, please contact Dr. Steffany Bennett and Thao Nguyen-Tran at ldomic@uottawa.ca. Please also send an example dataset which did not run successfully on iDMS.

# Citing
Nguyen-Tran, T., Shi, XX., Hashimoto-Roth, E., Organ, M.G., Lavallée-Adam, M., Perkins, T. J. & Bennett, S.A.L. (2026). Intelligent differential ion mobility spectrometry (iDMS) for lipidomics: A machine learning algorithm that predicts the optimal space -resolved ion mobility parameters for isomeric glycosphingolipids. [bioRxiv:2026.2008.2026.747394](https://www.biorxiv.org/content/10.64898/2026.08.26.747394v1) . 

This repository is linked to [zenodo](https://zenodo.org/records/22214408), where you can find a DOI for the version you are using.
