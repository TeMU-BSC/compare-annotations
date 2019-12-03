import os
import json


fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
data_dir = os.path.join(parentDir, "data")

def reading_duplicated_files(sset):
    loaded_json = os.path.join(data_dir, "Duplicated_files.txt")

    with open(loaded_json, 'r') as f:
        distros_dict = json.load(f)

    return distros_dict.get(sset.split("_")[0])