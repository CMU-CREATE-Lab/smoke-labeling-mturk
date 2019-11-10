import sys
import json
import numpy as np
from sklearn.metrics import classification_report as cr
from sklearn.metrics import cohen_kappa_score as cks
from collections import defaultdict, Counter
import pandas as pd


# Convert a defaultdict to dict
def ddict_to_dict(d):
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = ddict_to_dict(v)
    return dict(d)


# Load json file
def load_json(fpath):
    with open(fpath, "r") as f:
        return json.load(f)


# Find the most common element in an array (with random permutation)
def find_most_common(a, n=None):
    a = np.random.permutation(a)
    if n is not None:
        n = np.minimum(n, len(a))
        a = np.random.choice(a, n, replace=False)
    return Counter(a).most_common(1)[0][0]


def main(argv):
    mturk_labels = load_json("mturk_data.json")
    true_labels = load_json("mturk_batch_with_answers.json")

    # Build a dictionary of solutions
    answer = {}
    for i in range(len(true_labels)): # batch
        for j in range(len(true_labels[i])): # videos in the batch
            v = true_labels[i][j]
            answer[v["id"]] = {"label_state": v["label_state"], "label_state_admin": v["label_state_admin"]}

    # Analysis
    gold_pos = 47
    gold_neg = 32
    num_all_batches = 0 # number of reviewed batches
    num_batches = 0 # number of good batches (passed quality check)
    worker_data = defaultdict(lambda: defaultdict(int))
    video_data = defaultdict(lambda: defaultdict(list))
    video_data_accepted = defaultdict(lambda: defaultdict(list)) # when mturk get the gold standards correct
    for i in range(len(mturk_labels)): # batch
        m = mturk_labels[i]
        data = m["data"]
        worker_id = m["worker_id"]
        if worker_id in ["ASXRRKY1HG2OC", "A2658LN9LNAR1D", "AMPMTF5IAAMK8"]: continue
        worker_data[worker_id]["num_all_batches"] += 1
        num_all_batches += 1
        mturk_tmp = []
        discard_batch = False
        for j in range(len(data)): # label
            v = data[j]
            video_id = v["video_id"]
            a = answer[video_id] # answer
            b = v["label"] # label
            label_state_admin = a["label_state_admin"]
            if label_state_admin == gold_pos:
                if b != 1: discard_batch = True
            elif label_state_admin == gold_neg:
                if b != 0: discard_batch = True
            else:
                # not gold standards
                video_data[video_id]["mturk"] += [b]
                mturk_tmp.append(v)
        # add
        if not discard_batch:
            worker_data[worker_id]["num_batches"] += 1
            num_batches += 1
            for v in mturk_tmp:
                video_data_accepted[v["video_id"]]["mturk"] += [v["label"]]

    # Print
    print("number of reviewed batches: %d" % num_all_batches)
    print("number of accepted batches: %d" % num_batches)
    print("collaborative reliability: %.2f" % (num_batches/num_all_batches))

    # Video data
    print("="*60)
    print("FOR ALL DATA")
    describe_video_data(video_data, answer)
    print("="*60)
    print("FOR ONLY ACCEPTED DATA")
    describe_video_data(video_data_accepted, answer)

    # Worker data
    print("="*60)
    for w in worker_data:
        worker_data[w]["num_batches"] += 0
    worker_data = ddict_to_dict(worker_data)
    df_w = pd.DataFrame.from_dict(worker_data, orient="index")
    df_w["reliability"] = df_w["num_batches"] / df_w["num_all_batches"]
    print(df_w.describe().round(2))
    print(df_w)


def describe_video_data(video_data, answer):
    video_data = add_system_labels(video_data, answer)
    for v_id in video_data:
        a = video_data[v_id]["mturk"]
        video_data[v_id]["mturk"] = find_most_common(a)
    df_v = pd.DataFrame.from_dict(video_data, orient="index")
    print("Labeled %d videos" % len(df_v))
    print("Cohen's kappa (mturk and citizen): %.2f" % (cks(df_v["mturk"], df_v["citizen"])))
    print("Cohen's kappa (mturk and researcher): %.2f" % (cks(df_v["mturk"], df_v["researcher"])))
    print("Cohen's kappa (citizen and researcher): %.2f" % (cks(df_v["citizen"], df_v["researcher"])))
    print("Citizen data performance:")
    print(cr(df_v["researcher"], df_v["citizen"]))
    print("MTurk data performance:")
    print(cr(df_v["researcher"], df_v["mturk"]))


def add_system_labels(video_data, answer):
    pos = [23, 19]
    neg = [16, 20]
    video_data = ddict_to_dict(video_data)
    for v_id in video_data:
        a = answer[v_id]
        label_state_admin = a["label_state_admin"]
        label_state = a["label_state"]
        # researcher
        if label_state_admin in pos:
            video_data[v_id]["researcher"] = 1
        elif label_state_admin in neg:
            video_data[v_id]["researcher"] = 0
        else:
            video_data[v_id]["researcher"] = None
        # citizen
        if label_state in pos:
            video_data[v_id]["citizen"] = 1
        elif label_state in neg:
            video_data[v_id]["citizen"] = 0
        else:
            video_data[v_id]["citizen"] = None
    return video_data


if __name__ == "__main__":
    main(sys.argv)
