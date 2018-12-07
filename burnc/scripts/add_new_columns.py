'''
This script generates the following columns:

Most_Recent_Mention
Recent_Explicit_Mention
Recent_Implicit_Mention
Most_Recent_Mention_PoS
Recent_Explicit_Mention_PoS
Recent_Implicit_Mention_PoS
Number_Of_Coref_Mentions
Number_Of_Explicit_Mentions
Number_Of_Implicit_Mentions
Most_Recent_Mention_Syntactic_Function
Recent_Explicit_Mention_Syntactic_Function
Recent_Implicit_Mention_Syntactic_Function
Far_Back_Mention
'''

import os
import glob
import math
import datetime
import numpy as np
import pandas as pd
from example_config import config
from collections import namedtuple

SESSION = 'session'
CSV_EXTENSION = '.csv'
CSV_DIR = config['csv_dir']
SUFFIX = config['combine_suffix']
PREFIX = config['old_table_prefix']
TABLE_NAME = config['new_table_name']
CSV_MENTION_DIR = config['csv_mention_dir']
NEW_TABLE_PREFIX = config['new_table_prefix']

'''
'Missing' files
'''
# files with no data
EMPTY_FILES = [('speakerf2','session15'),('speakerf2','session22'),('speakerf3','session6')]
# files with no coreference ids
NO_COREFS_FILES = [('speakerf1','session2'),('speakerf3','session3'),('speakerf3','session4')]

pd.options.mode.chained_assignment = None
MentionInfo = namedtuple('MentionInfo', ['phrase', 'indices','PoS_last', 'sf_last'])

