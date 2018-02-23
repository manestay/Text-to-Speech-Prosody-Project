import pandas as pd
import math
import numpy as np
import datetime

pd.options.mode.chained_assignment = None
# BIGTABLEFILE = "new-big-table.csv"
BIGTABLEFILE = "games-data-20180217.csv"
TODAY = datetime.date.today().strftime("%Y%m%d")
CSV_EXTENSTION = ".csv"
NEW_TABLE_PREFIX = "games-data-"

class AddNewColumns(object):

    def __init__(self):
        self.bigtable_file = BIGTABLEFILE
        self.bigtable = pd.read_csv(BIGTABLEFILE)

    def getMentions(self):

        # Load csv and remove rows without Coreference_IDs
        df = columns.bigtable[['word_end_time', 'word', 'Coreference_IDs', 'Stanford_PoS']]
        truncated = df[df.Coreference_IDs.notnull()]

        # Track information about previous mentions in prior rows
        phrase_end_time, previous_word, previous_coref_id, pos = truncated.iloc[0]
        previous_index = 0
        phrase = previous_word
        indices = []
        phrase_tuples = dict()

        # Iterate through datafram
        for index, row in truncated.iterrows():

            # If current row has same coref_ID as previous row
            if row['Coreference_IDs'] == previous_coref_id and previous_index == index - 1:
                phrase += row['word'] + ' '
                phrase_end_time = row['word_end_time']
                pos = row['Stanford_PoS']
                indices.append(index + 1)

            else:
                # Add information about past mention if previous rows to dictionary
                mention_info = (phrase.rstrip(), float(phrase_end_time), indices, pos)

                # Add phrase information to dictionary
                if previous_coref_id in phrase_tuples.keys():
                    phrase_tuples[previous_coref_id].append(mention_info)
                else:
                    phrase_tuples[previous_coref_id] = [mention_info]

                # Reset data
                phrase_end_time = row['word_end_time']
                indices = []
                indices.append(index + 1)
                phrase = row['word'] + ' '
                pos = row['Stanford_PoS']

            previous_coref_id = row['Coreference_IDs']
            previous_index = index

        # Keep track of recent mentions
        recent_mentions = [None] * len(df)
        explicit_mentions = [None] * len(df)
        implicit_mentions = [None] * len(df)
        last_pos = [None] * len(df)
        explicit_pos = [None] * len(df)
        implicit_pos = [None] * len(df)

        for key in phrase_tuples.keys():
            phrases = sorted(phrase_tuples[key], key = lambda x: x[1])

            # Start from second phrase as first can't have a previous mention
            for i in range(1, len(phrases)):

                last_explicit_mention, last_implicit_mention = (None, None)
                last_explicit_pos, last_implicit_pos = (None, None)

                for j in range(i):
                    # If explicit mention
                    if phrases[i][0] == phrases[j][0]:
                        last_explicit_mention = phrases[j][1]
                        last_explicit_pos = phrases[j][3]
                    # Else is implicit mention
                    else:
                        last_implicit_mention = phrases[j][1]
                        last_implicit_pos = phrases[j][3]

                for index in phrases[i][2]:
                    recent_mentions[index - 1] = phrases[i - 1][1]
                    last_pos[index - 1] = phrases[i - 1][3]

                    explicit_mentions[index - 1] = last_explicit_mention
                    explicit_pos[index - 1] = last_explicit_pos

                    implicit_mentions[index - 1] = last_implicit_mention
                    implicit_pos[index - 1] = last_implicit_pos

        rm = pd.Series(recent_mentions)
        em = pd.Series(explicit_mentions)
        im = pd.Series(implicit_mentions)
        lp = pd.Series(last_pos)
        ep = pd.Series(explicit_pos)
        ip = pd.Series(implicit_pos)

        # Add information to and write csv
        self.bigtable.insert(loc = 36, column = 'Most_Recent_Mention', value = rm.values)
        self.bigtable.insert(loc = 37, column = 'Recent_Explicit_Mention', value = em.values)
        self.bigtable.insert(loc = 38, column = 'Recent_Implicit_Mention', value = im.values)
        self.bigtable.insert(loc = 39, column = 'Recent_Explicit_Mention_PoS', value = ep.values)
        self.bigtable.insert(loc = 40, column = 'Recent_Implicit_Mention_PoS', value = ip.values)
        self.bigtable.insert(loc = 41, column = 'Most_Recent_Mention_PoS', value = lp.values)
        self.bigtable.to_csv("added-big-table.csv")

    def getIntonationalPhrases(self):
        df = columns.bigtable[['word', 'word_tobi_break_index', 'word_tobi_boundary_tone']]

        curr_id = 0
        phrase_ids = [None] * len(df)

        for index, row in df.iterrows():
            if row['word_tobi_break_index'] == "3p" or row['word_tobi_boundary_tone'] != "_":
                curr_id += 1
                phrase_ids[index] = curr_id
            else:
                phrase_ids[index] = curr_id

        pid = pd.Series(phrase_ids)

        self.bigtable.insert(loc = self.bigtable.shape[1], column = 'Intonational_Phrase_ID', value = pid.values)
        self.bigtable.to_csv(NEW_TABLE_PREFIX + TODAY + CSV_EXTENSTION)

columns = AddNewColumns()
# columns.getMentions()
columns.getIntonationalPhrases()
