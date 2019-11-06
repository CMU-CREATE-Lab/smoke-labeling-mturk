import sys
import json
import numpy as np
from sklearn.metrics import classification_report as cr
from sklearn.metrics import cohen_kappa_score as cks

# Load json file
def load_json(fpath):
    with open(fpath, "r") as f:
        return json.load(f)


def main(argv):
    mturk_labels = load_json("mturk_batch.json")
    true_labels = load_json("mturk_batch_with_answers.json")

    # Fake labels for testing the analysis
    for i in range(len(mturk_labels)):
        for j in range(len(mturk_labels[i])):
            del mturk_labels[i][j]["url_part"]
            del mturk_labels[i][j]["url_root"]
            mturk_labels[i][j]["label"] = np.random.choice(2)

    # Build a dictionary of solutions
    answer = {}
    for i in range(len(true_labels)):
        for j in range(len(true_labels[i])):
            v = true_labels[i][j]
            answer[v["id"]] = {"label_state": v["label_state"], "label_state_admin": v["label_state_admin"]}

    # Analysis
    gold_pos = 47
    gold_neg = 32
    pos = [23, 19]
    neg = [16, 20]
    mturk_gold = []
    true_gold = []
    mturk = []
    researcher = []
    citizen = []
    mturk_correct = [] # when mturk get the gold standards correct
    researcher_correct = [] # when mturk get the gold standards correct
    citizen_correct = [] # when mturk get the gold standards correct
    for i in range(len(mturk_labels)): # batch
        mturk_tmp = []
        researcher_tmp = []
        citizen_tmp = []
        discard_batch = False
        for j in range(len(mturk_labels[i])): # label
            v = mturk_labels[i][j]
            a = answer[v["id"]] # answer
            b = v["label"] # label
            label_state_admin = a["label_state_admin"]
            label_state = a["label_state"]
            if label_state_admin == gold_pos:
                mturk_gold.append(b)
                true_gold.append(1)
                if b != 1: discard_batch = True
            elif label_state_admin == gold_neg:
                mturk_gold.append(b)
                true_gold.append(0)
                if b != 0: discard_batch = True
            else:
                # mturk worker
                mturk_tmp.append(b)
                # researcher
                if label_state_admin in pos:
                    researcher_tmp.append(1)
                elif label_state_admin in neg:
                    researcher_tmp.append(0)
                else:
                    researcher_tmp.append(None)
                # citizen
                if label_state in pos:
                    citizen_tmp.append(1)
                elif label_state in neg:
                    citizen_tmp.append(0)
                else:
                    citizen_tmp.append(None)
        # add
        mturk += mturk_tmp
        researcher += researcher_tmp
        citizen += citizen_tmp
        if not discard_batch:
            mturk_correct += mturk_tmp
            researcher_correct += researcher_tmp
            citizen_correct += citizen_tmp

    # Print
    print("Gold standards:")
    print(cr(true_gold, mturk_gold))
    print("Number of labels:")
    print(len(mturk), len(citizen), len(researcher))
    print("Cohen's kappa (mturk and citizen):")
    print(cks(mturk, citizen))
    print("Cohen's kappa (mturk and researcher):")
    print(cks(mturk, researcher))
    print("Cohen's kappa (citizen and researcher):")
    print(cks(citizen, citizen))
    print("Number of labels with correct gold:")
    print(len(mturk_correct), len(citizen_correct), len(researcher_correct))
    print("Cohen's kappa with correct gold (mturk and citizen):")
    print(cks(mturk_correct, citizen_correct))
    print("Cohen's kappa with correct gold (mturk and researcher):")
    print(cks(mturk_correct, researcher_correct))
    print("Cohen's kappa with correct gold (citizen and researcher):")
    print(cks(citizen_correct, citizen_correct))


if __name__ == "__main__":
    main(sys.argv)
