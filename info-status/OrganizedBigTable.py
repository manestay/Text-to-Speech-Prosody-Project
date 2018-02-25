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
TABLE_NAME = 'games-data-20180217.csv'
TURN_INDEX = 'word_number_in_turn'
TURN_LENGTH = 'total_number_of_words_in_turn'
WORD = 'word'

class OrderType(Enum):
    '''
    OrderType represents different options for organizing turns from the BigTables.
    '''
    SPEAKER_A = 1
    SPEAKER_B = 2
    INTERPOLATED = 3
    GIVEN = 4

class OrganizedBigTable(object):
    '''
    OrganizedBigTable correlates information from StanfordNLP to the Bigtable
    by arranging the bigtable in ways that make it conducive for processing by StanfordNLP,
    and offering methods to write information gotten from Stanford to the bigtable.
    '''
    def __init__(self, session_number=None, order_type=OrderType.INTERPOLATED, table_name=TABLE_NAME):
        '''
        Constructor for OrganizedBigTable.
        :param session_number: the session number for which to organize the BigTable. If None,
        organizes by all session numbers in BigTable (e.g. a list from 1 to 12).
        :param order_type: the order_type. Recommended to use GIVEN if unsure.
        :param table_name: name of CSV file to use
        '''
        self.session_number = session_number
        self.table_name = table_name
        self.df = pd.read_table(table_name, sep = ',')
        # self.dfA = self.df[self.df[CURRENT_SPEAKER]=='A'] # views of df, not copies
        # self.dfB = self.df[self.df[CURRENT_SPEAKER]=='B']
        self.order_type = order_type
        if not order_type == OrderType.GIVEN:
            self.spA_turns, self.spB_turns, self.interpolated_turns = _orderBigtableRows(self.df, session_number)
            self.all_turns = None
        else:
            self.spA_turns, self.spB_turns, self.all_turns = _getBigtableRows(self.df, session_number)
            self.interpolated_turns = None

    def updateDataFrame(self, order_type=OrderType.INTERPOLATED):
        '''
        Updates the internal DataFrame with spA_turns, spB_turns, and interpolated_turns data
        :param order_type: how to order the text of the bigtable into turns
        '''
        session = self.session_number
        if order_type.name == "INTERPOLATED":
            organized_df = _getSortedInterpolatedRows(session, self.df)
            self.df = organized_df
            return
        # else SPEAKER_A or SPEAKER_B
        dfA, dfB = _getSortedSpeakerRows(session, self.df)
        if order_type.name == "SPEAKER_A":
            self.dfA = dfA
        else:
            self.dfB = dfB

    def exportToFile(self):
        '''
        Writes the text of the bigtable a file for processing by Stanford.
        :param order_type: how to order the text of the bigtable into turns
        '''
        order_type = self.order_type
        text = _turnsToText(self.spA_turns) if order_type == OrderType.SPEAKER_A \
               else _turnsToText(self.spB_turns) if order_type == OrderType.SPEAKER_B \
               else _turnsToText(self.interpolated_turns) if order_type == OrderType.INTERPOLATED \
               else _turnsToText(self.all_turns)

        if not self.session_number:
            print("cannot use exportToFile without explicit session number; you may have initialized"
                  " OrganizedBigTable with no session_number parameter")
            return
        target = open(str(self.session_number).zfill(2) + '_' + order_type.name + '.txt', 'w')
        target.write(text)
        target.close()

    def addColumnToDataFrame(self, column_data, column_name):
        '''
        Takes information about this table ordered according to the order type, and
        adds it as columns to the bigtable.
        :param order_type: the OrderType of the text file Stanford processed
        :param column_data: The data with which to populate the new column. Each
        element of the list should be a 2-element tuple, with the word at the 0th
        index, and the data for the new column in the following index.
        :param column_names: the names to give the new column.
        '''
        text = _turnsToText(self.spA_turns) if order_type == OrderType.SPEAKER_A \
               else _turnsToText(self.spB_turns) if order_type == OrderType.SPEAKER_B \
               else _turnsToText(self.interpolated_turns) if order_type == OrderType.INTERPOLATED \
               else _turnsToText(self.all_turns)

        bigtable_rows = (row for turn in turns for row in turn[1])

        stanford_index_cur = 0

        # add to the table column
        for row in bigtable_rows:
            bigtable_word = row[WORD]
            bigtable_word_char_count = len(bigtable_word)
            stanford_char_count = 0
            stanford_index_start = stanford_index_cur
            # print(column_data[stanford_index_cur], bigtable_word)
            # find the range of indices in Stanford that correspond to one word in the bigtable
            while (stanford_char_count < bigtable_word_char_count and
                   stanford_index_cur < len(column_data) - 1):
                stanford_char_count += len(column_data[stanford_index_cur][0])
                stanford_index_cur += 1

            # Concatenate data from Stanford so can be placed in one row when necessary
            column_datum = ''
            for i in range(stanford_index_start, stanford_index_cur):
                out = column_data[i][1].strip().translate(str.maketrans('','',string.punctuation))
                column_datum += '_' + out if (out != '' and i != stanford_index_start) else out

            self.df.loc[self.df.index[int(row.name)], column_name] = column_datum

    def saveToCSV(self, order_type=None):
        order_type = order_type or self.order_type
        file_name = self.table_name.split('.')[0]
        df = self.df

        order_name = str(self.order_type).split('.')[1] if order_type else ''
        if order_name:
            file_name += "_{}".format(order_name)
            if order_name == "SPEAKER_A":
                df = self.dfA
            elif order_name == "SPEAKER_B":
                df = self.dfB

        if self.session_number:
            file_name += "_session{}".format(str(self.session_number))
            df = df[df[SESSION_NUMBER] == int(self.session_number)]

        file_name += '_organized.csv'
        df.to_csv(file_name, sep=',', index=False)

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

