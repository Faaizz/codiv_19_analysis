# Imports
import os, subprocess, json

# Environmental Variables
from dotenv import load_dotenv

import pandas as pd

# HTTP Client
import requests

# For parsing and sifting through HTML
from bs4 import BeautifulSoup


# Load environmental variables specified in .env
load_dotenv()


def get_johns_hopkings():
    """ Update data from Johns Hopkings (GITHUB)
    
    Parameters:
    ----------

    Returns:
    -------
    """

    # GIT CLONE
    if(not os.path.exists("data/raw")):
        os.mkdir("data/raw")

    if(not os.path.exists("data/processed")):
        os.mkdir("data/processed")

    if(not os.path.exists("data/raw/JH_dataset")):
        # Create directory
        os.mkdir("data/raw/JH_dataset")

    # Check if Dataset doesn't already exist in filesystem
    if(not os.path.exists("data/raw/JH_dataset/COVID-19")):
        # Command to clone dataset
        cmd=  "git clone https://github.com/CSSEGISandData/COVID-19.git"
        cmd_wd= "data/raw/JH_dataset"

    # Otherwise if Dataset repo has already been cloned, peform pull operation
    else:
        cmd= "git pull"
        cmd_wd= "data/raw/JH_dataset/COVID-19"

    # Pull from Git repo
    git_proc= subprocess.Popen(
        cmd,
        cwd=cmd_wd, shell=True, 
        stdout= subprocess.PIPE, stderr= subprocess.PIPE
    )

    proc_timeout= 600
    try:
        (git_proc_out, git_proc_err)= git_proc.communicate(timeout=proc_timeout)
    except TimeoutError:
        print("Update operation on Johns Hopkins Dataset from GITHUB failed...\n")

    print("Output: " + str(git_proc_out))
    print("Error: " + str(git_proc_err))



def get_current_nigeria():
    """ Update data from Nigeria Centre for Disease Control (NCDC)

    Update data from NCDC via webscraping
    
    Parameters:
    ----------

    Returns:
    -------
    """
    # WEB SCRAPING
    # Pull page on COVID-19
    page= requests.get("https://covid19.ncdc.gov.ng/")
    # Parse HTML
    parsed_page= BeautifulSoup(page.content, 'html.parser')
    # Pull Table
    html_table= parsed_page.find('table')
    # Pull table rows
    table_rows= html_table.find_all('tr')

    # Table Header
    table_header= dict()
    # Table data
    table_data=[]

    # Loop through table rows
    for idx,row in enumerate(table_rows):
        # Table headers in first row
        if(idx==0):
            # Pull column headers
            col_headers= row.find_all('th')
            # Make a dictionary of column headers
            table_headers= { idx:col_header.get_text(strip=True) for idx,col_header in enumerate(col_headers) }
        
        # Table data
        # Get row columns
        row_cols= row.find_all('td')
        # Get data body into list
        row_data= [ col.get_text(strip=True) for col in row_cols ]
        # Append col to row list
        table_data.append(row_data)

        # Make data into Pandas Frame
    pd_table= pd.DataFrame(table_data)
    # Remove empty rows
    pd_table= pd_table.dropna()
    # Insert column names
    pd_table= pd_table.rename(columns=table_headers)

    # Drop column "No. of Cases (on admission)"
    pd_table= pd_table.drop(["No. of Cases (on admission)"], axis=1)
    # Rename "No. of Cases (Lab Confirmed)"
    pd_table= pd_table.rename(
        columns={"No. of Cases (Lab Confirmed)": "No. of Cases"}
    )

    # UPDATE DATASET
    pd_table.to_csv(
        "data/processed/NCDC.csv", sep=";", 
    )
    print("Updated data for all {0} states in Nigeria.".format(pd_table.shape[0]))


if __name__ == "__main__":
    get_johns_hopkings()
    get_current_nigeria()
