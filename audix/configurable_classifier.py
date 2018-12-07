# This script performs prediction of both prosodic break and pitch accent tasks.
# Currently tested on Games, BURNC, and Audix datasets.
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

## Amaan's code.
def get_input_has_been_mentioned(df):
    '''
    Generates binary value feature column that determines whether a token as been mentioned before or not.
    '''
    return (df['Most_Recent_Mention'] > 0).astype(int).to_frame("Has_Been_Mentioned")

## Amaan's code.
def num_tokens_intonational_phrase_prev_mention(df, use_percentage=False):
    '''
    Get percentage of all referring expressions in an intonational phrase that have been mentioned before
    or determine whehther all referring expressions in an IP have been mentioned before.

    Generates feature with length of the Intonational Phrase the token is a part of

    Generates features with the normalized position of the token within its intonational phrase

    :param df Dataframe to filter from
    :param bool use_percentage Flag that determines whether to calculate percentage or not.
    '''

    df = pd.concat([df['Intonational_Phrase_ID'], get_input_has_been_mentioned(df)], axis=1)

    ip_id = -1
    counter = 0
    curr_ip_id = 1
    ip_series = np.array([])
    ip_length = np.array([])
    ip_pos_norm = np.array([])

    ip_groups = df.groupby(['Intonational_Phrase_ID'])

    group_keys = ip_groups.groups.keys()

    for i in group_keys:
        counter = 0
        value = 1
        for idx, row in enumerate(ip_groups.get_group(i)['Has_Been_Mentioned']):

            # Count how many referring expressions have been previously mentioned
            if row == 1:
                counter += 1

            # Detect if a referring expression in IP has not been previously mentioned
            if row != 1:
                value = 0

            if idx > 0:
                ip_pos_norm = np.append(ip_pos_norm, idx / float(len(ip_groups.get_group(i))))
            else:
                ip_pos_norm = np.append(ip_pos_norm, 0)

        if use_percentage:
            ip_series = np.append(ip_series, np.full(len(ip_groups.get_group(i)), counter / float(len(ip_groups.get_group(i))), dtype=float))
        else:
            ip_series = np.append(ip_series, np.full(len(ip_groups.get_group(i)), value), dtype=int)

        ip_length = np.append(ip_length, np.full(len(ip_groups.get_group(i)), len(ip_groups.get_group(i)), dtype=int))

    df_ip_mentions = pd.Series(ip_series).to_frame("IP_Prev_Mentions").fillna(0)
    df_ip_length = pd.Series(ip_length).to_frame("IP_Length").fillna(0)
    df_ip_pos_norm = pd.Series(ip_pos_norm).to_frame("IP_Pos_Normalized").fillna(0)

    return df_ip_pos_norm.join(df_ip_mentions.join(df_ip_length))

