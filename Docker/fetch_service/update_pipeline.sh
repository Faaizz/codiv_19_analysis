#/bin/bash

#==============================================================================
# This script runs the required python scripts for updating the dataset

python3 /app/get_data.py --data_path "/app/data/"
python3 /app/process_JH_data.py --data_path "/app/data/"
python3 /app/build_features.py --data_path "/app/data/"