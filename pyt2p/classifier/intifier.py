import csv
import glob

from classifier_util import *

LETTER_TO_INT = None
INT_TO_LETTER = None
PHONE_TO_INT = None
INT_TO_PHONE = None

### functions to get letters and phones back and forth from their int representations
def letter_to_int(letter, corpus='cmudict', stress='unstressed'):
    # initialize the dicts if they don't exist
    if (LETTER_TO_INT is None) or (INT_TO_LETTER is None):
        initialize_letter_dicts(corpus, stress)

    try: letter_int = LETTER_TO_INT[letter]
    except KeyError: letter_int = LETTER_TO_INT[None]

    return letter_int

def int_to_letter(i, corpus='cmudict', stress='unstressed'):
    # initialize the dicts if they don't exist
    if (LETTER_TO_INT is None) or (INT_TO_LETTER is None):
        initialize_letter_dicts(corpus, stress)

    try: int_letter = INT_TO_LETTER[i]
    except KeyError: int_letter = None

    return int_letter

def phone_to_int(phone, corpus='cmudict', stress='unstressed'):
    # initialize the dicts if they don't exist
    if (PHONE_TO_INT is None) or (INT_TO_LETTER is None):
        initialize_phone_dicts(corpus, stress)

    try: phone_int = PHONE_TO_INT[phone]
    except KeyError: phone_int = PHONE_TO_INT[None]

    return phone_int

def int_to_phone(i, corpus='cmudict', stress='unstressed'):
    # initialize the dicts if they don't exist
    if (PHONE_TO_INT is None) or (INT_TO_LETTER is None):
        initialize_phone_dicts(corpus, stress)

    try: int_phone = INT_TO_PHONE[i]
    except KeyError: int_phone = None

    return int_phone

### functions to load letter and phone dicts from file
def initialize_letter_dicts(corpus='cmudict', stress='unstressed'):
    letters_fname = construct_letters_fname(corpus, stress)

    # create the mapping files if they don't exist
    if not len(glob.glob(letters_fname)):
        build_letters_and_phones_from_allowables(corpus, stress)

    global LETTER_TO_INT
    global INT_TO_LETTER
    LETTER_TO_INT, INT_TO_LETTER = read_letters(corpus, stress)

def initialize_phone_dicts(corpus='cmudict', stress='unstressed'):
    phones_fname = construct_phones_fname(corpus, stress)

    # create the mapping files if they don't exist
    if not len(glob.glob(phones_fname)):
        build_letters_and_phones_from_allowables(corpus, stress)

    global PHONE_TO_INT
    global INT_TO_PHONE
    PHONE_TO_INT, INT_TO_PHONE = read_phones(corpus, stress)

### csv reading
def read_letters(corpus='cmudict', stress='unstressed'):
    letters_fname = construct_letters_fname(corpus, stress)

    letter_to_int, int_to_letter = read_forward_backward_csv(letters_fname)
    return letter_to_int, int_to_letter

def read_phones(corpus='cmudict', stress='unstress'):
    phones_fname = construct_phones_fname(corpus, stress)

    phone_to_int, int_to_phone = read_forward_backward_csv(phones_fname)
    return phone_to_int, int_to_phone

def read_forward_backward_csv(fname):
    a2b = {}
    b2a = {}

    with open(fname) as f:
        freader = csv.reader(f)
        for row in freader:
            a,b = row

            if a == '':
                a = None

            if b == '':
                b = None
            else:
                b = int(b)

            assert a not in a2b
            a2b[a] = b

            assert b not in b2a
            b2a[b] = a

    return a2b, b2a


### building the mapping files
def build_letters_and_phones_from_allowables(corpus='cmudict',
                                             stress='unstressed'):

    letters = set()
    phones = set()

    # read from allowables
    allowables_fname = construct_allowables_fname(corpus, stress)

    with open(allowables_fname,'U') as f:
        freader = csv.reader(f)
        for line in freader:
            line_letter, line_phones = line[0], line[1:]

            if line_letter == '':
                line_letter = None
            letters.add(line_letter)

            for phone in line_phones:
                if phone == '':
                    phone = None
                phones.add(phone)

    # write out indexed letters
    letters = list(letters)
    letters.sort()

    letters_fname = construct_letters_fname(corpus, stress)
    with open(letters_fname, 'w') as fout:
        fwriter = csv.writer(fout)
        for idx, letter in enumerate(letters):
            if letter is None:
                letter = ''
            fwriter.writerow([letter, idx])

    # write out indexed phones
    phones = list(phones)
    phones.sort()

    phones_fname = construct_phones_fname(corpus, stress)
    with open(phones_fname, 'w') as fout:
        fwriter = csv.writer(fout)
        for idx, phone in enumerate(phones):
            if phone is None:
                phone = ''
            fwriter.writerow([phone, idx])
