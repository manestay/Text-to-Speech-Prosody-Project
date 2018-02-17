import pandas as pd
import math
import numpy as np

pd.options.mode.chained_assignment = None
BIGTABLEFILE = "new-big-table.csv"

class AddNewColumns(object):

    def __init__(self):
        self.bigtable_file = BIGTABLEFILE
        self.bigtable = pd.read_csv(BIGTABLEFILE)

    def getMentionsRecency(self):
        df = columns.bigtable[['word_start_time', 'word_end_time', 'word', 'Coreference_IDs']]
        truncated = df[df.Coreference_IDs.notnull()]

        _ , phrase_end_time, previous_word, previous_coref_id = truncated.iloc[0]
        previous_index = 0
        phrase = previous_word
        indices = [1]

        phrase_tuples = dict()

        for index, row in truncated.iterrows():

            # If current row has same coref_ID as previous row
            if row['Coreference_IDs'] == previous_coref_id and previous_index == index - 1:
                phrase += row['word'] + ' '
                phrase_end_time = row['word_end_time']
                indices.append(index + 1)

            else:
                # Add information about past mention if previous rows to dictionary
                mention_info = (phrase.rstrip(), float(phrase_end_time), indices)

                if previous_coref_id in phrase_tuples.keys():
                    phrase_tuples[previous_coref_id].append(mention_info)
                else:
                    phrase_tuples[previous_coref_id] = [mention_info]

                # Reset data
                phrase_end_time = row['word_end_time']
                indices = []
                indices.append(index + 1)
                phrase = row['word'] + ' '

            previous_coref_id = row['Coreference_IDs']
            previous_index = index

        recent_mentions = [None] * len(df)
        explicit_mentions = [None] * len(df)
        implicit_mentions = [None] * len(df)

        for key in phrase_tuples.keys():
            phrases = sorted(phrase_tuples[key], key = lambda x: x[1])

            # Start from second phrase as first can't have a previous mention
            for i in range(1, len(phrases)):

                last_explicit_mention, last_implicit_mention = (None, None)

                for j in range(i):
                    if phrases[i][0] == phrases[j][0]:
                        last_explicit_mention = phrases[j][1]
                    else:
                        last_implicit_mention = phrases[j][1]

                for index in phrases[i][2]:
                    recent_mentions[index - 1] = phrases[i - 1][1]
                    explicit_mentions[index - 1] = last_explicit_mention
                    implicit_mentions[index - 1] = last_implicit_mention

        rm = pd.Series(recent_mentions)
        em = pd.Series(explicit_mentions)
        im = pd.Series(implicit_mentions)

        self.bigtable.insert(loc = 36, column = 'Most_Recent_Mention', value = rm.values)
        self.bigtable.insert(loc = 37, column = 'Recent_Explicit_Mention', value = em.values)
        self.bigtable.insert(loc = 38, column = 'Recent_Implicit_Mention', value = im.values)
        self.bigtable.to_csv("added-big-table.csv")


columns = AddNewColumns()
columns.getMentionsRecency()
