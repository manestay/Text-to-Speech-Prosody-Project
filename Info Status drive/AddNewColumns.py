import pandas as pd
import math

BIGTABLEFILE = "new-big-table.csv"

class AddNewColumns(object):

    def __init__(self):
        self.bigtable_file = BIGTABLEFILE
        self.bigtable = pd.read_csv(BIGTABLEFILE)

    def getMentionsRecency(self):
        df = columns.bigtable[['word_start_time', 'word_end_time', 'word', 'Coreference_IDs']]

        truncated = df[df.Coreference_IDs.notnull()]

        previous_word = truncated['word'].iloc[0]
        previous_coref_id = truncated['Coreference_IDs'].iloc[0]
        phrase_end_time = 0
        previous_index = 0
        phrase = ''
        indices = []

        phrase_tuples = dict()

        for index, row in truncated.iterrows():

            # If current row has same coref_ID as previous row
            if row['Coreference_IDs'] == previous_coref_id and previous_index == index - 1:
                phrase += row['word'] + ' '
                phrase_end_time = row['word_end_time']
                indices.append(index + 1)

            else:
                # Add information about past mention if previous rows to dictionary

                mention_info = (phrase, float(phrase_end_time), indices)

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

        print(phrase_tuples)

        for key in phrase_tuples.keys():

            corefs_sorted = sorted(phrase_tuples[key], key = lambda x: x[1])
            print(corefs_sorted)

            # print([(corefs_sorted[i - 1][1], corefs_sorted[i][2]) for i in range(1, len(corefs_sorted))])

columns = AddNewColumns()
columns.getMentionsRecency()
