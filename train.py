import pickle
import random

import corpus
import viterbi

'''
    allow a maximum letter limit, to avoid wasting tons of time and memory on
    words like "antidisestablishmentarianism"
'''
MAXIMUM_LETTERS = 22

def convert_corpus(corpus):
    ab_pairs = []
    for word in corpus:
        if len(word) > MAXIMUM_LETTERS:
            continue
        pronunciations = corpus[word]
        for pronun in pronunciations:
            ab_pairs.append((word, pronun))
    return ab_pairs

def convert_allowables(allowables):
    alignment_scores = {}

    for letter in allowables:
        alignment_scores[letter] = {}

        phones = allowables[letter]
        for phone in phones:
            alignment_scores[letter][phone] = 0

    return alignment_scores

if __name__ == "__main__":
    corpus, allowables = corpus.load_corpus_and_allowables()

    ab_pairs = convert_corpus(corpus)

    # test with 1% of the corpus
    #ab_pairs = random.sample(ab_pairs, len(ab_pairs)/1000)

    ab_pairs.sort(cmp = lambda x,y: cmp(x[0], y[0]))
    alignment_scores = convert_allowables(allowables)

    em = viterbi.ViterbiEM(ab_pairs, alignment_scores, max_iterations=100)
    #em.e_step(alignment_scores)
    em.run_EM()

    final_alignment_scores = em.alignment_scores[-1]
    with open('alignment_scores.pickle','w') as fout:
        pickle.dump(final_alignment_scores, fout)

    with open('em.pickle','w') as fout:
        pickle.dump(em, fout)
