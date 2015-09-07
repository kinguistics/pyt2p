import argparse
import pickle
import glob

from dictionary import *


if __name__ == "__main__":
    ### parse command-line arguments
    parser = argparse.ArgumentParser()

    ### what to do
    parser.add_argument('--train_alignment', action='store_true')
    parser.add_argument('--run_alignment', action='store_true')
    parser.add_argument('--train_classifier', action='store_true')
    parser.add_argument('--run_classifier', action='store_true')

    ### general arguments
    parser.add_argument('--corpus', default='cmudict', choices=['cmudict'])
    parser.add_argument('--stress', default='unstressed', choices=['unstressed','stressed','binarystress'])
    parser.add_argument('--subset', action='store_true')

    ### cluster-specific arguments
    parser.add_argument('--barley_cluster', action='store_true')
    args = parser.parse_args()

    if args.barley_cluster:
        with open('kerberos.txt') as f:
            kerberos_cmd = f.read().strip()
    else:
        kerberos_cmd = None


    em_model_fname = training.construct_model_fname(corpus, stress, subset)
    if args.train_alignment or not len(glob(em_model_fname)):
        # train the ViterbiAligner model, saving each iteration as we go
        em = train_alignment(corpus=args.corpus,
                            stress=args.stress,
                            subset=args.subset,
                            kerberos_cmd=kerberos_cmd)

    alignments_fname = training.construct_alignments_fname(corpus, stress, subset)
    if args.run_alignment and len(glob(em_model_fname)):
        # align all words
        alignments = align_all_words(corpus=args.corpus,
                                    stress=args.stress,
                                    subset=args.subset)
        with open(alignments_fname,'w') as fout:
            pickle.dump(alignments, fout)
