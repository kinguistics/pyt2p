import pickle
import glob

#import classifier_features
from classifier_features import build_unseen_word_features, intify_unseen_word_features
#import intifier
from intifier import int_to_phone
#import encoder
from encoder import encode_features

''' will probably want all this to be able to be run from the command line
    at some point, but for now i'm gonna be lazy and just try to set it up with
    sockets '''

CORPUS = 'cmudict'
STRESS = 'unstressed'
SUBSET = False

# don't necessarily need these; can just guess / find
WINDOW_SIZE = 7
DEPTH = 28


CLASSIFIER = None

def classify(word):
    if CLASSIFIER is None:
        initialize_classifier()

    word_features = build_unseen_word_features(word)
    word_ints = intify_unseen_word_features(word_features)
    word_enc = encode_features(word_ints)

    predicted_int = []
    for feature in word_enc:
        predicted_phone_int = CLASSIFIER.predict(feature)[0]
        predicted_int.append(predicted_phone_int)
    predicted_phones = [int_to_phone(i) for i in predicted_int]

    return predicted_phones


def initialize_classifier(corpus=CORPUS, stress=STRESS, subset=SUBSET,
                    window_size=WINDOW_SIZE, depth=DEPTH):
    # DOESN'T HANDLE SUBSET
    dtree_dir = 'model/%s-%s' % (corpus, stress)

    # we're gonna try to find the model with appropriate window size and depth
    #   if it doesn't exist, we'll take whatever model is available
    dtree_fname_glob = glob.glob('%s/dtree_w%s_d%s.pickle' % (dtree_dir, window_size, depth))
    if len(dtree_fname_glob) != 1:
        dtree_fname_glob = glob.glob('%s/dtree*.pickle' % dtree_dir)
    if not len(dtree_fname_glob):
        raise IOError

    dtree_fname = dtree_fname_glob[0]

    with open(dtree_fname) as f:
        dtree = pickle.load(f)

    global CLASSIFIER
    CLASSIFIER = dtree
