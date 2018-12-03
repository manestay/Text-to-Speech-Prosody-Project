'''
This file trains embeddings on the Games corpus, using the Word2Vec skipgram model, and generates clusters of them. 
'''
import math
import random
import numpy as np
import collections
import pandas as pd
import tensorflow as tf
from config_file import config
from add_embedding_column import *
from sklearn.cross_validation import train_test_split

EMBEDDING_DIM = config['emb_dim']
TABLE_NAME = config['input_table']
NUM_CLUSTERS = config['num_clusters']
NEW_TABLE_NAME = config['new_table_name']
NEW_COLUMN_NAME = config['games_trained_200d']

class Word2Vec_SkipGram():

  def __init__(self,table=TABLE_NAME):
    self.df = pd.read_csv(table)
    self.embeddings = dict()
    self.vocab = list([l.lower() for l in list(self.df['word'])])
    self.data_index = 0

  '''Function organizes data for batch and label generation''' 

  def build_dataset(self,words,n_words):
    count = [['UNK', -1]]
    count.extend(collections.Counter(words).most_common(n_words-1))
    dictionary = dict()
    for word, _ in count:
      dictionary[word] = len(dictionary)
    data = list()
    unk_count = 0
    for word in words:
      if word in dictionary:
        index = dictionary[word]
      else:
        index = 0
        unk_count += 1
      data.append(index)
    count[0][1] = unk_count
    reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
    return data, count, dictionary, reverse_dictionary

  '''Function to generate batches and labels'''

  def generate_batch(self,batch_size,num_skips,skip_window):

    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size,1), dtype=np.int32)
    span = 2*skip_window + 1
    buffer = collections.deque(maxlen=span)
    data = self.build_dataset(self.vocab, len(self.vocab))[0]
    for _ in range(span):
      buffer.append(data[self.data_index])
      self.data_index = (self.data_index + 1) % len(data)
    for i in range(batch_size//num_skips):
      target = skip_window
      targets_to_avoid = [skip_window]
      for j in range(num_skips):
        while target in targets_to_avoid:
          target = random.randint(0, span - 1)
        targets_to_avoid.append(target)
        batch[i*num_skips+j] = buffer[skip_window]
        labels[i*num_skips+j,0] = buffer[target]
      buffer.append(data[self.data_index])
      self.data_index = (self.data_index+1)%len(data)
    self.data_index = (self.data_index + len(data) - span) % len(data)
    return batch, labels

  '''Train Word2Vec model on data'''

  def train(self,vocabulary_size,batch_size,embedding_dim,skip_window,num_skips,num_neg_samples,num_training_iter):

    graph = tf.Graph()

    with graph.as_default():

      train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
      train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
      
      embeddings = tf.Variable(
          tf.random_uniform([vocabulary_size, embedding_dim], -1.0, 1.0))
      embed = tf.nn.embedding_lookup(embeddings, train_inputs) 

      nce_weights = tf.Variable(
          tf.truncated_normal([vocabulary_size, embedding_dim],
                                stddev=1.0 / math.sqrt(embedding_dim)))
      nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

      loss = tf.reduce_mean(
          tf.nn.nce_loss(weights=nce_weights,
                        biases=nce_biases,
                        labels=train_labels,
                        inputs=embed,
                        num_sampled=num_neg_samples,
                        num_classes=vocabulary_size))

      optimizer = tf.train.GradientDescentOptimizer(0.1).minimize(loss)

      norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
      normalized_embeddings = embeddings / norm
      init = tf.global_variables_initializer()

    with tf.Session(graph=graph) as session:

      init.run()

      average_loss = 0
      for step in range(num_training_iter):
        batch_inputs, batch_labels = self.generate_batch(
            batch_size, num_skips, skip_window)
        feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}

        _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
        average_loss += loss_val
      final_embeddings = normalized_embeddings.eval()
      reverse_dictionary = self.build_dataset(self.vocab,len(self.vocab))[3]
      for index,word in enumerate(reverse_dictionary.values()):
        self.embeddings[word] = final_embeddings[index]

def add_dataframe_column(column_data,column_name,vocab):

  print ("Generating {}d Games embeddings.....".format(EMBEDDING_DIM))
  df = pd.DataFrame()
  clusters_column = generate_embedding_clusters(column_data,NUM_CLUSTERS,vocab)
  df[column_name] = clusters_column
  return df 

def save_to_csv(dataframe,table_name):
  dataframe.to_csv(table_name)
  print ("Embeddings added.")

def main():
  model = Word2Vec_SkipGram()

  vocabulary = model.vocab
  vocabulary_size = len(vocabulary)

  data, count, dictionary, reverse_dictionary = model.build_dataset(vocabulary, vocabulary_size)

  data_index = 0
  model.train(vocabulary_size,
              batch_size=32,
              embedding_dim=EMBEDDING_DIM,
              skip_window=4,
              num_skips=8,
              num_neg_samples=64,
              num_training_iter=10000)

  games_embeddings = model.embeddings

  games_embeddings_df = add_dataframe_column(games_embeddings,NEW_COLUMN_NAME,model.vocab)
  return games_embeddings_df


'''
Acknowledgements: 
Deep Learning with Keras -- O'Reilly Media
http://adventuresinmachinelearning.com/word2vec-tutorial-tensorflow
'''


