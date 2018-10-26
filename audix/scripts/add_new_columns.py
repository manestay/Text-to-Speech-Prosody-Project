'''
This script generates the following columns:

Intonational_Phrase_ID
Most_Recent_Mention
Recent_Explicit_Mention
Recent_Implicit_Mention
Most_Recent_Mention_PoS
Recent_Explicit_Mention_PoS
Recent_Implicit_Mention_PoS
Number_Of_Coref_Mentions
Number_Of_Explicit_Mentions
Number_Of_Implicit_Mentions
syntactic_function_prev_explicit_mention
syntactic_function_prev_implicit_mention
syntactic_function_prev_mention
'''

import pandas as pd
import math
import numpy as np
import datetime
from collections import namedtuple
from example_config import config
from nltk.corpus import cmudict
import syllapy

pd.options.mode.chained_assignment = None

TABLE_NAME = config['new_table_name']
NEW_TABLE_PREFIX = config['new_table_prefix']
TODAY = config['date']

CSV_EXTENSION = ".csv"
MentionInfo = namedtuple('MentionInfo', ['phrase', 'start_time', 'token_id',
                                         'indices','PoS_last', 'sf_last'])

class AddNewColumns(object):

    def __init__(self):
        self.bigtable_file = TABLE_NAME
        self.bigtable = pd.read_csv(TABLE_NAME)

    '''
    Function iterates through table and groups phrases based on consecutive matching
    Coreference_IDs. Returns a dictionary of namedtuples indexed by Coreference ID where
    each namedtuple has the following 5 fields:
    (phrase, phrase_start_time, table_indices_of_phrase_words,
     PoS_of_last_phrase_word, syntactic_function_of_last_phrase_word)
    '''
    def getPhraseInformation(self):
        # Load csv and remove rows without Coreference_IDs
        df = self.bigtable[['word_start_time', 'word', 'Coreference_IDs', 'Stanford_PoS',
                            'syntactic_function', 'token_id']]
        truncated = df[df.Coreference_IDs.notnull()]

        # Track information about previous mentions in prior rows
        phrase_start_time, previous_word, previous_coref_id, pos, sf, token_id = truncated.iloc[0]
        previous_index = 0
        phrase = previous_word
        indices = []
        phrase_tuples = dict()

        # Iterate through dataframe
        for index, row in truncated.iterrows():

            # If current row has same coref_ID as previous row
            if row['Coreference_IDs'] == previous_coref_id and previous_index == index - 1:
                phrase += row['word'] + ' '
                phrase_start_time = row['word_start_time']
                token_id = row['token_id']
                pos = row['Stanford_PoS']
                sf = row['syntactic_function']
                indices.append(index + 1)

            else:
                # Add information about past mention if previous rows to dictionary
                mention_info = MentionInfo(phrase.rstrip(), float(phrase_start_time), token_id,
                                           indices, pos, sf)

                # Add phrase information to dictionary
                if previous_coref_id in phrase_tuples.keys():
                    phrase_tuples[previous_coref_id].append(mention_info)
                else:
                    phrase_tuples[previous_coref_id] = [mention_info]

                # Reset data
                phrase_start_time = row['word_start_time']
                token_id = row['token_id']
                indices = []
                indices.append(index + 1)
                phrase = row['word'] + ' '
                pos = row['Stanford_PoS']
                sf = row['syntactic_function']

            previous_coref_id = row['Coreference_IDs']
            previous_index = index

        return phrase_tuples

    '''
    Function takes phrase tuples from every Coreference ID and determines whether
    phrases are an explicit or implicit match. Adds information pertaining to
    previous explict, implicit, and (explict or implicit) word_start_time, PoS, and
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

        # Keep track of syntactic Functions
        last_sf = [None] * num_rows
        explicit_sf = [None] * num_rows
        implicit_sf = [None] * num_rows

        # Keep track of mention counts
        num_mentions = [None] * num_rows
        num_exp_mentions = [None] * num_rows
        num_imp_mentions = [None] * num_rows

        for key in phrase_tuples.keys():
            # print(phrase_tuples[key])
            phrases = sorted(phrase_tuples[key], key=lambda x: x.token_id)

            # Start from second phrase as first can't have a previous mention
            for i in range(1, len(phrases)):

                last_explicit_mention, last_implicit_mention = (None, None)
                last_explicit_pos, last_implicit_pos = (None, None)
                last_explicit_sf, last_implicit_sf = (None, None)
                explicit_count, implicit_count = (1, 0)

                for j in range(i):
                    # If explicit mention
                    if phrases[i].phrase == phrases[j].phrase:
                        last_explicit_mention = phrases[j].start_time
                        last_explicit_pos = phrases[j].PoS_last
                        last_explicit_sf = phrases[j].sf_last
                        explicit_count += 1
                    # Else is implicit mention
                    else:
                        last_implicit_mention = phrases[j].start_time
                        last_implicit_pos = phrases[j].PoS_last
                        last_implicit_sf = phrases[j].sf_last
                        implicit_count += 1

                for index in phrases[i].indices:
                    recent_mentions[index - 1] = phrases[i - 1].start_time
                    last_pos[index - 1] = phrases[i - 1].PoS_last
                    last_sf[index - 1] = phrases[i - 1].sf_last
                    explicit_mentions[index - 1] = last_explicit_mention
                    explicit_pos[index - 1] = last_explicit_pos
                    explicit_sf[index - 1] = last_explicit_sf

                    implicit_mentions[index - 1] = last_implicit_mention
                    implicit_pos[index - 1] = last_implicit_pos
                    implicit_sf[index - 1] = last_implicit_sf

            for i in range(0, len(phrases)):
                for index in phrases[i].indices:
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
                                (num_imp_mentions, 'Number_Of_Implicit_Mentions'),
                                (last_sf, 'Most_Recent_Mention_Syntactic_Function'),
                                (explicit_sf, 'Recent_Explicit_Mention_Syntactic_Function'),
                                (implicit_sf, 'Recent_Implicit_Mention_Syntactic_Function')
                            ]

        for pair in column_data_pair:
            if pair[1] in self.bigtable.columns:
                print('skipping {}, already exists in dataframe'.format(pair[1]))
                continue
            self.addColumnToDataFrame(pd.Series(pair[0]), pair[1])

    '''
    Function iterates through table and generates unique intonation phrase IDs
    for each intonation phrase in the table.
    '''
    def getIntonationalPhrases(self):
        df = self.bigtable[['word', 'session_number', 'word_tobi_boundary_tone', 'intermediate_phrase']]

        curr_id = 0
        phrase_ids = [None] * len(df)

        for index, row in df.iterrows():
            if row['session_number'] != 1:
                next_condition = row['intermediate_phrase'] == 'START'
            else:
                next_condition = pd.notnull(row['word_tobi_boundary_tone'])
            if next_condition:
                curr_id += 1
                phrase_ids[index] = curr_id
            else:
                phrase_ids[index] = curr_id

        if 'Intonational_Phrase_ID' in self.bigtable.columns:
            print('Intonational_Phrase_ID already exists in dataframe, skipping')
            return

        self.addColumnToDataFrame(pd.Series(phrase_ids), 'Intonational_Phrase_ID')

    '''
    Gets the syllable count for each word in the table.
    '''
    def getSyllableCounts(self):
        def syllable_count(word):
            try: # look in cmudict
                return [len(list(y for y in x if y[-1].isdigit())) for x in cmu_d[word.lower()]][0]
            except KeyError: # look in syllapy
                return syllapy.count(word)

        cmu_d = cmudict.dict()
        syllables = self.bigtable['word'].apply(syllable_count)

        self.addColumnToDataFrame(syllables, 'word_number_of_syllables')

    def getBreakIndices(self):
        df = self.bigtable
        # df['break_index'] = np.where(df['word_tobi_boundary_tone'].str.contains('%', na=False), 'B', 'NB')
        df['break_index'] = np.where(df['word_tobi_boundary_tone'].notna(), 'B', 'NB')

    def getNextColumns(self):
        """
        Adds columns for next POS, syntactic function, and NER
        """
        self.bigtable[['next_Stanford_PoS', 'next_syntactic_function', 'next_NER']] = \
            self.bigtable[['Stanford_PoS', 'syntactic_function', 'NER']].shift(-1)

    def addColumnToDataFrame(self, series, column_name):
        '''
        Adds a column to a dataframe.
        :param series: pandas Series to be added to the table
        :param column_name: Name of column to be added to the table passed in as a
        string
        '''
        self.bigtable.insert(loc = self.bigtable.shape[1], column = column_name, value = series.values)


    def saveTable(self):
        '''
        Writes table to csv file.
        '''
        self.bigtable.to_csv(NEW_TABLE_PREFIX + CSV_EXTENSION, index=False)

def main(table_name=''):
    global TABLE_NAME
    if table_name:
        TABLE_NAME = table_name
    columns = AddNewColumns()
    columns.getMentions()
    columns.getIntonationalPhrases()
    columns.getSyllableCounts()
    columns.getBreakIndices()
    columns.getNextColumns()
    columns.saveTable()

if __name__ == '__main__':
    main()
