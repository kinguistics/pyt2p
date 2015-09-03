import pickle
import random
import argparse
import glob
import re

import corpus
#import viterbi
from viterbi import ViterbiEM, ViterbiAligner


# window size for letter features
WINDOW_SIZE = 7

### FUNCTIONS FOR ALIGNMENT ###
def train_alignment(stress="unstressed", subset=False):
    ### load the corpus and dict of allowables
    pronun_dict, allowables = corpus.load_corpus_and_allowables(stress=stress)

    ### convert corpus and allowables to Viterbi format
    ab_pairs = convert_corpus(pronun_dict)
    alignment_scores = convert_allowables(allowables)

    ### are we testing with a subset?
    if subset:
        # test with 0.1% of the corpus
        ab_pairs = random.sample(ab_pairs, len(ab_pairs)/1000)

    ab_pairs.sort(cmp = lambda x,y: cmp(x[0], y[0]))

    # initialize the EM with the corpus and allowables
    em = ViterbiEM(ab_pairs, alignment_scores, max_iterations=100)

    # check to see if we've got a saved model
    saved_alignment_scores, \
            saved_likelihood, \
            saved_iteration_number= load_latest_saved()
    if saved_alignment_scores is not None:
        em.alignment_scores = saved_alignment_scores
        em.likelihood = saved_likelihood
        em.iteration_number = saved_iteration_number

    # run the Viterbi aligner EM, saving as we go
    while True:
        em.run_EM(1)
        with open('em_iteration_%s.pickle' % em.iteration_number,'w') as fout:
            pickle.dump([em.alignment_scores, em.likelihood], fout)
        if em.converged:
            break

    return em

def align_all_words(stress="unstressed", subset=False):
    ### load the corpus and dict of allowables
    pronun_dict, allowables = corpus.load_corpus_and_allowables(stress=stress)

    ### convert corpus and allowables to Viterbi format
    ab_pairs = convert_corpus(pronun_dict)
    alignment_scores = convert_allowables(allowables)

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
            continue
        # sort by number of insertions/deletions
        paths.sort(cmp=lambda x,y: cmp(count_nones_in_path(x),
                                       count_nones_in_path(y)))

        min_nones = count_nones_in_path(paths[0])
        for p in paths:
            if count_nones_in_path(p) > min_nones:
                continue
            alignments.append(p.get_elements())

    return alignments

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


def convert_allowables(allowables):
    """ convert a dict of {letter: phone} allowables to a
        {letter : {phone : alignment_probability} dict """
    alignment_scores = {}

    for letter in allowables:
        alignment_scores[letter] = {}

        phones = allowables[letter]
        for phone in phones:
            alignment_scores[letter][phone] = 0

    return alignment_scores


### FUNCTIONS FOR CLASSIFIER ###
# currently we only support decision trees
def train_classifier(alignments, window_size=WINDOW_SIZE):
    raw_features, raw_targets = build_features(alignments, window_size)
    classifier = None
    return classifier

if __name__ == "__main__":
    ### parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--stress', default='unstressed', choices=['unstressed','stressed','binarystress'])
    parser.add_argument('--subset', action='store_true')
    args = parser.parse_args()

    '''
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
    '''

    alignments = align_all_words()
    with open('all_alignments.pickle','w') as fout:
        pickle.dump(alignments, fout)
