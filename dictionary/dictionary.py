import re
import pickle

from nltk.corpus import cmudict

BASE_DIRECTORY = 'dictionary'
CMUDICT_FNAME = '%s/cmudict.pickle' % BASE_DIRECTORY

'''
    allow a maximum letter limit, to avoid wasting tons of time and memory on
    words like "antidisestablishmentarianism"
'''
MAXIMUM_LETTERS = 22


STRESS_OPTIONS = ['stressed','binarystress','unstressed']


def load_dictionary(pronun_dictionary_name='cmudict', stress='unstressed'):
    """ note that we only support cmudict from nltk """
    if stress not in STRESS_OPTIONS:
        raise TypeError

    try: cmu = cmudict.dict()
    except LookupError, AttributeError:
        cmu = load_cmu_pickle()

    if stress == 'stressed':
        pronun_dictionary = cmu
    else:
        # if we don't want full stress, we have to remove/collapse it
        cmu_unstressed = {}
        for word in cmu:
            cmu_unstressed[word] = []

            pronun_list = cmu[word]
            for pronun in pronun_list:
                pronun_unstressed = []
                for phone in pronun:
                    if stress == 'binarystress':
                        phone = collapse_stress(phone)
                    if stress == 'unstressed':
                        phone = delete_stress(phone)
                    pronun_unstressed.append(phone)
                cmu_unstressed[word].append(pronun_unstressed)
        pronun_dictionary = cmu_unstressed

    converted_dictionary = convert_dictionary(pronun_dictionary)
    return converted_dictionary

def convert_dictionary(pronun_dictionary):
    """ convert a pronunciation dictionary like cmudict to a list of
        (word, pronunciation) tuples """
    ab_pairs = []
    for word in pronun_dictionary:
        if len(word) > MAXIMUM_LETTERS:
            continue
        pronunciations = pronun_dictionary[word]
        for pronun in pronunciations:
            ab_pairs.append((word, pronun))
    return ab_pairs

def load_cmu_pickle():
    with open('%s/cmudict.pickle' % BASE_DIRECTORY) as f:
        cmudict = pickle.load(f)
    return cmudict

def collapse_stress(s):
    """converts fully stressed phone to binary stressed phone"""
    try: s = re.sub('2','1',s)
    except TypeError:
        pass
    return s

def delete_stress(s):
    """converts fully stressed phone to unstressed phone"""
    try: s = re.sub('\d','',s)
    except TypeError:
        pass
    return s
