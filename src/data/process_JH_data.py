# Imports
import os, subprocess, json
from datetime import datetime

# Environmental Variables
from dotenv import load_dotenv

import pandas as pd

# HTTP Client
import requests
# For parsing and sifting through HTML
from bs4 import BeautifulSoup

import argparse

#==============================================================================
# COMMAND LINE ARGUMENTS
# Create parser object
cl_parser= argparse.ArgumentParser(
    description="Process COVID-19 worldwide data from Johns Hopkings University \
        GITHUB."
)

# ARGUMENTS
# Path to data folder
cl_parser.add_argument(
    "--data_path", action="store", default="data/",
    help="Path to data folder"
)

# Collect command-line arguments
cl_options= cl_parser.parse_args()


#==============================================================================
def store_relational_model(data_path):
    """ Process Johns Hopkings data into a Relational dataset
    
    Parameters:
    ----------
    data_path: URI-like
        Path to data folder

    Returns:
    -------
    """
    # Read data into dataframe
    raw_data_path= data_path + "raw/JH_dataset/COVID-19/" + \
        "csse_covid_19_data/csse_covid_19_time_series/" + \
        "time_series_covid19_confirmed_global.csv"
    pd_raw= pd.read_csv(raw_data_path)

    # Create DataFrame
    rel_fr= pd.DataFrame(pd_raw)

    # Discard Lat and Long columns
    rel_fr= rel_fr.drop(["Lat", "Long"], axis=1)
    
    # Set NaN to 'no'. Important for indexing
    rel_fr= rel_fr.fillna('no')

    # Rename columns for convienence
    rel_fr= rel_fr.rename(
        columns={"Province/State": "state", "Country/Region": "country"}
        )
    # Index data by (state, country)
    rel_fr= rel_fr.set_index(["state", "country"])
    # Make dates row headers and state/country column headers
    rel_fr= rel_fr.T
    # Stack the data by dates and reset indices
    rel_fr= rel_fr.stack(["state", "country"]).reset_index()
    # Set new column names
    rel_fr= rel_fr.rename(columns={"level_0": "date", 0:"confirmed"})

    # Convert date to datetime type
    rel_fr["date"]= rel_fr.date.astype("datetime64[ns]")

    # UPDATE DATASET
    rel_fr.to_csv(
        data_path + "processed/COVID_relational_full.csv", sep=";",index=False
    )
    print("Number of rows stored: {0}.".format(rel_fr.shape[0]))


#==============================================================================
if __name__ == "__main__":
    store_relational_model(cl_options.data_path)