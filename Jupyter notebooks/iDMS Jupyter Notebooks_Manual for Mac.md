## Install Python 3.12.10
- Click [here](https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg) to download Python 3.12.10 for Mac (64x).
- Once downloaded, install on your computer.

## Install JupyterLab as a terminal-launched application
- On Mac, start Terminal.

>[!NOTE]
>DO NOT CLOSE Terminal window until you have finished using iDMS.
  
- Type: `pip3 install jupyterlab`

## Create a virtual environment

- In Terminal, create the project. For example, create the project folder 'iDMS' on 'Desktop' with the following commands:
  - Navigate to folder Desktop on your computer: `cd  Desktop`
  - Make new folder called "iDMS": `mkdir iDMS`
  - Enter folder "iDMS": `cd iDMS`
  - Check current active Python version on computer: `python3 --version`
 
- Download ALL files in the github folder "Jupyter notebooks", including files in the subfolders "Prediction template" and "Training dataset template". Place ALL files/folders in  your "iDMS" project folder. 

### *(If you have already established a virtual environment, you can skip this step and move to the next step to "Activate" virtual environment.)*
- Create a virtual environment with Python 3.12.10:\
  `python3.12 -m venv py3-12-10`

- Activate the virtual environment just created:\
  `source py3-12-10/bin/activate`

Your command line will now appear with the virtual environment name at the front, enclosed in a pair of round brackets:\
`((py3-12-10)) Neurolipidomics@User iDMS %`

- Install required packages and libraries for iDMS from *requirements.txt* (Please use the requirements.txt downloaded from iDMS/Jupyter notebooks):
  - On an Apple-chip MAC, type: `cat requirements.txt | xargs -n 1 pip3 install`
  - On an Intel-chop MAC, type: `while read requirement; do pip3 install "$requirement" || true; done < requirements.txt`

- Install ipykernel, create kernel for Python 3.12.10 in Jupyter Lab:\
  `pip3 install ipykernel`
  `python3 -m ipykernel install --user --name=py3-12-10 --display-name="Python 3.12.10"`

- Start Jupyter lab:\
  `jupyter lab`

If you have multiple kernels set up for jupyter lab on your computer, you will be prompted to select the kernel to start. Make sure you select kernel "Python 3.12.10".

## Execute Module 1 of iDMS
- A web browser will open with the Jupyter Lab interface. On the left hand-side, the display will show your current directory. This directory display is similar to what you see in a regular Windows Explorer interface. Navigate to where the iDMS Jupyter Notebooks are stored.
- Choose to open: **Module 1_Parametric Modelling Module.ipynb**
- Execute the notebook by running each cell, one at a time.  
- Follow the instruction in pop-up windows when prompted.
>[!CAUTION]
>Once finished, user must select: Kernel > Restart Kernel and Clear Outputs of All Cells...\
>Then, save the notebook by: File > Save
- Close Module 1 notebook and move onto Module 2.

## Execute Module 2 of iDMS
- Open: **Module 2_iDMS.ipynb**
- Execute the notebook by running all cells at once. Go to: Run > Restart Kernel and Run All

>[!CAUTION]
>Once finished, user must select: Kernel > Restart Kernel and Clear Outputs of All Cells...\
>Then, save the notebook by: File > Save
- Close Module 2 notebook.
- To close the JupyterLab web browser, go to File > Shut down.
- Select "Shut Down" when prompted for confirmation.
- Close the JupyterLab browser.

## Deactivate virtual environment
- On Terminal, type: `deactivate`
- Type to close command prompt: `exit`
- Press: `command + Q`

