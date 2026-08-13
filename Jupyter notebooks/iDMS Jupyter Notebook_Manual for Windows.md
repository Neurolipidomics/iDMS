## Install Python 3.12.10
- Click [here](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe) to download Python 3.12.10 for Windows (64x):
- Once downloaded, install on your computer.

## Install JupyterLab as a terminal-launched application
- On Windows, start Command Prompt by searching for 'cmd'.

>[!NOTE]
>DO NOT CLOSE Command Prompt window until you have finished using iDMS.
  
- Type: `pip install jupyterlab`

## Create a virtual environment

- In Command Prompt, create a project folder. For example, create project folder 'iDMS' on 'Documents' with the following commands:
  - Navigate to folder Documents on your computer: `cd  Documents`
  - Make new folder called "iDMS": `mkdir "iDMS"`
  - Enter folder "iDMS": `cd iDMS`

- Download ALL files in the github folder "Jupyter notebooks", including file in subfolders "Prediction template" and "Training dataset template". Place ALL files/folders in  your "iDMS" project folder.

### *(If you have already established a virtual environment, you can skip this step and move to "Activate" virtual environment.)*
- Create a virtual environment with Python 3.12.10:\
  `py -3.12 -m venv py3-12-10`

- Activate the virtual environment just created:\
  `py3-12-10\Scripts\activate`

Your command line will now appear with the virtual environment name at the front, enclosed by a pair of round brackets:\
`(py3-12-10) C:\Users\neuro\Documents\iDMS>`

- Install required packages and libraries for iDMS from *requirements.txt* (Please use the requirements.txt downloaded from iDMS/Jupyter notebooks):
  `for /F "tokens=*" %i in (requirements.txt) do pip install %i`

- Install ipykernel, create kernel for Python 3.12.10 in Jupyter Lab:\
  `pip install ipykernel
  python -m ipykernel install --user --name=py3-12-10 --display-name="Python 3.12.10"`

- Start Jupyter lab:\
  `jupyter lab`
  
If you have multiple kernels set up for Jupyter lab on your computer, you will be prompted to select the kernel to start. Make sure you select kernel "Python 3.12.10".


## Execute Module 1 of iDMS
- A web browser will open with the Jupyter Lab interface. On the left hand-side, the display will show the directory you currently are in. This directory display is\
similar to what you see in a regular Windows Explorer interface. Navigate to where the iDMS Jupyter Notebooks are stored.
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
- Close the JupyterLab browswer.

## Deactivate virtual environment
- On Command Prompt, type: `deactivate`
- Type to close command prompt: `exit`


