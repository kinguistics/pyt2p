from sklearn import tree
from sklearn.cross_validation import cross_val_score


from classifier_features import build_features, intify_features
from encoder import encode_features

# window size for letter features
WINDOW_SIZE = 7

### FUNCTIONS FOR CLASSIFIER ###
# currently we only support decision trees
def train_classifier(alignments, window_size=WINDOW_SIZE):
    features, targets = build_features(alignments)
    features_int, targets_int = intify_features(features, targets)
    features_enc = encode_features(features_int)

    dtree = tree.DecisionTreeClassifier()
    dtree.fit(features_enc, targets_int)
    return dtree

def crossval_classifier(alignments, window_size=WINDOW_SIZE):
    features, targets = build_features(alignments)
    features_int, targets_int = intify_features(features, targets)
    features_enc = encode_features(features_int)

    dtree = tree.DecisionTreeClassifier()
    accuracies = cross_val_score(dtree, features_enc, targets_int, cv=10)

    return accuracies
