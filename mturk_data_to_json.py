import sys
import os
import xmltodict
from os import listdir
from os.path import isfile, join, isdir
import json


# Check if a file exists
def is_file_here(file_path):
    return os.path.isfile(file_path)


# Return a list of all files in a folder
def get_all_file_names_in_folder(path):
    return [f for f in listdir(path) if isfile(join(path, f))]


# Load text file
def load_text(fpath):
    with open(fpath, "r") as f:
        return f.read()


# Save json file
def save_json(content, fpath):
    with open(fpath, "w") as f:
        json.dump(content, f)


def main(argv):
    p = "data/"
    file_names = get_all_file_names_in_folder(p)
    data_all = []
    for fn in file_names:
        if ".xml" not in fn: continue
        fn_split = fn.split("_")
        hit_id = fn_split[0]
        assignment_id = fn_split[1]
        worker_id = fn_split[2].split(".")[0]
        data = xmltodict.parse(load_text(p + fn))
        data = json.loads(data["QuestionFormAnswers"]["Answer"][2]["FreeText"])
        data = {"hit_id": hit_id, "assignment_id": assignment_id, "worker_id": worker_id, "data": data}
        data_all.append(data)
    save_json(data_all, "mturk_data.json")


if __name__ == "__main__":
    main(sys.argv)
