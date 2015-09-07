from intifier import letter_to_int, int_to_letter, phone_to_int, int_to_phone

WINDOW_SIZE = 7

def build_features(alignments, window_size=WINDOW_SIZE):
    all_features = []
    all_targets = []

    for alignment in alignments:
        word_features, word_targets = build_word_features(alignment, window_size)
        all_features += word_features
        all_targets += word_targets

    return all_features, all_targets

def build_word_features(alignment, window_size=WINDOW_SIZE):
    features = []
    targets = []

    letters = [pair[0] for pair in alignment]
    phones = [pair[1] for pair in alignment]

    half_window = window_size / 2

    for i in range(len(letters)):
        this_features = []

        for window_i in range(i-half_window,i+half_window+1):
            if window_i < 0 or window_i >= len(letters):
                letter = None
            else:
                letter = letters[window_i]
            this_features.append(letter)

        features.append(this_features)

        phone = phones[i]
        targets.append(phone)

    return features, targets

def intify_features(features, targets):
    intified_features = []
    intified_targets = []

    for alignment_idx in range(len(features)):
        feature = features[alignment_idx]
        target = targets[alignment_idx]

        feature_intified = [letter_to_int(letter) for letter in feature]
        intified_features.append(feature_intified)

        target_intified = phone_to_int(target)
        intified_targets.append(target_intified)

    return intified_features, intified_targets
