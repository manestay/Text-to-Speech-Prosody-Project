'''
This file generates clusters of 300d dependency-based embeddings.
'''

import pandas as pd
from config_file import config
from add_embedding_column import *

DEPS_DIR = config['deps_dir']
INPUT_TABLE = config['input_table']
NUM_CLUSTERS = config['num_clusters']
NEW_TABLE_NAME = config['new_table_name']
NEW_COLUMN_NAME = config['pretrained_deps_300d']

pretrained_dep_embeddings_df = pd.DataFrame()

def generate_dep_embeddings(filename):
  embeddings = {}
  with open(filename,'r') as f:
    for line in f:
      line = line.split()
      word = line[0]
      embedding = line[1:]
      embeddings[word] = embedding
  return embeddings

def deps_dataframe(deps_dir,num_clusters):

  print ("Generating 300d pretrained dependency embeddings......")
  df_input = pd.read_csv(INPUT_TABLE)
  df_output = pd.DataFrame()
  embeddings = generate_dep_embeddings(deps_dir[5:])
  clusters = generate_embedding_clusters(embeddings,num_clusters,df_input['word'])
  df_output[NEW_COLUMN_NAME] = clusters

  return df_output

def save_csv(dataframe,table_name):
  dataframe.to_csv(table_name,index=False)

def main():
  pretrained_dep_embeddings_df = deps_dataframe(DEPS_DIR,NUM_CLUSTERS)
  return pretrained_dep_embeddings_df