def _getBigtableRows(df, session_number):
    '''
    Represents the rows of the bigtables ordered in the arrangement they are ordered
    for Stanford. Does not sort anything.
    :return: 2 lists, one with speaker A's turns organized by start time,
    second with Speaker B's sorted by start time.
    '''
    df = df[df[SESSION_NUMBER] == int(session_number)]
    spA_rows = df[df[CURRENT_SPEAKER]=='A'].copy()
    spB_rows = df[df[CURRENT_SPEAKER]=='B'].copy()
    spA_turns = _findTurns(spA_rows)
    spB_turns = _findTurns(spB_rows)
    all_turns = _findTurns(df)
    return spA_turns, spB_turns, all_turns

def _orderBigtableRows(df, session_number):
    '''
    Represents the rows of the bigtables ordered in the arrangement they are ordered
    for Stanford.
    :return: 3 lists, one with speaker A's turns organized by start time,
    second with Speaker B's sorted by start time, third with the interpolated turns.
    '''
    spA_rows, spB_rows = _getSortedSpeakerRows(session_number, df)
    spA_turns = sorted(_findTurns(spA_rows), key=lambda x: (x[1][0]['token_id2'], x[0]))
    spB_turns = sorted(_findTurns(spB_rows), key=lambda x: (x[1][0]['token_id2'], x[0]))
    return spA_turns, spB_turns, interpolated_turns

'''
Arranges ordered rows of a speaker into turns.
:param speaker_rows: the rows of the speaker
:return: a list of turns, where each turn is an ordered list of rows
'''
def _findTurns(speaker_rows):
    turns = []
    turn_list = []
    for idx, row in speaker_rows.iterrows():
        if row[WORD] not in FILLERS and row[WORD][-1] != HYPHEN:
            turn_list.append(row)
            if row[TURN_INDEX] == row[TURN_LENGTH]:
                turns.append([turn_list[0][START_TIME],turn_list])
                turn_list = []
    return turns

'''
Helper method to strip_time from token_id, used for proper sorting.
'''
def _strip_time(text):
    idx = text.rfind('.', 0, text.rfind('.', 0, text.rfind('.')))
    return text[0:idx]

'''
Separates words spoken by Speaker A and Speaker B, and sorts them by time.
:param session: the session to sort, if None then will sort all sessions
:return: two lists, one containing the sorted rows of speaker A, the second B
'''

def _getSortedSpeakerRows(session, df):
    # fix method to properly sort rows

    df_temp = df
    if session:
        df_temp = df[df[SESSION_NUMBER] == int(session)]

    dfA = df_temp[df_temp[CURRENT_SPEAKER]=='A'].copy()
    dfB = df_temp[df_temp[CURRENT_SPEAKER]=='B'].copy()

    dfA['token_id2']= dfA['token_id'].apply(_strip_time)
    dfB['token_id2']= dfB['token_id'].apply(_strip_time)

    dfA = dfA.sort_values(['token_id2',START_TIME],ascending=[True, True])
    dfB = dfB.sort_values(['token_id2',START_TIME],ascending=[True, True])
    return dfA, dfB

def _getSortedInterpolatedRows(session, df):
    df_temp = df
    if session:
        df_temp = df[df[SESSION_NUMBER] == int(session)]

    df['token_id2']= df['token_id'].apply(_strip_time)

    df_interpolated = df.sort_values(['token_id2',START_TIME],ascending=[True, True])
    return df_interpolated
