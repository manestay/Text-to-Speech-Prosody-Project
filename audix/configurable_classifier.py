# This script performs prediction of both prosodic break and pitch accent tasks.
# Currently tested on BURNC and Audix datasets.
# @author: Bryan Li (bl2557)
# includes code written by Agustin Gravano, Rose Sloan, Amaan Khular and Pablo Brusco

import argparse
import numpy as np
import pandas as pd
import sys

import sklearn.impute
from sklearn.model_selection import train_test_split

from classifier_lib import generate_featsets, run_experiments, run_experiments_eval, standardize_df

parser = argparse.ArgumentParser(description='classifier for predicting prosodic breaks')
#########################################################

parser.add_argument('task', help='task to predict: break | accent')
parser.add_argument('--train', help='train file', default="audix-data-2018-10-26.csv")
parser.add_argument('--test', help='test file (if not specified, splits train file into train/test)',
                    default='')
parser.add_argument('--range', type=int, nargs=2, help='range of feature set sizes', default=[1, -1])
parser.add_argument('--no-rank', action='store_false', dest='print_rank', help='do not print feature \
                    ranking', default=True)
parser.add_argument('--test-all', action='store_true',  help='test on all of test split, instead of \
                    just a consistent split of it (default: False)', default=False)
# Part of Speech tags that are considered to be referring expressions
REFERRING_EXP_POS = ["NN", "NNS", "NNP", "NNPS", "PDT", "CD", "POS", "PRP", "PRP$"]

def process_data(df, featcats, task):
    """
    Prepares columns for classification.
    df: dataframe
    featcats: list of feature categories to include. eg, ['syntax/pos','mentions']
    Outputs X (instance vectors), y (labels), columns (feature names)
    """
    features = dict()
    # features['dependency'] = ['syntactic_function', 'next_syntactic_function']
    # features['pos'] = ['Stanford_PoS', 'next_Stanford_PoS']
    # features['spanningtree'] = ['next_word_spanning_label', 'next_word_spanning_depth', 'next_word_spanning_width']
    # features['constituent'] = ['constituent_width', 'constituent_label']
    # features['constpos'] = ['constituent_forward_position', 'constituent_backward_position']
    # features['depth'] = ['word_depth']

    features['syntax/pos'] = ['syntactic_function', 'word_depth', 'tree_depth', 'tree_width',
        'constituent_width', 'constituent_label', 'constituent_forward_position',
        'constituent_backward_position', 'next_word_spanning_depth', 'next_word_spanning_width', 'next_word_spanning_label',
        'Stanford_PoS', 'next_Stanford_PoS', 'next_syntactic_function']
    # features['syntax/pos'] = ['syntactic_function', 'Stanford_PoS', 'next_Stanford_PoS', 'next_syntactic_function', 'constituent_label', 'next_word_spanning_label']
    features['supertag'] = ['supertag']
    features['position'] = ['word_number_in_sentence', 'total_number_of_words_in_sentence']
    features['syllables'] = ['word_number_of_syllables']
    features['NER'] = ['NER', 'next_NER']
    features['punctuation'] = ['punctuation']

    def flatten(z):
        """
        Flatten a list of lists into a list of contained objects.
        """
        return [x for y in z for x in y]
    data = df[flatten([features[x] for x in featcats])].copy()
    # print(flatten([features[x] for x in featcats]))

    # - - - - - - - - - -
    if 'dependency' in featcats:
        dummies_synfn = pd.get_dummies(data["syntactic_function"], prefix="synfn")
        dummies_nsynfn = pd.get_dummies(data["next_syntactic_function"], prefix="nsynfn")
        data = pd.concat([data, dummies_synfn, dummies_nsynfn], axis=1)
        data = data.drop(['syntactic_function', 'next_syntactic_function'], axis=1)

    if 'pos' in featcats:
        dummies_pos = pd.get_dummies(data["Stanford_PoS"], prefix="pos")
        dummies_npos = pd.get_dummies(data["next_Stanford_PoS"], prefix="npos")
        data = pd.concat([data, dummies_pos, dummies_npos], axis=1)
        data = data.drop(['Stanford_PoS', 'next_Stanford_PoS'], axis=1)

    if 'spanningtree' in featcats:
        dummies_nwsl = pd.get_dummies(data["next_word_spanning_label"], prefix="nwsl")
        data = pd.concat([data, dummies_nwsl], axis=1)
        data = data.drop(["next_word_spanning_label"], axis=1)

    if 'constituent' in featcats:
        dummies_const = pd.get_dummies(data["constituent_label"], prefix="const")
        data = pd.concat([data, dummies_const], axis=1)
        data = data.drop(["constituent_label"], axis=1)

    if "syntax/pos" in featcats:
        dummies_const = pd.get_dummies(data["constituent_label"], prefix="const")
        dummies_synfn = pd.get_dummies(data["syntactic_function"], prefix="synfn")
        dummies_nwsl  = pd.get_dummies(data["next_word_spanning_label"], prefix="nwsl")
        data = pd.concat([data, dummies_const, dummies_synfn, dummies_nwsl], axis=1)
        data = data.drop(["constituent_label", "syntactic_function", "next_word_spanning_label"], axis=1)

        dummies_pos = pd.get_dummies(data["Stanford_PoS"], prefix="pos")
        data = pd.concat([data, dummies_pos], axis=1)
        data = data.drop(["Stanford_PoS"], axis=1)

        dummies_npos = pd.get_dummies(data["next_Stanford_PoS"], prefix="npos")
        dummies_nsynfn = pd.get_dummies(data["next_syntactic_function"], prefix="nsynfn")
        data = pd.concat([data, dummies_npos, dummies_nsynfn], axis=1)
        data = data.drop(['next_Stanford_PoS', 'next_syntactic_function'], axis=1)

    # - - - - - - - - - -
    if "position" in featcats:
        # Define new features: number of words until the end of the turn or task
        data['words_until_end_of_sentence'] = df['total_number_of_words_in_sentence'] - df['word_number_in_sentence']
        #data['words_until_end_of_utterance'] = df['total_number_of_words_in_utterance'] - df['word_number_in_utterance']

    # - - - - - - - - - -
    if "supertag" in featcats:
        dummies_super = pd.get_dummies(data["supertag"], prefix="super")
        data = pd.concat([data, dummies_super], axis=1)
        data = data.drop(["supertag"], axis=1)

    # - - - - - - - - - -
    if "NER" in featcats:
        dummies_ner = pd.get_dummies(data["NER"], prefix="ner")
        dummies_nner = pd.get_dummies(data["next_NER"], prefix="nner")
        data = pd.concat([data, dummies_ner, dummies_nner], axis=1)
        data = data.drop(["NER", "next_NER"], axis=1)

    # - - - - - - - - - -
    if "punctuation" in featcats:
        dummies_punc = pd.get_dummies(data["punctuation"], prefix="punc")
        data = pd.concat([data, dummies_punc], axis=1)
        data = data.drop(["punctuation"], axis=1)

    # - - - - - - - - - -

    X = data
    columns = X.columns

    #Any 4-level break is considered a break, nothing lower is
    y_labels = []
    indices = []
    if task == 'break':
        if 'break_index' in df:
            for index, row in df.iterrows():
                y_labels.append(row['break_index'])
                indices.append(index)
        elif 'word_tobi_break_index' in df:
            for index, row in df.iterrows():
                y_labels.append('B' if row['word_tobi_break_index'] == '4' else 'NB')
                indices.append(index)
    elif task == 'accent':
        for index, row in df.iterrows():
            y_labels.append('unaccented' if row['word_tobi_pitch_accent'] in ["*?", "_", "cl", "-"] \
                            else 'accented')
            indices.append(index)

    y = pd.Series(y_labels, index=indices)

    return X, y, columns

