## Install Python 3.12.10
- Click [here](https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg) to download Python 3.12.10 for Mac (64x).
- Once downloaded, install on your computer.

## Create a virtual environment
- On Mac, start Terminal.

>[!NOTE]
>DO NOT CLOSE Terminal until you finish with iDMS. 

- Create a project folder for the project you are working on. For example, create project folder 'iDMS' on 'Desktop' with the following commands:
  - Navigate to folder Desktop on your computer: `cd  Desktop`
  - Make new folder called "iDMS": `mkdir iDMS`
  - Enter folder "iDMS": `cd iDMS`
  - Check current active Python version on computer: `python3 --version`
 
- Download all files in folders "Python scripts", "Training dataset template", "Prediction template" and store them in the "iDMS" project folder.

### *(If you have already had a virtual environment, you can skip this step and move to the next step to "Activate" virtual environment.)*
- Create a virtual environment with Python 3.12.10:\
  `python3.12 -m venv py3-12-10`

- Activate the virtual environment just created:\
  `source py3-12-10/bin/activate`

Your command line will now appear with the virtual environment name at the front, enclosed in a pair of round brackets, similar to below:\
`((py3-12-10)) Neurolipidomics@User iDMS %`

- Install required packages and libraries for iDMS from *requirements.txt* (Please use the requirements.txt downloaded from iDMS/Python scripts):\
  `cat requirements.txt | xargs -n 1 pip install`

## Execute Module 1 of iDMS
- In the same Command Prompt window, execute:\
  `python3 Module 1_Parametric Modelling.py`
- Follow the instruction in pop-up windows when prompted.
  
Once finished, moved on to Module 2.

## Execute Module 2 of iDMS
- In the same Command Prompt window, execute:\
  `python3 Module 2_iDMS.py`
- Follow the instruction in pop-up windows when prompted.  

## Deactivate virtual environment
- On Command Prompt, type: `deactivate`
- Type to close command prompt: `exit`
- Press: `Command + Q`
