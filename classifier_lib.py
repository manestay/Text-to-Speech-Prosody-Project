from collections import OrderedDict
import itertools
import numpy as np

import pandas as pd

import sklearn
import sklearn.metrics
from sklearn import ensemble
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.dummy import DummyClassifier

# Trains and evaluates a classifier running 5-fold CV; compares results against
# a majority-class baseline; and ranks features according to their importance.
# Arguments:
#  clf: classifier
#  X_train, y_train: training data (aka 'development set')
#  X_test, y_test: test data (aka 'evaluation set')
#  columns: feature names
# (Adapted from Pablo Brusco's code.)

def cross_val(clf, X_train, y_train, X_test, y_test):
    res_cv = cross_val_score(clf, X_train, y_train, cv=4, scoring="accuracy")
    dummy_clf = DummyClassifier(strategy="most_frequent")
    random_cv = cross_val_score(dummy_clf, X_train, y_train, cv=4, scoring="accuracy")

    # print("Classifier: {}".format(type(clf)))
    print("Cross-validation results: {} +/- {} (random={})".format(round(res_cv.mean(), 3), round(res_cv.std(), 3), round(random_cv.mean(), 3)))

def test(clf, X_train, y_train, X_test, y_test, columns, pos_label, print_rank=True):
    clf.fit(X_train, y_train)
    dummy_clf = DummyClassifier(strategy="most_frequent")
    dummy_clf.fit(X_train, y_train)

    res_train = clf.score(X_train, y_train)
    random_train = dummy_clf.score(X_train, y_train)
    print("On training data: accuracy={} (random={})".format(round(res_train, 3), round(random_train, 3)))

    res_accuracy = clf.score(X_test, y_test)
    random_accuracy = dummy_clf.score(X_test, y_test)

    y_pred = clf.predict(X_test)
    print("On test data:", end=" ")
    print("accuracy=%.3f (random=%.3f) f1=%.3f precision=%.3f recall=%.3f"%(
        res_accuracy, random_accuracy,
        sklearn.metrics.f1_score(y_test, y_pred, pos_label=pos_label),
        sklearn.metrics.precision_score(y_test, y_pred, pos_label=pos_label),
        sklearn.metrics.recall_score(y_test, y_pred, pos_label=pos_label)))
    if print_rank:
        print("Feature ranking:")
        importances = clf.feature_importances_
        indices = np.argsort(importances)[::-1]
        for f in range(min(20, X_train.shape[1])):
                print("%d. feature %d (%f) %s" % (f + 1, indices[f], importances[indices[f]], columns[indices[f]]))

    print("-----------------")
    return

def run_experiments(X, y, columns, pos_label, print_rank=True):
    """
    Splits the data into training/test sets, and runs the ML tests using a RF classifier.
    """

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)
    clf = sklearn.ensemble.RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=1)
    # cross_val(clf, X_train, y_train, X_test, y_test)
    test(clf, X_train, y_train, X_test, y_test, columns, pos_label, print_rank)

def run_experiments_eval(X_train, X_test, y_train, y_test, columns, pos_label, print_rank=True):
    """
    Runs the ML evaluation tests on given train and test sets using a RF classifier.
    """
    clf = sklearn.ensemble.RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=1)
    # cross_val(clf, X_train, y_train, X_test, y_test)
    test(clf, X_train, y_train, X_test, y_test, columns, pos_label, print_rank)

def generate_featsets(l, start=1, end=5, featsets=OrderedDict()):
    """
    Creates feature sets based on all combinations of given list, and adds them into the featsets dict.
    """
    for i in range(start, end + 1):
        combinations = list(itertools.combinations(l, i))
        for combo in combinations:
            featsets['_'.join(combo)] = combo
    return featsets

def standardize_df(df):
    """
    Renames columns of dataframe, and changes values within them, to be consistent.
    """
    d = {
        'word_pos_tag': 'Stanford_PoS',
        'next_PoS': 'next_Stanford_PoS',
        'S-Tag': 'supertag',
        'pitch_accent': 'word_tobi_pitch_accent',
        'word_number_in_utterance': 'word_number_in_sentence',
        'total_number_of_words_in_utterance': 'total_number_of_words_in_sentence',

        # for games
        'word_number_in_turn': 'word_number_in_segment',
        'total_number_of_words_in_turn': 'total_number_of_words_in_segment',
        'word_number_in_task': 'word_number_in_session',
        'total_number_of_words_in_task': 'total_number_of_words_in_session',
        # for burnc
        'word_number_in_paragraph': 'word_number_in_segment',
        'total_number_of_words_in_paragraph': 'total_number_of_words_in_segment',
        'word_number_in_story': 'word_number_in_session',
        'total_number_of_words_in_story': 'total_number_of_words_in_session',


        'Words_Back_Mentioned': 'Far_Back_Mention'
    }
    df = df.rename(index=str, columns={k: v for k, v in d.items() if v not in df})

    pos_cols = ['Stanford_PoS', 'next_Stanford_PoS', 'Most_Recent_Mention_PoS',
                'Recent_Explicit_Mention_PoS', 'Recent_Implicit_Mention_PoS']
    for col in pos_cols:
        df[col] = df[col].str.replace('/', '_')
        df[col] = df[col].replace({'NP': 'NNP', 'NPS': 'NNPS', 'PP': 'PRP', 'PP$': 'PRP$'})
    return df