if __name__ == '__main__':
    args = parser.parse_args()

    if args.task not in set(['break', 'accent']):
        print("{} is not a valid task, must be either 'break' or 'accent'".format(args.task))
        sys.exit(-1)
    pos_label = 'B' if args.task == 'break' else 'accented'

    # Data frame with all words.
    df_train = pd.read_csv(args.train)
    df_train = standardize_df(df_train)
    # Data frame with just referring expressions.
    df_ref = df_train.loc[df_train['Stanford_PoS'].isin(REFERRING_EXP_POS)].copy()
    print("# words:", len(df_train), " # referring expressions:", len(df_ref))

    if args.test:
        df_test = pd.read_csv(args.test)
        df_test = standardize_df(df_test)
        df_ref_test = df_test.loc[df_test['Stanford_PoS'].isin(REFERRING_EXP_POS)].copy()
        print("# words in test:", len(df_test), " # referring expressions in test:", len(df_ref_test))

    # # Uncomment for debugging.
    # df_train = df_train.head(5000)

    # Add these columns using Amaan's function.
    # IP_Pos_Normalized: the normalized position of the token within its intonational phrase
    # IP_Prev_Mentions: % of all ref.expressions in an into.phrase that have been mentioned before
    # IP_Length: length of the Intonational Phrase the token is a part of
    # df_train = df_train.join(num_tokens_intonational_phrase_prev_mention(df_train, use_percentage=True))

    if 'games' in args.train or 'games' in args.test: # games missing some columns
        feat_names = ["syntax/pos", "position", "syllables"]
    else:
        feat_names = ["syntax/pos", "position", "syllables", "punctuation", "NER", "supertag"]
    start, end = args.range
    start = len(feat_names) if start == -1 else start
    end = len(feat_names) if end == -1 else end
    featsets = generate_featsets(feat_names, start, end)

    if not args.test:
        print("##### ML experiments on all words: #####")
        for t in featsets.keys():
            print("## " + t)

            X, y, cols = process_data(df_train, featsets[t], args.task)
            imputer = sklearn.impute.SimpleImputer(strategy="most_frequent")
            X = imputer.fit_transform(X)
            run_experiments(X, y, cols, pos_label, print_rank=args.print_rank)
            print()
    else:
        print("##### Evaluation ML experiments on all words: #####")
        for t in featsets.keys():
            print("## " + t)
            X_train, y_train, cols_train = process_data(df_train, featsets[t], args.task)
            X_test, y_test, cols_test = process_data(df_test, featsets[t], args.task)

            if not args.test_all:
                _, X_test, _, y_test = train_test_split(X_test, y_test, random_state=1)
                print('testing on a size {} subset of test set'.format(len(y_test)))
            else:
                print('testing on all {} examples from test set'.format(len(y_test)))

            # Add columns to X_train and X_test so they have identical columns.
            cols = set(cols_train) | set(cols_test)
            X_train = X_train.reindex(columns=cols, fill_value=0)
            X_test = X_test.reindex(columns=cols, fill_value=0)
            # import pdb; pdb.set_trace()

            imputer = sklearn.impute.SimpleImputer(strategy="most_frequent")
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.fit_transform(X_test)
            run_experiments_eval(X_train, X_test, y_train, y_test, cols, pos_label, print_rank=args.print_rank)
            print()
