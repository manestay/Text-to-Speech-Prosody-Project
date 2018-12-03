import numpy as np
import pandas as pd
from config_file import config
from sklearn.cluster import KMeans

class AddEmbeddingColumn():
  
  def __init__(self,input_table,embedding_dir):
    self.df = pd.read_csv(input_table,sep=',')
    self.vocab = list(self.df['word'])
    self.embedding_dir = embedding_dir

  def glove_embeddings(self):
    embeddings = dict()
    with open(self.embedding_dir,'r') as f:
      for l in f:
        word = list(l.split(' '))[0]
        embedding = np.asarray(l.split(' ')[1:], dtype="float32")
        embeddings[word] = embedding
    return embeddings 

def generate_embedding_clusters(embeddings,num_clusters,vocab):
  dim = len(embeddings[embeddings.keys()[0]])
  table_embeddings = [embeddings[word] if word in embeddings else [0.0]*dim for word in vocab]
  kmeans = KMeans(n_clusters=num_clusters, random_state=1).fit(table_embeddings)
  clusters = [str(kmeans.labels_[i]) for i in range(len(vocab))]
  return clusters


