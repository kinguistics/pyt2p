import pickle
import random
import glob
import re
import os
from collections import defaultdict

from dictionary import load_dictionary
from allowables import load_allowables
#import viterbi
from viterbi import ViterbiEM, ViterbiAligner

BASE_DIRECTORY = 'dictionary'
EM_MODEL_FLABEL = 'em_model.pickle'
ALIGNMENTS_FLABEL = 'alignments.pickle'

# window size for letter features
WINDOW_SIZE = 7

### FUNCTIONS FOR ALIGNMENT ###
def train_alignment(corpus='cmudict',
                    stress="unstressed",
                    subset=False,
                    delete_prob=0.01,
                    insert_prob=0.01,
                    kerberos_cmd=None):
    ### load the corpus and dict of allowables
    ab_pairs = load_dictionary()
    alignment_scores = load_allowables(delete_prob=delete_prob,
                                       insert_prob=insert_prob)

    ### are we testing with a subset?
    if subset:
        # test with 0.1% of the corpus
        ab_pairs = random.sample(ab_pairs, len(ab_pairs)/1000)

    ab_pairs.sort(cmp = lambda x,y: cmp(x[0], y[0]))

    # initialize the EM with the corpus and allowables
    em = ViterbiEM(ab_pairs, alignment_scores, max_iterations=100)

    # check to see if we've got a saved model
    em_fname = construct_model_fname(corpus, stress, subset)
    try: em.load(em_fname)
    except IOError: pass

    if kerberos_cmd is not None:
        os.system(kerberos_cmd)

    # run the Viterbi aligner EM, saving as we go
    while True:
        em.run_EM(1)

        em.save(em_fname)

        if em.converged:
            break

        if em.iteration_number > em.max_iterations:
            break

    return em

def align_all_words(corpus='cmudict', stress="unstressed", subset=False):
    ### load the corpus and dict of allowables
    ab_pairs = load_dictionary()
    #alignment_scores = load_allowables()

    # load the model
    em = ViterbiEM([],None)
    em_fname = construct_model_fname(corpus, stress, subset)
    em.load(em_fname)

    alignment_scores = em.alignment_scores[-1]

    ### are we testing with a subset?
    if subset:
        # test with 0.1% of the corpus
        ab_pairs = random.sample(ab_pairs, len(ab_pairs)/1000)

    ab_pairs.sort(cmp = lambda x,y: cmp(x[0], y[0]))

    alignments = []
    for a,b in ab_pairs:
        v = ViterbiAligner(a, b, alignment_scores)
        paths = v.get_best_paths()
        if not len(paths):
            print "no path:",a,b
            continue

        # sort by number of insertions/deletions
        path_nones = [(path, count_nones_in_path(path)) for path in paths]
        path_nones.sort(cmp=lambda x,y: cmp(x[1], y[1]))

        min_nones = path_nones[0][1]

        for path, path_none in path_nones:

            if path_none > min_nones:
                continue

            alignments.append(path.get_elements())

    return alignments

def construct_model_fname(corpus, stress, subset):
    model_directory = construct_model_directory(corpus, stress, subset)
    em_fname = '%s/%s' % (model_directory, EM_MODEL_FLABEL)

    return em_fname

def construct_alignments_fname(corpus, stress, subset):
    model_directory = construct_model_directory(corpus, stress, subset)
    alignments_fname = '%s/%s' % (model_directory, ALIGNMENTS_FLABEL)

    return alignments_fname

def construct_model_directory(corpus, stress, subset):
    model_directory = '%s/%s-%s' % (BASE_DIRECTORY, corpus, stress)
    if subset:
        model_directory = '%s-subset' % (model_directory)

    return model_directory


def count_nones_in_path(path):
    """ sometimes we get "equally good" alignments with a ton of inserted and
        deleted elements. so we sort each a,b alignment by number of Nones """
    count = 0
    alignment = path.get_elements()
    for a,b in alignment:
        if a is None:
            count += 1
        if b is None:
            count += 1

    return count



### FUNCTIONS FOR CLASSIFIER ###
# currently we only support decision trees
def train_classifier(alignments, window_size=WINDOW_SIZE):
    raw_features, raw_targets = build_features(alignments, window_size)
    classifier = None
    return classifier
