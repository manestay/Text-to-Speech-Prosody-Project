'''
This file converts data from BigTable to a text file that can be read in by
StanfordNLP, and allows for writing data from StanfordNLP back into the bigtable.
'''
from enum import Enum
import pandas as pd
import string

CURRENT_SPEAKER = 'speaker1'
FILLERS = ['um','uh','uh-huh','hm','ah','mm','mmhm']
HYPHEN = '-'
SESSION_NUMBER = 'session_number'
SPEAKER_A = 'A'
START_TIME = 'word_start_time'
TABLE_NAME = 'big-table.csv'
TURN_INDEX = 'word_number_in_turn'
TURN_LENGTH = 'total_number_of_words_in_turn'
WORD = 'word'

'''
OrderType represents different options for organizing turns from the BigTables.
'''
class OrderType(Enum):
    SPEAKER_A = 1
    SPEAKER_B = 2
    INTERPOLATED = 3

'''
OrganizedBigTable correlates information from StanfordNLP to the Bigtable
by arranging the bigtable in ways that make it conducive for processing by StanfordNLP,
and offering methods to write information gotten from Stanford to the bigtable.
'''
class OrganizedBigTable(object):
    '''
    Constructor for OrganizedBigTable.
    :param: session_number the session number for which to organize the BigTable.
    '''
    def __init__(self, session_number):
        self.session_number = session_number
        self.df = pd.read_table(TABLE_NAME, sep = ',')
        self.spA_turns, self.spB_turns, self.interpolated_turns = _orderBigtableRows(self.df, session_number)

    '''
    Writes the text of the bigtable a file for processing by Stanford.
    :param order_type: how to order the text of the bigtable into turns
    '''
    def exportToFile(self, order_type):
        text = _turnsToText(self.spA_turns) if order_type == OrderType.SPEAKER_A \
               else _turnsToText(self.spB_turns) if order_type == OrderType.SPEAKER_B \
               else _turnsToText(self.interpolated_turns)
        target = open(str(self.session_number).zfill(2) + '_' + order_type.name + '.txt', 'w')
        target.write(text)
        target.close()

    '''
    Takes information about this table ordered according to the order type, and
    adds it as columns to the bigtable.
    :param order_type: the OrderType of the text file Stanford processed
    :param column_data: The data with which to populate the new column. Each
    element of the list should be a 2-element tuple, with the word at the 0th
    index, and the data for the new column in the following index.
    :param column_names: the names to give the new column.
    '''
    def addColumnToDataFrame(self, order_type, column_data, column_name):

        turns = self.spA_turns if order_type == OrderType.SPEAKER_A \
                else self.spB_turns if order_type == OrderType.SPEAKER_B \
                else self.interpolated_turns

        bigtable_rows = [row for turn in turns for row in turn[1]]

        stanford_index_cur = 0

        # add to the table column
        for row in bigtable_rows:
            bigtable_word = row[WORD]
            bigtable_word_char_count = len(bigtable_word)
            stanford_char_count = 0
            stanford_index_start = stanford_index_cur
            # print column_data[stanford_index_cur], bigtable_word
            # find the range of indices in Stanford that correspond to one word in the bigtable
            while (stanford_char_count < bigtable_word_char_count and
                   stanford_index_cur < len(column_data) - 1):
                stanford_char_count += len(column_data[stanford_index_cur][0])
                stanford_index_cur += 1

            # Concatenate data from Stanford so can be placed in one row when necessary
            column_datum = ''
            for i in range(stanford_index_start, stanford_index_cur):
                out = column_data[i][1].strip().translate(None, string.punctuation)
                column_datum += '_' + out if (out != '' and i != stanford_index_start) else out

            self.df.loc[self.df.index[int(row.name)], column_name] = column_datum

    def saveToCSV(self):
        self.df.to_csv('big-table.csv', sep=',', index=False)

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

'''
Represents the rows of the bigtables ordered in the arrangement they are ordered
for Stanford.
:return: 3 lists, one with speaker A's turns organized by start time,
second with Speaker B's sorted by start time, third with the interpolated turns.
'''
def _orderBigtableRows(df, session_number):
    spA_rows, spB_rows = _getSortedSpeakerRows(session_number, df)
    spA_turns = sorted(_findTurns(spA_rows), key=lambda x: x[0])
    spB_turns = sorted(_findTurns(spB_rows), key=lambda x: x[0])
    interpolated_turns = sorted(spA_turns + spB_turns, key=lambda x: x[0])
    return spA_turns, spB_turns, interpolated_turns

'''
Arranges ordered rows of a speaker into turns.
:param speaker_rows: the rows of the speaker
:return: a list of turns, where each turn is an ordered list of rows
'''
def _findTurns(speaker_rows):
    turns = []
    turn_list = []
    for row in speaker_rows:
        if row[WORD] not in FILLERS and row[WORD][-1] != HYPHEN:
            turn_list.append(row)
            if row[TURN_INDEX] == row[TURN_LENGTH]:
                turns.append([turn_list[0][START_TIME],turn_list])
                turn_list = []
    return turns

'''
Separates words spoken by Speaker A and Speaker B, and sorts them by time.
:param session: the session to sort
:return: two lists, one containing the sorted rows of speaker A, the second B
'''
def _getSortedSpeakerRows(session, df):
    spA_rows, spB_rows = [], []
    j = 0
    for index, row in df.iterrows():
        if row[SESSION_NUMBER] == int(session):
            if row[CURRENT_SPEAKER] == SPEAKER_A:
                spA_rows.append(row)
            else: # speaker B
                spB_rows.append(row)
        j += 1

    spA_rows = sorted(spA_rows, key=lambda x: x[START_TIME])
    spB_rows = sorted(spB_rows, key=lambda x: x[START_TIME])
    return spA_rows, spB_rows
