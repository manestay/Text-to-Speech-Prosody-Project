'''
This file converts data from BigTable to a text file that can be read in by
StanfordNLP, and allows for writing data from StanfordNLP back into the bigtable.
'''
from os import path
import pandas as pd
import string
import datetime
from example_config import config

TODAY = config['date']
TABLE_NAME = config['input_table']
TABLE_PREFIX = config['old_table_prefix']

FILLERS = ['um','uh','uh-huh','hm','ah','mm','mmhm']
HYPHEN = '-'
SESSION_NUMBER = 'session_number'
SPEAKER_A = 'A'
START_TIME = 'word_start_time'
TURN_INDEX = 'word_number_in_turn'
TURN_LENGTH = 'total_number_of_words_in_turn'
WORD = 'word'
CSV_EXTENSTION = ".csv"

class OrganizedBigTable(object):
    '''
    OrganizedBigTable correlates information from StanfordNLP to the Bigtable
    by arranging the bigtable in ways that make it conducive for processing by StanfordNLP,
    and offering methods to write information gotten from Stanford to the bigtable.
    '''
    def __init__(self, session_number=None, table_name=TABLE_NAME):
        '''
        Constructor for OrganizedBigTable.
        :param session_number: the session number for which to organize the BigTable.
        :param table_name: name of CSV file to use
        '''
        self.session_number = session_number
        self.table_name = table_name
        self.df = pd.read_table(table_name, sep=',').set_index('token_id')
        if session_number:
            self.limitDataFrameToSession()
        self.all_turns = None

    def limitDataFrameToSession(self):
        self.df = self.df[self.df[SESSION_NUMBER] == int(self.session_number)]
        # TODO: limit turns fields as well

    def get_sentences(self):
        return self.df['sentence'].unique()

    def export_txt(self):
        '''
        Writes the text of the bigtable a file for processing by Stanford.
        '''
        session_number = str(self.session_number).zfill(2)
        target = open('{}_session{}.txt'.format(TABLE_PREFIX, session_number), 'w')
        sentences = self.get_sentences()
        sentences = [x + '\n' for x in sentences]
        target.writelines(sentences)
        target.close()

    def addColumnToDataFrame(self, column_data, column_name, concatenate=True):
        '''
        Takes information about this table and adds it as columns to the bigtable.
        :param column_data: The data with which to populate the new column. Each
        element of the list should be a 2-element tuple, with the word at the 0th
        index, and the data for the new column in the following index.
        :param column_name: the name to give the new column.
        '''
        process_word = lambda x : x.replace('.', '').lower()
        if column_name in self.df:
            print('warning: column {} already exists, overwriting in table'.format(column_name))

        idx = 0
        new_col = []
        for row in self.df.itertuples():
            row_word = process_word(row.word)
            word, item = column_data[idx]
            word = process_word(word)
            # print(row_word, word)
            if row_word == word:
                new_col.append(item)
                idx += 1
                continue
            elif row_word.startswith(word): # possible case of contraction
                word_next, item_next = column_data[idx + 1]
                word_next = process_word(word_next)
                if word + word_next == row_word:
                    if concatenate and item and item_next:
                        new_col.append('{}_{}'.format(item, item_next))
                    elif item:
                        new_col.append(item)
                    elif item_next:
                        new_col.append(item_next)
                    else:
                        new_col.append('')
                    idx += 2
                    continue
            # TODO: handle cases where word.startswith(row_word)? currently using manual corrections in make_audix_csv.py
            idx += 1
            word, item = column_data[idx]
            word = process_word(word)
            if row_word == word:
                new_col.append(item)
                idx += 1
            else: # uncomment to catch typos
                import pdb; pdb.set_trace()


        new_col_series = pd.Series(new_col, index=self.df.index)
        assert len(new_col_series) == self.df.shape[0]
        self.df[column_name] = new_col_series

    def addColumnToDataFrameInPlace(self, values, column_name):
        '''
        Adds a column directly into dataframe without any ordering.
        '''
        if column_name in self.df:
            print('warning: column {} already exists, overwriting in table'.format(column_name))
        num_rows = len(self.df)
        num_values = len(values)
        if num_values < num_rows:
            print('adding column {}, but size was {}, so padding'.format(column_name, num_values))
            values = values + ([None] * (num_rows - num_values))
        elif len(values) > num_rows:
            print('adding column {}, but size was {}, so truncating'.format(column_name, num_values))
            values = values[:num_rows]
        self.df.insert(loc=self.df.shape[1], column=column_name, value=values)

    def saveToCSV(self, print_msg=True):
        file_name = path.splitext(path.basename(self.table_name))[0]
        df = self.df

        if self.session_number:
            session_number = str(self.session_number).zfill(2)
            file_name += "_session{}".format(str(session_number))
            df = df[df[SESSION_NUMBER] == int(session_number)]

        file_name += '.csv'
        if print_msg:
            print('saving {}...'.format(file_name))
        df.to_csv(file_name, sep=',', index=True)

'''
Helper method to organize turns into a text file with sentences.
:param turns: a list of turns, organized by time
:return: a string of text with sentence divisions.
'''
def _turnsToText(turns):
    text = ''
    for turn in turns:
        for row in turn[1]:
            text += ' ' + row[WORD]
        text += '.'
    return text