def process_data(df, featcats, task):
    """
    Prepares columns for classification. NOTE: some columns renamed for consistency between datasets,
    see classifier_lib.standardize_df()
    df: dataframe
    featcats: list of feature categories to include. eg, ['syntax/pos','mentions']
    Outputs X (instance vectors), y (labels), columns (feature names)
    """
    features = dict()

    features['syntax/pos'] = ['syntactic_function', 'word_depth', 'tree_depth', 'tree_width',
        'constituent_width', 'constituent_label', 'constituent_forward_position',
        'constituent_backward_position', 'next_word_spanning_depth', 'next_word_spanning_width', 'next_word_spanning_label',
        'Stanford_PoS', 'next_Stanford_PoS', 'next_syntactic_function']
    features['supertag'] = ['supertag']
    features['position'] = ['word_number_in_sentence', 'total_number_of_words_in_sentence']
    features['turn/task'] = ['word_number_in_sentence', 'word_number_in_segment', 'word_number_in_session',
                             'total_number_of_words_in_sentence', 'total_number_of_words_in_segment', 'total_number_of_words_in_session']
    features['morph'] = ['word_number_of_syllables']
    features['NER'] = ['NER', 'next_NER']
    features['punctuation'] = ['punctuation']
    features['mentions'] = ['Most_Recent_Mention',
                            'Recent_Explicit_Mention', 'Recent_Implicit_Mention',
                            'Most_Recent_Mention_PoS', 'Recent_Explicit_Mention_PoS',
                            'Recent_Implicit_Mention_PoS', 'Number_Of_Coref_Mentions',
                            'Number_Of_Explicit_Mentions', 'Number_Of_Implicit_Mentions',
                            'Most_Recent_Mention_Syntactic_Function',
                            'Recent_Explicit_Mention_Syntactic_Function',
                            'Recent_Implicit_Mention_Syntactic_Function',
                            'Far_Back_Mention']

    def flatten(z):
        """
        Flatten a list of lists into a list of contained objects.
        """
        return [x for y in z for x in y]
    data = df[flatten([features[x] for x in featcats])].copy()

    # - - - - - - - - - -

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
        data['words_until_end_of_sentence'] = df['total_number_of_words_in_sentence'] - df['word_number_in_sentence']

    if "turn/task" in featcats:
        # Define new features: number of words until the end of the turn or task
        data['words_until_end_of_sentence'] = df['total_number_of_words_in_sentence'] - df['word_number_in_sentence']
        data['words_until_end_of_segment'] = df['total_number_of_words_in_segment'] - df['word_number_in_segment']
        data['words_until_end_of_session'] = df['total_number_of_words_in_session'] - df['word_number_in_session']

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

    if "mentions" in featcats:
        data['Number_Of_Coref_Mentions'] = data['Number_Of_Coref_Mentions'].fillna(value=0)
        data['Far_Back_Mention'] = data['Far_Back_Mention'].fillna(value=1000000)
        dummies_cmpos = pd.get_dummies(data["Most_Recent_Mention_PoS"], prefix="cmpos")
        dummies_cepos = pd.get_dummies(data["Recent_Explicit_Mention_PoS"], prefix="cepos")
        dummies_cipos = pd.get_dummies(data["Recent_Implicit_Mention_PoS"], prefix="cipos")
        dummies_cmsynf = pd.get_dummies(data["Most_Recent_Mention_Syntactic_Function"], prefix="cmsynf")
        dummies_cesynf = pd.get_dummies(data["Recent_Explicit_Mention_Syntactic_Function"], prefix="cesynf")
        dummies_cisynf = pd.get_dummies(data["Recent_Implicit_Mention_Syntactic_Function"], prefix="cisynf")
        data = pd.concat([data, dummies_cmpos, dummies_cepos, dummies_cipos,
                         dummies_cmsynf, dummies_cesynf, dummies_cisynf], axis=1)
        data = data.drop(['Most_Recent_Mention_PoS','Recent_Explicit_Mention_PoS','Recent_Implicit_Mention_PoS',
                          'Most_Recent_Mention_Syntactic_Function','Recent_Explicit_Mention_Syntactic_Function',
                          'Recent_Implicit_Mention_Syntactic_Function'], axis=1)
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
    if 'Intonational_Phrase_ID' in df_train:
        df_train = df_train.join(num_tokens_intonational_phrase_prev_mention(df_train, use_percentage=True))
    # Data frame with just referring expressions.
    df_ref = df_train.loc[df_train['Stanford_PoS'].isin(REFERRING_EXP_POS)].copy()
    print("# words:", len(df_train), " # referring expressions:", len(df_ref))
    if args.test:
        df_test = pd.read_csv(args.test)
        df_test = standardize_df(df_test)
        if 'Intonational_Phrase_ID' in df_test:
            df_test = df_test.join(num_tokens_intonational_phrase_prev_mention(df_test, use_percentage=True))
        df_ref_test = df_test.loc[df_test['Stanford_PoS'].isin(REFERRING_EXP_POS)].copy()
        print("# words in test:", len(df_test), " # referring expressions in test:", len(df_ref_test))

    # Add these columns using Amaan's function.
    # IP_Pos_Normalized: the normalized position of the token within its intonational phrase
    # IP_Prev_Mentions: % of all ref.expressions in an into.phrase that have been mentioned before
    # IP_Length: length of the Intonational Phrase the token is a part of
    # df_train = df_train.join(num_tokens_intonational_phrase_prev_mention(df_train, use_percentage=True))

    if 'games' in args.train or 'games' in args.test: # games missing some columns
        feat_names = ["syntax/pos", "morph", "supertag", "mentions"]
    else:
        feat_names = ["syntax/pos", "morph", "supertag", "mentions", "punctuation", "NER"]

    if 'burnc' in args.train or 'burnc' in args.test:
        feat_names.append('position')
    else:
        feat_names.append('turn/task')
    start, end = args.range
    start = len(feat_names) if start == -1 else start
    end = len(feat_names) if end == -1 else end
    featsets = generate_featsets(feat_names, start, end)

    if not args.test:
        print("##### ML experiments on all words: #####")
        for t in featsets.keys():
            print("## " + t)

            X, y, cols = process_data(df_train, featsets[t], args.task)
            print('{} columns'.format(len(cols)))
            imputer = sklearn.impute.SimpleImputer(strategy='most_frequent')
            X = imputer.fit_transform(X)
            run_experiments(X, y, cols, pos_label, print_rank=args.print_rank)
            print()
    else:
        print("##### Evaluation ML experiments on all words: #####")
        for t in featsets.keys():
            print("## " + t)
            if not args.test_all: # 75/25 split
                df_train, _ = train_test_split(df_train, random_state=1)
                _, df_test = train_test_split(df_test, random_state=1)
                print('testing on a size {} subset of test set'.format(len(df_test)))
            else:
                print('testing on all {} examples from test set'.format(len(df_test)))

            X_train, y_train, cols_train = process_data(df_train, featsets[t], args.task)
            X_test, y_test, cols_test = process_data(df_test, featsets[t], args.task)


            # Add columns to X_train and X_test so they have identical columns.
            train_set, test_set = set(cols_train), set(cols_test)
            cols = train_set & test_set
            excluded_cols = train_set.symmetric_difference(test_set)
            cols = sorted(list(cols))
            print('{} common columns, {} excluded columns'.format(len(cols), len(excluded_cols)))
            X_train = X_train.reindex(columns=cols, fill_value=0)
            X_test = X_test.reindex(columns=cols, fill_value=0)

            imputer = sklearn.impute.SimpleImputer(strategy="most_frequent")
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.fit_transform(X_test)
            run_experiments_eval(X_train, X_test, y_train, y_test, cols, pos_label, print_rank=args.print_rank)
            print()
