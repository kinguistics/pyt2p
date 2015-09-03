import pickle
import random
import argparse
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

# window size for letter features
WINDOW_SIZE = 7

### FUNCTIONS FOR ALIGNMENT ###
def train_alignment(corpus='cmudict', stress="unstressed", subset=False,
                    delete_prob=0.01, insert_prob=0.01):
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


    # run the Viterbi aligner EM, saving as we go
    while True:
        em.run_EM(1)

        em.save(em_fname)

        if em.converged:
            break

        if em.iteration_number > em.max_iterations:
            break

    return em

def align_all_words(corpus='cmudict', stress="unstressed", subset=False, which_paths='best'):
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
        if which_paths == 'best':
            paths = v.get_best_paths()
        else:
            paths = v.get_all_paths()
        if not len(paths):
            continue
        # sort by number of insertions/deletions
        paths.sort(cmp=lambda x,y: cmp(count_nones_in_path(x),
                                       count_nones_in_path(y)))

        #min_nones = count_nones_in_path(paths[0])
        for p in paths:
            '''
            if count_nones_in_path(p) > min_nones:
                continue
            '''
            alignments.append((p.get_elements(), p.get_score()))

    return alignments

def construct_model_fname(corpus, stress, subset):
    model_directory = '%s/%s-%s' % (BASE_DIRECTORY, corpus, stress)
    if subset:
        model_directory = '%s-subset' % (model_directory)
    em_fname = '%s/%s' % (model_directory, EM_MODEL_FLABEL)

    return em_fname

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

def load_latest_saved(model='.'):
   # check to see if there's one we can resume
    saved_iteration_fnames = glob.glob('%s/em_iteration*.pickle' % model)
    if len(saved_iteration_fnames):
        saved_iterations = [(fname, int(re.sub('\D','',fname))) for fname in saved_iteration_fnames]
        saved_iterations.sort(cmp=lambda x,y: cmp(x[1],y[1]))

        final_iteration, final_iteration_number = saved_iterations[-1]
        with open(final_iteration) as f:
            alignment_scores, likelihood = pickle.load(f)

        return alignment_scores, likelihood, final_iteration_number

    else:
        return None,None, None

def test_allowable_deletion_probs(max_i=10, max_k=10):
    ab_pairs = load_dictionary()
    all_counts = {}
    for p in [1.0, 0.5, 0.1, 0.05, 0.01]:
        insert_prob = p
        delete_prob = p/10

        all_counts[(insert_prob, delete_prob)] = []

        # train each EM 10 times
        for i in range(max_i):
            print p, i

            em = train_alignment(subset=True,
                                 delete_prob=delete_prob,
                                 insert_prob=insert_prob)

            alignment_scores = em.alignment_scores[-1]


            # test each on 10 subsets
            for k in range(max_k):
                print p, i, k

                ab_subset = random.sample(ab_pairs, len(ab_pairs)/1000)
                
                alignments = []
                counts = defaultdict(int)
                for a,b in ab_subset:
                    v = ViterbiAligner(a, b, alignment_scores)
                    paths = v.get_best_paths()
                    counts[len(paths)] += 1

                    if not len(paths):
                        continue

                    alignments += paths

                with open('%s-%s-%s.pickle' % (p,i,k),'w') as f:
                    pickle.dump(alignments, f)

                all_counts[(insert_prob, delete_prob)].append(counts)

            # kill the trained model
            os.remove('dictionary/cmudict-unstressed-subset/em_model.pickle')

    return all_counts


### FUNCTIONS FOR CLASSIFIER ###
# currently we only support decision trees
def train_classifier(alignments, window_size=WINDOW_SIZE):
    raw_features, raw_targets = build_features(alignments, window_size)
    classifier = None
    return classifier




if __name__ == "__main__":

    all_counts = test_allowable_deletion_probs(10,10)
    with open('all_test_counts.pickle','w') as f:
        pickle.dump(all_counts)

'''
    ### parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--stress', default='unstressed', choices=['unstressed','stressed','binarystress'])
    parser.add_argument('--subset', action='store_true')
    args = parser.parse_args()


    # train the ViterbiAligner model, saving each iteration as we go
    em = train_alignment(stress=args.stress, subset=args.subset)

    # save the final EM scores
    final_alignment_scores = em.alignment_scores[-1]
    alignment_scores_fname = 'alignment_scores_%s.pickle' % args.stress
    if args.subset:
        alignment_scores_fname = alignment_scores_fname.replace('.pickle','_subset.pickle')
    with open(alignment_scores_fname,'w') as fout:
        pickle.dump(final_alignment_scores, fout)

    # save all alignment scores and likelihoods from the final EM
    em_fname = 'em_%s.pickle' % args.stress
    if args.subset:
        em_fname = em_fname.replace('.pickle','_subset.pickle')
    with open(em_fname,'w') as fout:
        pickle.dump(em.alignment_scores, fout)
        pickle.dump(em.likelihood, fout)


    alignments = align_all_words()
    with open('all_alignments.pickle','w') as fout:
        pickle.dump(alignments, fout)
'''
