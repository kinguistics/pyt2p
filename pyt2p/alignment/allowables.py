import csv
try:
    '''numpy's log provides more float precision'''
    from numpy import log, exp, isinf
except ImportError:
    from math import log, exp, isinf

from alignment_util import logAdd, logSum

BASE_DIRECTORY = 'model'
ALLOWABLES_FLABEL = 'allowables.csv'
STRESS_OPTIONS = ['stressed','binarystress','unstressed']


### FUNCTIONS FOR LOADING ALLOWABLE LETTER-TO-PHONE MAPPINGS ###
def load_allowables(pronun_dictionary='cmudict', stress='unstressed', delete_prob=0.01, insert_prob=0.01):
    if stress not in STRESS_OPTIONS:
        raise TypeError

    dictionary_directory = '%s/%s-%s' % (BASE_DIRECTORY, pronun_dictionary, stress)
    allowables_fname = '%s/%s' % (dictionary_directory, ALLOWABLES_FLABEL)

    allowables = read_allowables_csv(allowables_fname)
    converted_probablities = convert_allowables(allowables, delete_prob, insert_prob)

    return converted_probablities

def convert_allowables(allowables, delete_prob, insert_prob):
    """ convert a dict of {letter: phone} allowables to a
        {letter : {phone : alignment_probability} dict """
    alignment_scores = {}

    for letter in allowables:
        alignment_scores[letter] = {}

        phones = allowables[letter]
        phone_scores = []

        for phone in phones:
            score = 0
            # penalize deletions
            if (phone is None):
                score += log(delete_prob)
            # really penalize insertions
            if (letter is None):
                score += log(insert_prob)
            phone_scores.append(score)

        total_phone_scores = logSum(phone_scores)
        for idx,score in enumerate(phone_scores):
            alignment_scores[letter][phones[idx]] = score - total_phone_scores

    return alignment_scores


def read_allowables_csv(allowables_fname):
    allowables = {}
    with open(allowables_fname) as f:
        freader = csv.reader(f)

        for row in freader:
            a, blist = row[0], row[1:]
            blistout = []

            if a == '':
                a = None

            for b in blist:
                if b == '':
                    b = None
                blistout.append(b)

            allowables[a] = blistout

    return allowables

def write_allowables_csv(allowables, allowables_fname):
    with open(allowables_fname, 'w') as f:
        fwriter = csv.writer(f)

        for a in sorted(allowables.keys()):
            row = []

            if a is None:
                aout = ''
            else:
                aout = a
            row.append(aout)

            for b in sorted(allowables[a]):
                if b is None:
                    b = ''
                row.append(b)

            fwriter.writerow(row)
