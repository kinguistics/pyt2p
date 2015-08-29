import pickle
import random
import argparse

import corpus
#import viterbi
from viterbi import ViterbiEM

'''
    allow a maximum letter limit, to avoid wasting tons of time and memory on
    words like "antidisestablishmentarianism"
'''
MAXIMUM_LETTERS = 22

# window size for letter features
WINDOW_SIZE = 7

### FUNCTIONS FOR ALIGNMENT ###
def train_alignment(stress="none", subset=False):
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

    # run the Viterbi aligner EM
    em = ViterbiEM(ab_pairs, alignment_scores, max_iterations=100)
    #em.e_step(alignment_scores)
    em.run_EM()

    return em

def convert_corpus(corpus):
    """ convert a pronunciation dictionary like cmudict to a list of
        (word, pronunciation) tuples """
    ab_pairs = []
    for word in corpus:
        if len(word) > MAXIMUM_LETTERS:
            continue
        pronunciations = corpus[word]
        for pronun in pronunciations:
            ab_pairs.append((word, pronun))
    return ab_pairs

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
    parser.add_argument('--stress', default='none', choices=['none','full','collapsed'])
    parser.add_argument('--subset', action='store_true')
    args = parser.parse_args()

    # train the ViterbiAligner model
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
