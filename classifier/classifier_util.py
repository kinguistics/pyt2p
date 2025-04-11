BASE_DIRECTORY = 'model'
ALLOWABLES_FLABEL = 'allowables.csv'
LETTERS_FLABEL = 'letters.csv'
PHONES_FLABEL = 'phones.csv'
ONEHOT_FLABEL = 'letters_onehot_%s.pickle'

def construct_onehot_fname(window_size, corpus, stress):
    directory = construct_directory_name(corpus,stress)
    onehot_flabel = ONEHOT_FLABEL % window_size
    onehot_fname = '%s/%s' % (directory, onehot_flabel)

    return onehot_fname

def construct_letters_fname(corpus, stress):
    directory = construct_directory_name(corpus, stress)
    letters_fname = '%s/%s' % (directory, LETTERS_FLABEL)

    return letters_fname

def construct_phones_fname(corpus, stress):
    directory = construct_directory_name(corpus, stress)
    phones_fname = '%s/%s' % (directory, PHONES_FLABEL)

    return phones_fname

def construct_directory_name(corpus, stress):
    directory = '%s/%s-%s' % (BASE_DIRECTORY, corpus, stress)
    return directory

def construct_allowables_fname(corpus, stress):
    directory = construct_directory_name(corpus, stress)
    allowables_fname = '%s/%s' % (directory, ALLOWABLES_FLABEL)

    return allowables_fname
