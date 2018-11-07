# Author: Agustin Gravano, includes code written by Amaan Khular and Pablo Brusco
# July 10, 2018
from __future__ import print_function
import sklearn
import sklearn.metrics
from sklearn import ensemble
from sklearn.cross_validation import cross_val_score
from sklearn.dummy import DummyClassifier
import numpy as np
import pandas as pd

#########################################################

CSV_FILE = "tables/burnc-20181106.csv"

#########################################################

# Data frame with all words.
df_all = pd.read_csv(CSV_FILE)

# Uncomment for debugging.
#df_all = df_all.head(5000)

# Add these columns using Amaan's function.
# IP_Pos_Normalized: the normalized position of the token within its intonational phrase
# IP_Prev_Mentions: % of all ref.expressions in an into.phrase that have been mentioned before
# IP_Length: length of the Intonational Phrase the token is a part of
#df_all = df_all.join(num_tokens_intonational_phrase_prev_mention(df_all, use_percentage=True))

# Part of Speech tags that are considered to be referring expressions
REFERRING_EXP_POS = ["NN", "NNS", "NNP", "NNPS", "PDT", "CD", "POS", "PRP", "PRP$"]

# Data frame with just referring expressions.
df_ref = df_all.loc[df_all['word_pos_tag'].isin(REFERRING_EXP_POS)].copy()

print("#words:", len(df_all), "#referring expressions:", len(df_ref))

#########################################################

