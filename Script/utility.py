import os
import json


def reading_duplicated_files(sset, data_dir):
    loaded_json = os.path.join(data_dir, "Duplicated_files.txt")

    with open(loaded_json, 'r') as f:
        distros_dict = json.load(f)

    return distros_dict.get(sset.split("_")[0])
