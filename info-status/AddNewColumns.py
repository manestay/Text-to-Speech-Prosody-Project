import pandas as pd
import math
import numpy as np
import datetime

pd.options.mode.chained_assignment = None
# BIGTABLEFILE = "games-data-20180217.csv"
BIGTABLEFILE = "games-data-20180223.csv"
TODAY = datetime.date.today().strftime("%Y%m%d")
CSV_EXTENSTION = ".csv"
NEW_TABLE_PREFIX = "extended-games-data-"

class AddNewColumns(object):

    def __init__(self):
        self.bigtable_file = BIGTABLEFILE
        self.bigtable = pd.read_csv(BIGTABLEFILE)

    '''
    Function iterates through table and groups phrases based on consecutive matching
    Coreference_IDs. Returns a dictionary of tuples indexed by Coreference ID where
    each tuple has the
    (phrase, phrase_end_time, table_indicies_of_phrase_words, PoS_of_the_last_phrase_word)
    '''
    def getPhraseInformation(self):
        # Load csv and remove rows without Coreference_IDs
        df = self.bigtable[['word_end_time', 'word', 'Coreference_IDs', 'Stanford_PoS']]
        truncated = df[df.Coreference_IDs.notnull()]

        # Track information about previous mentions in prior rows
        phrase_end_time, previous_word, previous_coref_id, pos = truncated.iloc[0]
        previous_index = 0
        phrase = previous_word
        indices = []
        phrase_tuples = dict()

        # Iterate through dataframe
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

        return phrase_tuples

    '''
    Function takes phrase tuples from every Coreference ID and determines whether
    phrases are an explicit or implicit match. Adds information pertaining to
    previous explict, implicit, and (explict or implicit) word_end_time, PoS, and
    counts
    '''
    def getMentions(self):

        num_rows = len(self.bigtable)
        phrase_tuples = self.getPhraseInformation()

        # Keep track of recent mentions
        recent_mentions = [None] * num_rows
        explicit_mentions = [None] * num_rows
        implicit_mentions = [None] * num_rows

        # Keep track of PoS
        last_pos = [None] * num_rows
        explicit_pos = [None] * num_rows
        implicit_pos = [None] * num_rows

        # Keep track of mention counts
        num_mentions = [None] * num_rows
        num_exp_mentions = [None] * num_rows
        num_imp_mentions = [None] * num_rows

        for key in phrase_tuples.keys():
            phrases = sorted(phrase_tuples[key], key = lambda x: x[1])

            # Start from second phrase as first can't have a previous mention
            for i in range(1, len(phrases)):

                last_explicit_mention, last_implicit_mention = (None, None)
                last_explicit_pos, last_implicit_pos = (None, None)
                explicit_count, implicit_count = (1, 0)

                for j in range(i):
                    # If explicit mention
                    if phrases[i][0] == phrases[j][0]:
                        last_explicit_mention = phrases[j][1]
                        last_explicit_pos = phrases[j][3]
                        explicit_count += 1
                    # Else is implicit mention
                    else:
                        last_implicit_mention = phrases[j][1]
                        last_implicit_pos = phrases[j][3]
                        implicit_count += 1

                for index in phrases[i][2]:
                    recent_mentions[index - 1] = phrases[i - 1][1]
                    last_pos[index - 1] = phrases[i - 1][3]

                    explicit_mentions[index - 1] = last_explicit_mention
                    explicit_pos[index - 1] = last_explicit_pos

                    implicit_mentions[index - 1] = last_implicit_mention
                    implicit_pos[index - 1] = last_implicit_pos

            for i in range(0, len(phrases)):
                for index in phrases[i][2]:
                    num_mentions[index - 1] = len(phrases)
                    num_exp_mentions[index - 1] = explicit_count
                    num_imp_mentions[index - 1] = implicit_count

        column_data_pair = [    (recent_mentions, 'Most_Recent_Mention'),
                                (explicit_mentions, 'Recent_Explicit_Mention'),
                                (implicit_mentions, 'Recent_Implicit_Mention'),
                                (last_pos, 'Most_Recent_Mention_PoS'),
                                (explicit_pos, 'Recent_Explicit_Mention_PoS'),
                                (implicit_pos, 'Recent_Implicit_Mention_PoS'),
                                (num_mentions, 'Number_Of_Coref_Mentions'),
                                (num_exp_mentions, 'Number_Of_Explicit_Mentions'),
                                (num_imp_mentions, 'Number_Of_Implicit_Mentions')
                            ]

        for pair in column_data_pair:
            self.addColumnToDataFrame(pd.Series(pair[0]), pair[1])

    '''
    Function iterates through table and generates unique intonation phrase IDs
    for each intonation phrase in the table.
    '''
    def getIntonationalPhrases(self):
        df = self.bigtable[['word', 'word_tobi_break_index', 'word_tobi_boundary_tone']]

        curr_id = 0
        phrase_ids = [None] * len(df)

        for index, row in df.iterrows():
            if row['word_tobi_break_index'] == "3p" or row['word_tobi_boundary_tone'] != "_":
                curr_id += 1
                phrase_ids[index] = curr_id
            else:
                phrase_ids[index] = curr_id

        self.addColumnToDataFrame(pd.Series(phrase_ids), 'Intonational_Phrase_ID')

    '''
    Adds a column to a dataframe.
    :param series: pandas Series to be added to the table
    :param column_name: Name of column to be added to the table passed in as a
    string
    '''
    def addColumnToDataFrame(self, series, column_name):
        self.bigtable.insert(loc = self.bigtable.shape[1], column = column_name, value = series.values)

    '''
    Writes table to csv file
    '''
    def saveTable(self):
        self.bigtable.to_csv(NEW_TABLE_PREFIX + TODAY + CSV_EXTENSTION)

if __name__ == '__main__':
    columns = AddNewColumns()
    columns.getMentions()
    columns.getIntonationalPhrases()
    columns.saveTable()
