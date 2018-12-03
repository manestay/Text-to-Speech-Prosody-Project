'''
This file generates clusters of the following GloVe embedding features:
glove_6B_50d
glove_6B_100d
glove_6B_200d
glove_6B_300d
glove_twitter_27B_25d
glove_twitter_27B_50d
glove_twitter_27B_100d
glove_twitter_27B_200d
glove_42B_300d
glove_840B_300d
'''

import glob
import pandas as pd 
from config_file import config
from add_embedding_column import *

GLOVE_DIR = config['glove_dir']
TABLE_NAME = config['input_table']
NUM_CLUSTERS = config['num_clusters']
NEW_TABLE_NAME = config['new_table_name']

glove_embeddings_df = pd.DataFrame()

def glove_dataframe(glove_dir,num_clusters):

  print ("Generating GloVe embeddings......")
  df = pd.DataFrame()

  for filename in sorted(glob.glob(glove_dir + '*'), key=lambda x: (int(x.split('.')[-3][:-1]), int(x.split('.')[-2][:-2]))):
    new_column_name = ('_').join(filename[6:].split('.')[:-1])
    print ("...Generating {} embeddings".format(new_column_name))
    new_column = AddEmbeddingColumn(TABLE_NAME,filename)
    embeddings = new_column.glove_embeddings()
    clusters = generate_embedding_clusters(embeddings,num_clusters,new_column.vocab)
    df[new_column_name] = clusters

  return df

def save_csv(dataframe,table_name):
  dataframe.to_csv(table_name,index=False)

def main():
  glove_embeddings_df = glove_dataframe(GLOVE_DIR,NUM_CLUSTERS)
  return glove_embeddings_df

