# TPDLAccessibilityofGovernmentDocuments

This repository contains the data and notebooks for the Short paper submission 'Making PDFs accessible for Visually Impaired Users (and Everybody Else)' to the TPDL conference.

## Installation

To be able to run the code and experiments in this repository, follow these steps:

1. Install Anaconda: 

   - Visit the [Anaconda website](https://www.anaconda.com/products/individual) and download the installer for your operating system.
   - Follow the installation instructions provided for your specific OS.

2. Clone this repository:
```
git clone https://github.com/RubenvanHeusden/TPDLAccessibilityofGovernmentDocuments.git
```
3. Navigate to the project directory:
```
cd TPDLAccessibilityofGovernmentDocuments
```
4. Create a new Anaconda environment:

   Open a terminal (or Anaconda Prompt on Windows) and run the following command, which installs the requirement according to the environment file we provid:
   ```
   conda env create -f environment.yml
   ```
   
5. Activate the environment:
  ```
  conda activate pdf_accessibility_env
  ```
6. Alternative using pip
   If you prefer using pip, you can also install the environment using the requirements file we supplied
   ```
   pip install - requirements.txt
   ```
7. Running Jupyter Notebook:
   If you haven't worked with Jupyter Notebook yet, you should set up jupyter so that you can select the right kernel and work with the packages we just installed.
   ```
   ipython kernel install --name "pdf_accessibility_env" --user
   ```
   
## Directory Structure

- `notebooks/`: Contains Jupyter Notebook files.
    - `Experiments.ipynb`: Notebook containing the main experiments and explanation of the algorithm. 
- `datasets/`: Contains source code files.
    - `data.csv`: Contains the data with the labels of the different pages
    - `images`: contains the PNG images of the pages.
    - `gold_standard-json`: Contains the json file of the manual annotations from the research.
