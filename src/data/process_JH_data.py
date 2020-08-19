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


def store_relational_model():
    """ Process Johns Hopkings data into a Relational dataset
    
    Parameters:
    ----------

    Returns:
    -------
    """
    # Read data into dataframe
    data_path= "data/raw/JH_dataset/COVID-19/" + \
        "csse_covid_19_data/csse_covid_19_time_series/" + \
        "time_series_covid19_confirmed_global.csv"
    pd_raw= pd.read_csv(data_path)

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
        "data/processed/COVID_relational_full.csv", sep=";",index=False
    )
    print("Number of rows stored: {0}.".format(rel_fr.shape[0]))


if __name__ == "__main__":
    store_relational_model()