class AddNewColumns(object):

  def __init__(self, table_name=None):
    self.bigtable = pd.read_csv(table_name or TABLE_NAME)
    self.no_corefs_in_table = False
    self.no_corefs_num_rows = 0

  '''
  Function iterates through table and groups phrases based on consecutive matching
  Coreference_IDs. Returns a dictionary of namedtuples indexed by Coreference ID where
  each namedtuple has the following 4 fields:
  (phrase, table_indices_of_phrase_words, PoS_of_last_phrase_word, syntactic_function_of_last_phrase_word)
  '''
  def getPhraseInformation(self):
    # Load csv and remove rows without Coreference_IDs
    df = self.bigtable[['word', 'Coreference_IDs', 'word_pos_tag', 'syntactic_function']]
    truncated = df[df.Coreference_IDs.notnull()]
    phrase_tuples = dict()

    if truncated.empty:
      self.no_corefs_in_table = True
      self.no_corefs_num_rows = df.shape[0]
      return

    # Iterate through dataframe
    for index, row in truncated.iterrows():
      coref_id = row['Coreference_IDs']
      mention_info = MentionInfo(row['word'],[index + 1],row['word_pos_tag'],row['syntactic_function'])
      if coref_id in phrase_tuples.keys():
        phrase_tuples[coref_id].append(mention_info)
      else:
        phrase_tuples[coref_id] = [mention_info]

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

    # Keep track of syntactic Functions
    last_sf = [None] * num_rows
    explicit_sf = [None] * num_rows
    implicit_sf = [None] * num_rows

    # Keep track of mention counts
    num_mentions = [None] * num_rows
    num_exp_mentions = [None] * num_rows
    num_imp_mentions = [None] * num_rows
    far_back_mention = [None] * num_rows

    if self.no_corefs_in_table:
      column_data_pair = [
                          (['']*self.no_corefs_num_rows, 'Most_Recent_Mention'),
                          (['']*self.no_corefs_num_rows, 'Recent_Explicit_Mention'),
                          (['']*self.no_corefs_num_rows, 'Recent_Implicit_Mention'),
                          (['']*self.no_corefs_num_rows, 'Most_Recent_Mention_PoS'),
                          (['']*self.no_corefs_num_rows, 'Recent_Explicit_Mention_PoS'),
                          (['']*self.no_corefs_num_rows, 'Recent_Implicit_Mention_PoS'),
                          (['']*self.no_corefs_num_rows, 'Number_Of_Coref_Mentions'),
                          (['']*self.no_corefs_num_rows, 'Number_Of_Explicit_Mentions'),
                          (['']*self.no_corefs_num_rows, 'Number_Of_Implicit_Mentions'),
                          (['']*self.no_corefs_num_rows, 'Most_Recent_Mention_Syntactic_Function'),
                          (['']*self.no_corefs_num_rows, 'Recent_Explicit_Mention_Syntactic_Function'),
                          (['']*self.no_corefs_num_rows, 'Recent_Implicit_Mention_Syntactic_Function'),
                          (['']*self.no_corefs_num_rows, 'Far_Back_Mention')
                        ]
    else:

      for key in phrase_tuples.keys():
        phrases = sorted(phrase_tuples[key], key=lambda x: x.indices[0])
        explicit_count, implicit_count = (1, 0)

        # Set first phrase as first explicit mention
        for index in phrases[0].indices:
          (recent_mentions[index-1], explicit_mentions[index-1]) = (index,index)
          (last_pos[index-1], explicit_pos[index-1]) = (phrases[0].PoS_last, phrases[0].PoS_last)
          (last_sf[index-1], explicit_sf[index-1]) = (phrases[0].sf_last, phrases[0].sf_last)

        # Set all subsequenct mentions
        for i in range(1, len(phrases)):

          last_explicit_mention, last_implicit_mention = (None, None)
          last_explicit_pos, last_implicit_pos = (None, None)
          last_explicit_sf, last_implicit_sf = (None, None)
          explicit_count, implicit_count = (1,0)
          for j in range(i):
            # If explicit mention
            if phrases[i].phrase == phrases[j].phrase:
              last_explicit_mention = phrases[j].indices[0]
              last_explicit_pos = phrases[j].PoS_last
              last_explicit_sf = phrases[j].sf_last
              explicit_count += 1
            # Else is implicit mention
            else:
              last_implicit_mention = phrases[j].indices[0]
              last_implicit_pos = phrases[j].PoS_last
              last_implicit_sf = phrases[j].sf_last
              implicit_count += 1

          for index in phrases[i].indices:
            recent_mentions[index - 1] = phrases[i - 1].indices[0]
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
            num_exp_mentions[index - 1] = len([mention for mention in phrases if mention.phrase == phrases[i].phrase])
            num_imp_mentions[index - 1] = num_mentions[index - 1] - num_exp_mentions[index - 1]

            far_back_mention[index - 1] = 0 if i == 0 else index - phrases[i-1].indices[0]

      column_data_pair = [
                            (recent_mentions, 'Most_Recent_Mention'),
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
                            (implicit_sf, 'Recent_Implicit_Mention_Syntactic_Function'),
                            (far_back_mention, 'Far_Back_Mention')
                          ]

    for pair in column_data_pair:
      if pair[1] in self.bigtable.columns:
        print('skipping {}, already exists in dataframe'.format(pair[1]))
        continue
      self.addColumnToDataFrame(pd.Series(pair[0]), pair[1])

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
  def saveTable(self,new_file_id):
    self.bigtable.to_csv(CSV_MENTION_DIR + NEW_TABLE_PREFIX + '_' + new_file_id + CSV_EXTENSION, index=False)


  def getMetadataColumns(self):
    """
    Adds metadata columns, including speaker_id, story_id
    """
    df = self.bigtable
    df['speaker_id'] = df['file_id'].str.slice(0, 3)
    df['story_id'] = df['file_id'].str.slice(0, 6)

  def getSessionColumns(self):
    df = self.bigtable
    df['total_number_of_words_in_story'] = df.groupby('story_id')['story_id'].transform('count')
    df['word_number_in_story'] =  df.groupby('story_id').cumcount() + 1
    df['total_number_of_words_in_paragraph'] = df.groupby('file_id')['file_id'].transform('count')
    df['word_number_in_paragraph'] =  df.groupby('file_id').cumcount() + 1

def main(prefix, suffix):
  global TABLE_NAME
  os.makedirs(CSV_MENTION_DIR,exist_ok=True)
  csvs = glob.glob(CSV_DIR + '{}_speaker*_session*{}'.format(prefix, suffix))
  empty_files = list(map(lambda x: CSV_DIR + '{}_{}_{}{}'.format(prefix,x[0],x[1],suffix),EMPTY_FILES))
  for filename in sorted(csvs,key=lambda x: (x.split('_')[1],int(x.split('_')[2][len(SESSION):]))):

    if filename in empty_files:
      continue

    TABLE_NAME = filename
    new_file_id = '_'.join(filename.split('_')[1:3])

    columns = AddNewColumns()
    columns.getPhraseInformation()
    columns.getMentions()
    columns.getMetadataColumns()
    columns.getSessionColumns()
    columns.saveTable(new_file_id)


if __name__ == '__main__':
  main(PREFIX,SUFFIX)