# Prepares columns for classification. 
# df: dataframe
# featcats: list of feature categories to include. eg, ['syntax/pos','mentions']
# Outputs X (instance vectors), y (labels), columns (feature names)
def process_data(df, featcats):

  features = dict()

  '''features['dependency'] = ['syntactic_function', 'next_syntactic_function']
  features['pos'] = ['word_pos_tag', 'next_PoS']
  features['spanningtree'] = ['next_word_spanning_label', 'next_word_spanning_depth', 'next_word_spanning_width']
  features['constituent'] = ['constituent_width', 'constituent_label']
  features['constpos'] = ['constituent_forward_position', 'constituent_backward_position']
  features['depth'] = ['word_depth']'''

  features['syntax/pos'] = ['syntactic_function', 'word_depth', 'tree_depth', 'tree_width', 
    'constituent_width', 'constituent_label', 
    'constituent_forward_position', 
    'constituent_backward_position', 'next_word_spanning_depth', 'next_word_spanning_width', 'next_word_spanning_label',
    'word_pos_tag', 'next_PoS', 'next_syntactic_function']

  features['supertag'] = ['supertag']

  features['position'] = ['word_number_in_sentence', 'total_number_of_words_in_sentence']

  features['morph'] = ['NER', 'next_NER', 'word_length']

  features['punctuation'] = ['punctuation']

  features['mentions'] = [
                          'Coreference_IDs', 'Most_Recent_Mention',
                          'Recent_Explicit_Mention', 'Recent_Implicit_Mention',
                          'Most_Recent_Mention_PoS', 'Recent_Explicit_Mention_PoS',
                          'Recent_Implicit_Mention_PoS', 'Number_Of_Coref_Mentions',
                          'Number_Of_Explicit_Mentions', 'Number_Of_Implicit_Mentions',
                          'Most_Recent_Mention_Syntactic_Function',
                          'Recent_Explicit_Mention_Syntactic_Function',
                          'Recent_Implicit_Mention_Syntactic_Function',
                          'Far_Back_Mention'
                        ]


  def flatten(z): return [x for y in z for x in y]
  data = df[flatten([features[x] for x in featcats])].copy()

  # - - - - - - - - - - 
  if 'dependency' in featcats:
    dummies_synfn = pd.get_dummies(data["syntactic_function"], prefix="synfn")
    dummies_nsynfn = pd.get_dummies(data["next_syntactic_function"], prefix="nsynfn")
    data = pd.concat([data, dummies_synfn, dummies_nsynfn], axis=1)
    data = data.drop(['syntactic_function', 'next_syntactic_function'], axis=1)

  if 'pos' in featcats:
    dummies_pos   = pd.get_dummies(data["word_pos_tag"], prefix="pos")
    dummies_npos   = pd.get_dummies(data["next_PoS"], prefix="npos")
    data = pd.concat([data, dummies_pos, dummies_npos], axis=1)
    data = data.drop(["word_pos_tag", "next_PoS"], axis=1)

  if 'spanningtree' in featcats:
    dummies_nwsl  = pd.get_dummies(data["next_word_spanning_label"], prefix="nwsl")
    data = pd.concat([data, dummies_nwsl], axis=1)
    data = data.drop(["next_word_spanning_label"], axis=1)

  if 'constituent' in featcats:
    dummies_const = pd.get_dummies(data["constituent_label"], prefix="const")
    data = pd.concat([data, dummies_const], axis=1)
    data = data.drop(["constituent_label"], axis=1)

  if "syntax/pos" in featcats:
    dummies_const = pd.get_dummies(data["constituent_label"], prefix="const")
    dummies_synfn = pd.get_dummies(data["syntactic_function"], prefix="synfn")
    dummies_nwsl  = pd.get_dummies(data["next_word_spanning_label"], prefix="nwsl")
    data = pd.concat([data, dummies_const, dummies_synfn, dummies_nwsl], axis=1)
    data = data.drop(["constituent_label", "syntactic_function", "next_word_spanning_label"], axis=1)

    dummies_pos   = pd.get_dummies(data["word_pos_tag"], prefix="pos")
    data = pd.concat([data, dummies_pos], axis=1)
    data = data.drop(["word_pos_tag"], axis=1)

    dummies_npos   = pd.get_dummies(data["next_PoS"], prefix="npos")
    dummies_nsynfn = pd.get_dummies(data["next_syntactic_function"], prefix="nsynfn")
    data = pd.concat([data, dummies_npos, dummies_nsynfn], axis=1)
    data = data.drop(['next_PoS', 'next_syntactic_function'], axis=1)    
  
  # - - - - - - - - - - 
  if "position" in featcats:
    # Define new features: number of words until the end of the turn or task
    data['words_until_end_of_sentence'] = df['total_number_of_words_in_sentence'] - df['word_number_in_sentence']
    #data['words_until_end_of_utterance'] = df['total_number_of_words_in_utterance'] - df['word_number_in_utterance']

  # - - - - - - - - - - 
  if "supertag" in featcats:
    dummies_super = pd.get_dummies(data["supertag"], prefix="super")
    data = pd.concat([data, dummies_super], axis=1)
    data = data.drop(["supertag"], axis=1)

  # - - - - - - - - - - 
  if "morph" in featcats:
    dummies_ner = pd.get_dummies(data["NER"], prefix="ner")
    dummies_nner = pd.get_dummies(data["next_NER"], prefix="nner")
    data = pd.concat([data, dummies_ner, dummies_nner], axis=1)
    data = data.drop(["NER", "next_NER"], axis=1)

  # - - - - - - - - - - 
  if "punctuation" in featcats:
    dummies_punc = pd.get_dummies(data["punctuation"], prefix="punc")
    data = pd.concat([data, dummies_punc], axis=1)
    data = data.drop(["punctuation"], axis=1)

  if "mentions" in featcats:
    dummies_cmpos = pd.get_dummies(data["Most_Recent_Mention_PoS"], prefix="cmpos")
    dummies_cepos = pd.get_dummies(data["Recent_Explicit_Mention_PoS"], prefix="cepos")
    dummies_cipos = pd.get_dummies(data["Recent_Implicit_Mention_PoS"], prefix="cipos")
    dummies_cmsynf = pd.get_dummies(data["Most_Recent_Mention_Syntactic_Function"], prefix="cmsynf")
    dummies_cesynf = pd.get_dummies(data["Recent_Explicit_Mention_Syntactic_Function"], prefix="cesynf")
    dummies_cisynf = pd.get_dummies(data["Recent_Implicit_Mention_Syntactic_Function"], prefix="cisynf")
    data = pd.concat([data, dummies_cmpos, dummies_cepos, dummies_cipos,
                      dummies_cmsynf, dummies_cesynf, dummies_cisynf], axis=1)
    data = data.drop(['Most_Recent_Mention_PoS','Recent_Explicit_Mention_PoS','Recent_Implicit_Mention_PoS',
                      'Most_Recent_Mention_Syntactic_Function','Recent_Explicit_Mention_Syntactic_Function',
                      'Recent_Implicit_Mention_Syntactic_Function'], axis=1)

  # - - - - - - - - - - 
  
  # A token is considered to be accented if its value for column 'word_tobi_pitch_accent' is not '*?' or '_'
  y_labels = []
  indices = []
  for index, row in df.iterrows():
      y_labels.append('unaccented' if row['pitch_accent'] in ["*?", "_"] else 'accented')
      indices.append(index)

  X = data
  y = pd.Series(y_labels, index=indices)
  columns = X.columns

  # Replace remaining NaNs with medians.
  imputer = sklearn.preprocessing.Imputer(strategy="most_frequent")
  X = imputer.fit_transform(X)

  return X, y, columns


