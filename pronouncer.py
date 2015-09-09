import argparse
import pickle
import glob

from alignment import *
from classifier import *

if __name__ == "__main__":
    ### parse command-line arguments
    parser = argparse.ArgumentParser()

    ### what to do
    parser.add_argument('--train_alignment', action='store_true')
    parser.add_argument('--run_alignment', action='store_true')

    parser.add_argument('--train_classifier', action='store_true')
    parser.add_argument('--run_classifier', action='store_true')

    parser.add_argument('--crossval_classifier', action='store_true')
    parser.add_argument('--test_classifier_depth', action='store_true')

    parser.add_argument('--max_depth', default=100)
    parser.add_argument('--window_size', default=7)
    parser.add_argument('--nfolds', default=10)

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


    em_model_fname = alignment_training.construct_model_fname(args.corpus,
                                                              args.stress,
                                                              args.subset)
    if args.train_alignment and not len(glob.glob(em_model_fname)):
        # train the ViterbiAligner model, saving each iteration as we go
        em = train_alignment(corpus=args.corpus,
                             stress=args.stress,
                             subset=args.subset,
                             kerberos_cmd=kerberos_cmd)

    alignments_fname = alignment_training.construct_alignments_fname(args.corpus,
                                                                     args.stress,
                                                                     args.subset)
    if args.run_alignment and len(glob.glob(em_model_fname)):
        # align all words
        align_all_words(corpus=args.corpus,
                        stress=args.stress,
                        subset=args.subset)

    if args.train_classifier and len(glob.glob(alignments_fname)):
        alignments = load_alignments(args.corpus, args.stress, args.subset)
        dtree = train_classifier(alignments, args.window_size, args.max_depth)

        dtree_directory = 'model/%s-%s' % (args.corpus, args.stress)
        if args.subset:
            dtree_directory = '%s-subset' % dtree_directory
        dtree_flabel = 'dtree_w%s_d%s.pickle' % (args.window_size, args.max_depth)
        dtree_fname = '%s/%s' % (dtree_directory, dtree_flabel)

        with open(dtree_fname, 'w') as f:
            pickle.dump(dtree, f)

    if args.crossval_classifier and len(glob.glob(alignments_fname)):
        alignments = load_alignments(args.corpus, args.stress, args.subset)
        confusion = crossval_classifier(alignments, args.window_size, args.nfolds, args.max_depth)

    if args.test_classifier_depth and len(glob.glob(alignments_fname)):
        alignments = load_alignments(args.corpus, args.stress, args.subset)
        test_classifier_depth(alignments, args.window_size, args.nfolds, args.max_depth)
