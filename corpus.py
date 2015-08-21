import re
import pickle
from nltk.corpus import cmudict

ALLOWABLES_FNAME = 'allowables.pickle'
STRESS_OPTIONS = ['full','collapsed','none']

def collapse_stress(s):
    try: s = re.sub('2','1',s)
    except TypeError:
        pass
    return s

def delete_stress(s):
    try: s = re.sub('\d','',s)
    except TypeError:
        pass
    return s

def load_corpus_and_allowables(corpus='cmudict',stress='none'):
    corpus = load_corpus(corpus, stress)
    allowables = load_allowables(stress)

    return corpus, allowables

def load_corpus(corpus='cmudict', stress='none'):
    if stress not in STRESS_OPTIONS:
        raise TypeError

    cmu = cmudict.dict()

    if stress == 'full':
        return cmu
    else:
        # if we don't want full stress, we have to remove/collapse it
        cmu_unstressed = {}
        for word in cmu:
            cmu_unstressed[word] = []

            pronun_list = cmu[word]
            for pronun in pronun_list:
                pronun_unstressed = []
                for phone in pronun:
                    if stress == 'collapsed':
                        phone = collapse_stress(phone)
                    if stress == 'none':
                        phone = delete_stress(phone)
                    pronun_unstressed.append(phone)
                cmu_unstressed[word].append(pronun_unstressed)
        return cmu_unstressed

def load_allowables(stress='none'):
    if stress not in STRESS_OPTIONS:
        raise TypeError

    with open(ALLOWABLES_FNAME) as f:
        allowables = pickle.load(f)

    if stress == 'full':
        return allowables

    else:
        allowables_unstressed = {}
        for letter in allowables:
            phones = allowables[letter]
            allowables_unstressed[letter] = []

            for phone in phones:
                if stress == 'collapsed':
                    phone = collapse_stress(phone)
                if stress == 'none':
                    phone = delete_stress(phone)
                if phone in allowables_unstressed[letter]:
                    continue
                allowables_unstressed[letter].append(phone)
        return allowables_unstressed

### MOVE THIS TO TRAIN.PY ###


def choose_pronunciation(corpus, word):
    return corpus[word][0]
