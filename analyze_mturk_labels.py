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


def experiment(debug=False):
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


    # Worker data
    for w in worker_data:
        worker_data[w]["num_batches"] += 0
    worker_data = ddict_to_dict(worker_data)
    df_w = pd.DataFrame.from_dict(worker_data, orient="index")
    df_w["reliability"] = df_w["num_batches"] / df_w["num_all_batches"]

    # Print
    if debug:
        print("="*60)
        print("number of reviewed batches: %d" % num_all_batches)
        print("number of accepted batches: %d" % num_batches)
        print("Number of labeled videos: %d" % len(video_data.keys()))
        print("collaborative reliability: %.2f" % (num_batches/num_all_batches))
        print(df_w.describe().round(2))
        print(df_w)

    # Video data
    r = describe_video_data(video_data, answer, n=3) # choose three workers at random
    #describe_video_data(video_data_accepted, answer)
    return r


def describe_video_data(video_data, answer, n=3):
    video_data = add_system_labels(video_data, answer)
    for v_id in video_data:
        a = video_data[v_id]["mturk"]
        video_data[v_id]["mturk"] = find_most_common(a, n=n)
    df_v = pd.DataFrame.from_dict(video_data, orient="index")
    r = {}
    r["Cohen's kappa (mturk and citizen)"] = cks(df_v["mturk"], df_v["citizen"])
    r["Cohen's kappa (mturk and researcher)"] = cks(df_v["mturk"], df_v["researcher"])
    r["Cohen's kappa (citizen and researcher)"] = cks(df_v["citizen"], df_v["researcher"])
    r["Citizen data performance"] = cr(df_v["researcher"], df_v["citizen"], output_dict=True)
    r["MTurk data performance"] = cr(df_v["researcher"], df_v["mturk"], output_dict=True)
    return r


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


def main(argv):
    r_all = []
    n = 100
    for i in range(n):
        print(i)
        debug = False
        if i == n - 1: debug = True
        r_all.append(experiment(debug=debug))
    print("="*60)
    a = defaultdict(list)
    b = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for k in r_all[0].keys():
        for r in r_all:
            if type(r[k]) != dict:
                a[k].append(r[k])
            else:
                for p in r[k]:
                    if type(r[k][p]) != dict: continue
                    for q in r[k][p]:
                        b[k][p][q].append(r[k][p][q])
    a = ddict_to_dict(a)
    b = ddict_to_dict(b)

    # Report
    for k in a:
        d = np.array(a[k])
        a[k] = {"mean": d.mean().round(2), "std": d.std().round(3)}
    for k in b:
        for p in b[k]:
            for q in b[k][p]:
                d = np.array(b[k][p][q])
                b[k][p][q] = {"mean": d.mean().round(2), "std": d.std().round(3)}
    print(json.dumps(a, indent=4))
    print(json.dumps(b, indent=4))


if __name__ == "__main__":
    main(sys.argv)
