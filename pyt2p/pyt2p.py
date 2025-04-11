import csv
import pickle
from nltk.corpus import cmudict
from numpy import log, exp
from time import time

import viterbi

ALLOWABLES_FNAME = "allowables.csv"
CROSSVAL_NFOLDS = 10
DEPTH_TEST_STEP = 2

CMU = cmudict.dict()


def read_allowables(fname):
    allowables = {}

    with open(fname, "U") as f:
        freader = csv.reader(f)
        for row in freader:
            letter = row[0]
            allowables[letter] = {}

            phones = row[1:]
            for phone in phones:
                allowables[letter][phone] = 0

    return allowables


def build_features(alignment, letter_dict, phone_dict):
    features = []
    targets = []
    for i in range(len(alignment)):
        this_features = []

        for window_i in range(i - 3, i + 4):
            if window_i < 0 or window_i >= len(alignment):
                letter = "#"
            else:
                letter = alignment[window_i][-3]
            this_features.append(letter_dict[letter])

        features.append(this_features)

        phone = alignment[i][-2]
        targets.append(phone_dict[phone])

    return features, targets


def build_int_translators(alignment_probabilities):
    letters = alignment_probabilities.keys()
    letters.append("#")
    letters.sort()
    letter_dict = dict(zip(letters, range(len(letters))))

    phones = set()
    for letter in alignment_probabilities:
        for phone in alignment_probabilities[letter]:
            phones.add(phone)
    phones = list(phones)
    phones.sort()
    phone_dict = dict(zip(phones, range(len(phones))))

    return letter_dict, phone_dict


if __name__ == "__main__":
    """
    ### ALIGN LETTERS TO PHONES ###

    ## this is just testing the allowable alignments ##
    allowables = read_allowables(ALLOWABLES_FNAME)

    problems = []
    for word in sorted(CMU.keys()):
        print(word)
        pronun = [l.lower() for l in CMU[word][0]]
        v = ViterbiAligner(word,pronun,allowables)
        v.align()
        alignment = v.get_best_path()
        if not len(alignment):
            problems.append((word,pronun,v))

    ## here is the actual EM ##
    try:
        with open('alignment_probabilities.pickle') as f:
            alignment_probabilities = pickle.load(f)
    except:
        em = ViterbiEM(CMU, allowables)
        em.run_EM()
        alignment_probabilities = em.alignment_probabilities[-1]

        with open('alignment_probabilities.pickle','w') as fout:
            pickle.dump(alignment_probabilities,fout)

    ## here we use the alignment probs from the EM to do the alignments ##
    try:
        with open('alignments.pickle') as f:
            alignments = pickle.load(f)
    except:
        alignments = []
        for word in sorted(CMU.keys()):
            pronun = [l.lower() for l in CMU[word][0]]
            v = ViterbiAligner(word,pronun,alignment_probabilities)
            v.align()
            alignment = v.get_best_path()
            if not len(alignment):
                print("no alignment for",word,pronun)
            alignments.append(alignment)
        with open('alignments.pickle','w') as fout:
            pickle.dump(alignments,fout)

    ## pulling the features ##
    try:
        with open('features_targets.pickle') as f:
            all_features,all_targets = pickle.load(f)
    except:
        letter_dict, phone_dict = build_int_translators(alignment_probabilities)

        all_features = []
        all_targets = []
        for alignment in alignments:
            features,targets = build_features(alignment, letter_dict, phone_dict)

            all_features += features
            all_targets += targets
        with open('features_targets.pickle','w') as fout:
            pickle.dump((all_features,all_targets),fout)
    """
    from sklearn import tree
    from sklearn import preprocessing
    from sklearn.cross_validation import cross_val_score
    import numpy as np

    try:
        with open("features_targets_enc.pickle") as f:
            feature_enc, target_array = pickle.load(f)
    except:
        enc = preprocessing.OneHotEncoder()
        enc.fit(all_features)
        feature_enc = enc.transform(all_features)
        target_array = np.array(all_targets)
        with open("features_targets_enc.pickle", "w") as fout:
            pickle.dump((feature_enc, target_array), fout)

    # real stuff is below. this is testing for max_depth
    # NOTE: the unconstrained tree gives max depth 94
    # so we'll go up to 90 and then try unconstrained

    ### DON'T NEED TO DENSIFY ANYMOREEEEE
    # feature_array = feature_enc.toarray()
    # print("feature array densified")

    fout = open("max_depth_crossval_tests.csv", "w")
    fwriter = csv.writer(fout)
    headerout = ["depth", "avg", "time"] + range(CROSSVAL_NFOLDS)

    for depth in range(0, 94, DEPTH_TEST_STEP)[1:]:
        print("depth =", depth)
        clf = tree.DecisionTreeClassifier(max_depth=depth)
        t_before = time()
        accuracies = cross_val_score(clf, feature_enc, target_array, cv=10)
        t_after = time()
        duration = t_after - t_before
        avg_acc = np.mean(accuracies)
        acc_list = list(accuracies)
        rowout = [depth, avg_acc, duration] + acc_list
        fwriter.writerow(rowout)

        print("accuracy: %s, time: %s" % (avg_acc, duration))

    """
    try:
        with open('dtree.pickle') as f:
            clf = pickle.load(f)
    except:
        print("fitting tree...")
        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(feature_enc, target_array)

    # or do cross-validation

    clf = tree.DecisionTreeClassifier(random_state=0)
    accuracies = cross_val_score(clf, feature_enc, target_array, cv=10)


     some accuracies from a sample run:
    [ 0.80291479,  0.80914104,  0.78321458,  0.80681484,  0.80617996,
        0.7742462 ,  0.78304495,  0.78762121,  0.79670611,  0.82589242]
    """
