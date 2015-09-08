import random
import csv
import pickle
import os
from time import time

from sklearn import tree
from sklearn.cross_validation import cross_val_score
import numpy as np

from classifier_features import build_features, intify_features
from encoder import encode_features

# window size for letter features
WINDOW_SIZE = 7
MAX_DEPTH=100

### FUNCTIONS FOR CLASSIFIER ###
# currently we only support decision trees
def train_classifier(alignments, window_size=WINDOW_SIZE, max_depth=MAX_DEPTH):
    features_enc, targets_int = encode_alignments(alignments)

    dtree = tree.DecisionTreeClassifier(max_depth=max_depth)
    dtree.fit(features_enc, targets_int)
    return dtree

def sklearn_crossval(alignments, window_size=WINDOW_SIZE, nfolds=10):
    features_enc, targets_int = encode_alignments(alignments)

    dtree = tree.DecisionTreeClassifier()
    accuracies = cross_val_score(dtree, features_enc, targets_int, cv=nfolds)

    return accuracies

def crossval_classifier(alignments, window_size=WINDOW_SIZE, nfolds=10, max_depth=MAX_DEPTH):
    random.shuffle(alignments)
    alignment_folds = step_through(alignments, nfolds)

    accuracies = []
    for fold in alignment_folds:
        train_fold, heldout_fold = fold
        train_dtree = train_classifier(train_fold, window_size)

        fold_confusion = test_classifier(train_dtree, heldout_fold)

        confusion_accuracy = calculate_confusion_accuracy(fold_confusion)
        accuracies.append(confusion_accuracy)

    return accuracies

def test_classifier_depth(alignments, window_size=WINDOW_SIZE, nfolds=10, max_depth=MAX_DEPTH):
    fout = open('classifier/max_depth_crossval_tests.csv','w')
    fwriter = csv.writer(fout)
    headerout = ['max_depth','avg', 'time', 'size','depth'] + range(nfolds)
    fwriter.writerow(headerout)

    features_enc, targets_int = encode_alignments(alignments)

    for depth in range(0, max_depth, 5)[1:]:
        print "depth =", depth
        clf = tree.DecisionTreeClassifier(max_depth=depth)
        t_before = time()
        accuracies = cross_val_score(clf,
                                     features_enc,
                                     targets_int,
                                     cv=10)
        t_after = time()
        duration = t_after - t_before
        avg_acc = np.mean(accuracies)
        acc_list = list(accuracies)

        dtree = train_classifier(alignments, window_size, depth)
        dtree_fname = 'classifier/depth_%s.pickle' % depth
        with open(dtree_fname,'w') as dtree_f:
            pickle.dump(dtree, dtree_f)
        dtree_size = os.stat(dtree_fname).st_size

        calculated_depth = tree_depth(0, dtree.tree_)

        rowout = [depth, avg_acc, duration, dtree_size, calculated_depth] + acc_list
        fwriter.writerow(rowout)

    fout.close()

def encode_alignments(alignments):
    features, targets = build_features(alignments)
    features_int, targets_int = intify_features(features, targets)
    features_enc = encode_features(features_int)

    return features_enc, targets_int

def calculate_confusion_accuracy(confusion):
    correct = 0
    total = 0

    for a in confusion.keys():
        for b in confusion[a].keys():
            if a == b:
                correct += 1
            total += 1

    accuracy = float(correct) / total
    return accuracy

def test_classifier(dtree, alignments):
    confusion_matrix_d = {}

    features_enc, targets_int = encode_alignments(alignments)

    for feature, target in zip(features_enc, targets_int):
        if target not in confusion_matrix_d:
            confusion_matrix_d[target] = {}
        predicted = dtree.predict(feature)[0]
        if predicted not in confusion_matrix_d[target]:
            confusion_matrix_d[target][predicted] = 0
        confusion_matrix_d[target][predicted] += 1

    return confusion_matrix_d

def add_confusion_matrices(d1, d2):
    dout = {}
    for a in list(set(d1.keys()+d2.keys())):
        if a not in dout:
            dout[a] = {}

        blist = []
        if a in d1:
            blist += d1[a].keys()
        if a in d2:
            blist += d2[a].keys()

        for b in list(set(blist)):
            if b not in dout[a]:
                dout[a][b] = 0
            try: dout[a][b] += d1[a][b]
            except: pass
            try: dout[a][b] += d2[a][b]
            except: pass

    return dout

def step_through(l, n):
    step_size = float(len(l))/n
    step_indices = [int(i*step_size) for i in range(n)] + [len(l)+1]

    for step_idx in range(n):
        heldout_start = step_indices[step_idx]
        heldout_stop = step_indices[step_idx + 1]

        heldout = l[heldout_start:heldout_stop]
        train_fold = l[heldout_stop:] + l[:heldout_start]

        yield((train_fold, heldout))

def tree_depth(node, the_tree):
    if node == -1:
        return -1

    left_depth = tree_depth(the_tree.children_left[node], the_tree) + 1
    right_depth = tree_depth(the_tree.children_right[node], the_tree) + 1

    return max(left_depth, right_depth)
