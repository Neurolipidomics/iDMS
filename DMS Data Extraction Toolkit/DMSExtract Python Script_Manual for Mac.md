## Install Python 3.12.10
- Click [here](https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg) to download Python 3.12.10 for Mac (64x).
- Once downloaded, install on your computer.

## Create a virtual environment
- On Mac, start Terminal.
- In Terminal, create a project folder for the project you are working on. For example, create project folder 'iDMS' on 'Desktop' with the following commands:
  - Navigate to folder Desktop on your computer: `cd  Desktop`
  - Make new folder called "iDMS": `mkdir iDMS`
  - Enter folder "iDMS": `cd iDMS`
  - Check current active Python version on computer: `python3 --version`
 
- From folder "DMS Data Extraction Toolkit" of github, download:
  - *requirements.txt*
  - Either: "From .jdx"/*DMSDataExtractionToolkit_fromJDX.py* or "From .mzml"/*DMSDataExtractionToolkit_fromMZML.py*
  - *DataInfo.csv*

- Place them all in folder "iDMS" just made above.

### *(If you have already had a virtual environment, you can skip this step and move to the next step to "Activate" virtual environment.)*
- Create a virtual environment with Python 3.12.10:\
  `python3.12 -m venv py3-12-10`

- Activate the virtual environment just created:\
  `source py3-12-10/bin/activate`

Your command line will now appear with the virtual environment name at the front, enclosed in a pair of round brackets:\
`((py3-12-10)) Neurolipidomics@User iDMS %`

- Install required packages and libraries for iDMS from *requirements.txt*
  - On an Apple-chip MAC, type: `cat requirements.txt | xargs -n 1 pip install`
  - On an Intel-chip MAC, type: `while read requirement; do pip install "$requirement" || true; done < requirements.txt`

## Fill in *DataInfo_template.csv* with information related to your data
- There are 4 columns: "Data Folder Directory", "isomer", "sphingoidBackbone", "chainLength", "unsaturationUnit"
- Sample information associated to experimental data files is populated in these columns.
- Note that information in column "Data Folder Directory" must contain the full path.
  - In order to obtain full path for your data folder, select the folder containing individual experimental .jdx or .mzml files of each isomeric lipid species (for example, folder for GlcCer(d18:1/20:0)), and press `Option + Command + C`, then paste into column "Data Folder Directory" in DataInfo.csv.
- Data entered in columns "isomer" and "sphingoidBackbone" must be text (string), while data entered in columns "chainLength" and "unsaturationUnit" must be numeric.

## Execute DMS Data Extraction Toolkit python script
- - In the same Terminal window, execute:\
  `python3 DMSDataExtractionToolkit_fromJDX.py` or `python3 DMSDataExtractionToolkit_fromMZML.py`
- Follow the instruction in pop-up windows when prompted.

> [!IMPORTANT]
> User must process **1** isomer at a time.
> User can use the same DataInfo.csv containing information of both isomers; however, the data folder must only contain experimental data files of 1 isomer.

## Deactivate virtual environment
- On Terminal, type: `deactivate`
- Type to close Terminal: `exit`
- Press: `Command + Q`
