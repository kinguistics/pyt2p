import argparse
import pickle

from dictionary import *


if __name__ == "__main__":
    ### parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', default='cmudict', choices=['cmudict'])
    parser.add_argument('--stress', default='unstressed', choices=['unstressed','stressed','binarystress'])
    parser.add_argument('--subset', action='store_true')
    parser.add_argument('--barley_cluster', action='store_true')
    args = parser.parse_args()

    if args.barley_cluster:
        with open('kerberos.txt') as f:
            kerberos_cmd = f.read().strip()
    else:
        kerberos_cmd = None


    # train the ViterbiAligner model, saving each iteration as we go
    em = train_alignment(corpus=args.corpus,
                         stress=args.stress,
                         subset=args.subset,
                         kerberos_cmd=kerberos_cmd)

    alignments = align_all_words(corpus=args.corpus,
                                 stress=args.stress,
                                 subset=args.subset)
    with open('all_alignments.pickle','w') as fout:
        pickle.dump(alignments, fout)
