import pickle
import glob

from sklearn.preprocessing import OneHotEncoder

import intifier
from classifier_util import *

WINDOW_SIZE = 7

ENCODER = None

def encode_feature(feature, corpus='cmudict', stress='unstressed'):
    if ENCODER is None:
        initialize_encoder(len(feature), corpus, stress)

    feature_encoded = ENCODER.transform([feature])
    return feature_encoded

def encode_features(features, corpus='cmudict', stress='unstressed'):
    if ENCODER is None:
        initialize_encoder(len(features[0]), corpus, stress)

    features_encoded = ENCODER.transform(features)
    return features_encoded

def decode_feature(feature, corpus='cmudict', stress='unstressed'):
    if ENCODER is None:
        initialize_encoder(len(feature), corpus, stress)

    encoder_indices = ENCODER.feature_indices_
    feature.sort_indices()

    feature_ints = []
    for feature_number in range(len(encoder_indices)-1):
        row_feature = feature.indices[feature_number]
        encoder_feature_start = encoder_indices[feature_number]

        feature_int = row_feature - encoder_feature_start
        feature_ints.append(feature_int)

    return feature_ints

def decode_features(features, corpus='cmudict', stress='unstressed'):
    if ENCODER is None:
        initialize_encoder(len(features[0]), corpus, stress)

    all_feature_ints = []

    nrows = features.get_shape()[0]
    for row in range(nrows):
        feature_ints = decode_feature(features.getrow(row), corpus, stress)
        all_feature_ints.append(feature_ints)

    return all_feature_ints

def initialize_encoder(window_size=WINDOW_SIZE, corpus='cmudict', stress='unstressed'):
    onehot_fname = construct_onehot_fname(window_size, corpus, stress)

    if not len(glob.glob(onehot_fname)):
        build_onehot_from_intifiers(window_size, corpus, stress)

    global ENCODER
    ENCODER = load_onehot(window_size, corpus, stress)


def load_onehot(window_size=WINDOW_SIZE, corpus='cmudict', stress='unstressed'):
    onehot_fname = construct_onehot_fname(window_size, corpus, stress)
    with open(onehot_fname) as f:
        onehot = pickle.load(f)

    return onehot

def save_onehot(onehot, window_size=WINDOW_SIZE, corpus='cmudict', stress='unstressed'):
    onehot_fname = construct_onehot_fname(window_size, corpus, stress)
    with open(onehot_fname,'w') as f:
        pickle.dump(onehot, f)

def build_onehot_from_intifiers(window_size=WINDOW_SIZE,
                                 corpus='cmudict',
                                 stress='unstressed'):
    if intifier.LETTER_TO_INT is None:
        intifier.initialize_letter_dicts(corpus, stress)

    letter_ints = intifier.LETTER_TO_INT.values()
    letter_ints.sort()

    letter_windows = []
    letter_i = 0
    while letter_i < len(letter_ints):
        this_letter_window = letter_ints[letter_i:letter_i+window_size]
        if len(this_letter_window) < window_size:
            this_letter_window += range(window_size - len(this_letter_window))

        letter_windows.append(this_letter_window)

        letter_i += 1

    onehot = OneHotEncoder()
    onehot.fit(letter_windows)

    save_onehot(onehot, window_size, corpus, stress)
    return letter_windows
