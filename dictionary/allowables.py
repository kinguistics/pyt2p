import csv

BASE_DIRECTORY = 'dictionary'
ALLOWABLES_FLABEL = 'allowables.pickle'
STRESS_OPTIONS = ['stressed','binarystress','unstressed']

### FUNCTIONS FOR LOADING ALLOWABLE LETTER-TO-PHONE MAPPINGS ###

def load_allowables(pronun_dictionary='cmudict', stress='unstressed'):
    if stress not in STRESS_OPTIONS:
        raise TypeError

    dictionary_directory = '%s/%s-%s' % (BASE_DIRECTORY, pronun_dictionary, stress)
    allowables_fname = '%s/%s' % (dictionary_directory, ALLOWABLES_FLABEL)

    allowables = read_allowables_csv(allowables_fname)

    return allowables

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

            allowables[a] = blist

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
