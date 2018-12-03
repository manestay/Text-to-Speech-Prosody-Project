'''
This script adds all GloVe, games-trained, and dependency-based embeddings to the table.
'''

import pandas as pd 
from functools import reduce
from config_file import config

import add_reg_embeddings 
import add_glove_embeddings
import add_pretrained_dep_embeddings

INPUT_TABLE = config['input_table']
NEW_TABLE_NAME = config['new_table_name']

def concat_dfs(dataframes):
  df = reduce(lambda df1,df2: pd.concat([df1,df2],axis=1),dataframes)
  return df

def save_to_csv(dataframe,table_name):
  print ("Embeddings added.")
  dataframe.to_csv(table_name,sep=",",index=False)

def main():

  glove_embeddings_df = add_glove_embeddings.main()
  games_embeddings_df = add_reg_embeddings.main()
  pretrained_dep_embeddings_df = add_pretrained_dep_embeddings.main()
  orig_df = pd.read_csv(INPUT_TABLE)

  dfs = [orig_df,
         glove_embeddings_df,
         games_embeddings_df,
         pretrained_dep_embeddings_df]
  
  df = concat_dfs(dfs)
  save_to_csv(df,NEW_TABLE_NAME)

if __name__ == '__main__':
  main()
  