# Trains and evaluates a classifier running 5-fold CV; compares results against
# a majority-class baseline; and ranks features according to their importance.
# Arguments:
#  clf: classifier
#  X_train, y_train: training data (aka 'development set')
#  X_test, y_test: test data (aka 'evaluation set')
#  columns: feature names
# (Adapted from Pablo Brusco's code.)
def test(clf, X_train, y_train, X_test, y_test, columns):
    res_cv = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
    dummy_clf = DummyClassifier(strategy="most_frequent")
    random_cv = cross_val_score(dummy_clf, X_train, y_train, cv=5, scoring="accuracy")

    print("-----------------")
    print("Classifier: {}".format(type(clf)))
    print("Cross-validation results: {} +/- {} (random={})".format(round(res_cv.mean(), 3), round(res_cv.std(), 3), round(random_cv.mean(), 3)))

    clf.fit(X_train, y_train)
    dummy_clf.fit(X_train, y_train)

    res_train = clf.score(X_train, y_train)
    random_train = dummy_clf.score(X_train, y_train)
    print("On training data: accuracy={} (random={})".format(round(res_train, 3), round(random_train, 3)))

    res_accuracy = clf.score(X_test, y_test)
    random_accuracy = dummy_clf.score(X_test, y_test)

    y_pred = clf.predict(X_test)
    print("Evaluation results:", end=" ")
    print("accuracy=%.3f (random=%.3f) f1=%.3f precision=%.3f recall=%.3f"%(
      res_accuracy, random_accuracy,
      sklearn.metrics.f1_score(y_test, y_pred, pos_label="accented"),
      sklearn.metrics.precision_score(y_test, y_pred, pos_label="accented"),
      sklearn.metrics.recall_score(y_test, y_pred, pos_label="accented")))

    print("Feature ranking:")
    importances = clf.feature_importances_
    indices = np.argsort(importances)[::-1]
    for f in range(min(20, X_train.shape[1])):
        print("%d. feature %d (%f) %s" % (f + 1, indices[f], importances[indices[f]], columns[indices[f]]))
        
    print("-----------------")

# - - - - -

# Splits the data into training/test sets, runs the ML tests using a RF classifier.
def run_experiments(X, y, columns):
    X_train, X_test, y_train, y_test = sklearn.cross_validation.train_test_split(X, y, random_state = 1)
    clf = sklearn.ensemble.RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=1)
    test(clf, X_train, y_train, X_test, y_test, columns)

# - - - - -

# Define feature sets for each ML task:
featsets = dict()

def add_to_featsets(l):
  if len(l) == 0:
    return None
  elif len(l) == 1:
    featsets[l[0]] = l
    return [l]
  else:
    otherfeats = add_to_featsets(l[1:])
    newfeats = []
    featsets[l[0]] = [l[0]]
    newfeats.append([l[0]])
    for ol in otherfeats:
      newfeats.append(ol)
      newfeats.append([l[0]] + ol)
      featsets['_'.join([l[0]] + ol)] = [l[0]] + ol
    return newfeats


# TASK 1: Prosody assignment from text
'''featsets['task1'] = ["syntax/pos", "punctuation", "position", "morph", "supertag"]
featsets['task1_syntax_punc'] = ["syntax/pos", "punctuation"]
featsets['task1_syntax_punc_pos'] =[ "syntax/pos", "punctuation", "position"]
featsets['task1_syntax/pos'] = ["syntax/pos"]
featsets['task1_punctuation'] = ["punctuation"]  
featsets['task1_morph']      = ["morph"]
featsets['task1_position'] = ["position"]
featsets['task1_supertag'] = ["supertag"]
featsets['task1_minus_syntax/pos'] = ["punctuation", "position", "morph", "supertag"]
featsets['task1_minus_punctuation'] = ["syntax/pos", "position", "morph", "supertag"]
featsets['task1_minus_position'] = ["syntax/pos", "punctuation", "morph", "supertag"]
featsets['task1_minus_morph'] = ["syntax/pos", "punctuation", "position", "supertag"]
featsets['task1_minus_supertag'] = ["syntax/pos", "punctuation", "position", "morph"]'''

add_to_featsets(["syntax/pos", "punctuation", "position", "morph", "supertag", "mentions"])

print("##### ML experiments on all words: #####")
for t in featsets.keys():
  print("## "+ t)
  X,y,cols = process_data(df_all, featsets[t])
  run_experiments(X,y,cols)
  print()

