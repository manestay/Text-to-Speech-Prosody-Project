'''
This file converts data from BigTable to a text file that can be read in by
StanfordNLP, and allows for writing data from StanfordNLP back into the bigtable.
'''
import re
import string
import pandas as pd
from clean_corefs import * 
from os import path,makedirs
from example_config import config

WORD = 'word'
FILE_ID = 'file_id'
CSV_EXTENSTION = '.csv'
CSV_DIR = config['csv_dir']
PUNCTUATION = 'punctuation'
TEXT_DIR = config['txt_dir']
SESSION_NUMBER = 'session_number'
TABLE_NAME = config['input_table']

class OrganizedBigTable(object):
  '''
  OrganizedBigTable correlates information from StanfordNLP to the Bigtable
  by arranging the bigtable in ways that make it conducive for processing by StanfordNLP,
  and offering methods to write information gotten from Stanford to the bigtable.
  '''
  def __init__(self, session_number, speaker_id, table_name=TABLE_NAME, clean=True):
    '''
    Constructor for OrganizedBigTable.
    :param session_number: the session number for which to organize the BigTable.
    :param speaker_number: the speaker for which to organize the BigTable
    :param table_name: name of CSV file to use
    '''
    self.session_number = session_number
    self.speaker_id = speaker_id
    self.table_name = table_name
    self.df = pd.read_table(table_name, sep = ',')

  def exportToFile(self):
    ''' 
    Creates text files of text from bigtable -- differentiated by session number
    '''
    if not self.session_number:
      print("cannot use exportToFile without explicit session number; you may have initialized"
            "OrganizedBigTable with no session_number parameter")
      return
    if not self.speaker_id:
      print("cannot use exportToFile without explicit speaker id; you may have initialized"
            "OrganizedBigTable with no speaker_id parameter")
      return 
    
    sessions = _orderBigtableRows(self.df, self.speaker_id, self.session_number, clean=True)
    text = _sessionsToText(sessions)
    
    target = open(TEXT_DIR + str(self.speaker_id) + '_' + str(self.session_number) + '.txt', 'w')
    target.write(text)
    target.close()
  
  def addCorefIDsToDataFrame(self, column_data, column_name, session_number):

      '''
      :param session_number: the session number for which the table will be constructed
      :param column_data: The data with which to populate the new column. Each
      element of the list should be a 2-element tuple, with the word at the 0th
      index, and the data for the new column in the following index.
      :param column_names: the names to give the new column.
      '''
      if column_name in self.df:
          print('warning: column {} already exists, overwriting in table'.format(column_name))

      speaker_rows = self.df[self.df.apply(lambda x: _cleanFileID(x[FILE_ID])[0] == session_number 
                              and _cleanFileID(x[FILE_ID])[1] == self.speaker_id, axis=1)]
      bigtable_rows = [row for i,row in speaker_rows.iterrows()]
      
      correct_index = 0
      phase = 0

      for row in bigtable_rows:
        if row[WORD] == column_data[correct_index][0]:
          column_datum = column_data[correct_index][1]
          correct_index += 1
        else:
          incomplete_word = column_data[correct_index][0]
          while row[WORD] != incomplete_word:
            phase += 1
            incomplete_word += column_data[correct_index + phase][0]
          column_datum = column_data[correct_index][1]
          correct_index += phase + 1
          phase = 0
        self.df.loc[self.df.index[int(row.name)], column_name] = column_datum

  def saveToCSV(self):
    makedirs(CSV_DIR, exist_ok=True)
    file_name = path.splitext(self.table_name)[0]
    df = self.df
    if self.session_number:
      session_number = str(self.session_number)
      speaker_id = str(self.speaker_id)
      file_name += "_speaker{}_session{}".format(str(speaker_id),str(session_number))

      df = df[df.apply(lambda x: _cleanFileID(x[FILE_ID])[0] == session_number 
                                  and _cleanFileID(x[FILE_ID])[1] == self.speaker_id, axis=1)]

    file_name += '_organized.csv'
    print('saving {}...'.format(file_name))
    df.to_csv(CSV_DIR + file_name, sep=',', index=False)

def _sessionsToText(sessions):
  '''
  Helper method that organizes text from bigtable into text file, with punctuation. 
  '''
  text = ''
  for row in sessions:
    punctuation = row[PUNCTUATION] if row[PUNCTUATION] == '.' else ''
    text += ' ' + row[WORD] + punctuation
  return text.strip()

def _orderBigtableRows(df, speaker_id, session_number, clean=True):
  '''
  Helper method that filters rows of table based on session speaker
  '''
  speaker_rows = df[df[FILE_ID].str.contains(speaker_id)].copy()
  speaker_sessions = _findSessions(speaker_rows, session_number, clean=clean)
  return speaker_sessions

def _cleanFileID(file_id):
  '''
  Helper method that extracts speaker and session information from file_id
  '''
  speaker_id = list(map(lambda x: x.lstrip('0'),re.split('[absp]',file_id)))[0]
  session_number = list(map(lambda x: x.lstrip('0'),re.split('[absp]',file_id)))[2]
  return session_number,speaker_id

def _findSessions(speaker_rows, session_number, clean=True):
  '''
  Helper method that extracts rows from bigtable basedon session_number 
  '''
  sessions = []
  for _,row in speaker_rows.iterrows():
    session_id = _cleanFileID(row[FILE_ID])[0]
    if str(session_number) == session_id:
      sessions.append(row)
  return sessions

