## Install Python 3.12.10
- Click here to download Python 3.12.10 for Windows (64x) [https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe]
- Once downloaded, install on your computer.

## Create a virtual environment
- On Windows, start Command Prompt by searching for 'cmd'.

- Create a project folder for the project you are working on. For example, create project folder 'iDMS' on 'Documents' with the following commands:\
  - Navigate to folder Desktop on your computer: `cd  Documents`
  - Make new folder called "iDMS": `mkdir "iDMS"`
  - Enter folder "iDMS": `cd iDMS`
  - Check current active Python version on computer: `python --version`

- Create a virtual environment with Python 3.12.10:\
  `py -3.12 -m venv py3-12-10`

- Activate the virtual environment just created:\
  `py3-12-10\Scripts\activate`

Your command line will now appear with the virtual environment name at the front, enclosed in a pair of round brackets:\
`(py3-12-10) C:\Users\neuro\Documents\iDMS>`

- Install required packages and libraries for iDMS from *requirements.txt* "\
  `for /F "tokens=*" %i in (requirements.txt) do pip install %i`

## Execute Module 1 of iDMS
- In the same Command Prompt window, execute:\
  `python Module 1_Parametric Modelling.py`
- Follow the instruction in pop-up windows when prompted.
  
Once finished, moved on to Module 2.

## Execute Module 2 of iDMS
- In the same Command Prompt window, execute:\
  `python Module 2_iDMS.py`
- Follow the instruction in pop-up windows when prompted.  
