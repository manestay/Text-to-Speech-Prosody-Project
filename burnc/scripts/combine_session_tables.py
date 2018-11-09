import glob
import math
import datetime
import numpy as np
import pandas as pd
from example_config import config

SESSION = 'session'
TODAY = config['date']
CSV_EXTENSION = '.csv'
PREFIX = config['new_table_prefix']
NEW_TABLE_NAME = config['new_table_name']
CSV_MENTION_DIR = config['csv_mention_dir']

def combine(prefix, new_table_name='', date=TODAY):
  if not new_table_name:
    new_table_name = '{}'.format(NEW_TABLE_NAME)
    print('Combining csv files into {}'.format(new_table_name))
  csvs = glob.glob(CSV_MENTION_DIR + '{}_*_*{}'.format(prefix, CSV_EXTENSION))

  df_list = []
  for filename in sorted(csvs,key=lambda x: (x.split('_')[2],int(x.split('_')[3][len(SESSION):-4]))):
    df_list.append(pd.read_csv(filename))
  full_df = pd.concat(df_list)

  full_df.to_csv(new_table_name, index=False)
  return new_table_name

def main(prefix):
  combine(prefix)
if __name__ == '__main__':
    combine(PREFIX)
