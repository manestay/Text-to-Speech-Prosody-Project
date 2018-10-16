import pandas as pd
import math
import numpy as np
import datetime
import xml.etree.ElementTree as ET
import os
import pickle

BIGTABLE = "games-data-20180323.csv"
XML = "xml-corrections/02_INTERPOLATED.xml"

df = pd.read_csv(BIGTABLE)
all_words = df[['session_number', 'word']]

session_words = all_words.groupby('session_number')

words = session_words.get_group(2)['word']

tree = ET.parse(XML)
root = tree.getroot()

sentences = root[0][1]
phrases = []
phrase_num_dict = dict()


# Find all sentences in XML and get phrases consisting of their tokens
for i, sentence in enumerate(sentences):
    tokens = sentence.find('tokens')
    phrase = []
    for token in tokens:
        t = token.find('word').text
        if t != ".":
            if "'" in t:
                phrase[-1] += t
            else:
                phrase.append(t)

    phrases.append(phrase)
    phrase_num_dict[i] = (phrase, [])

# for k, phrase in enumerate(phrases):
#     for i in range(len(words)):
#         if len(phrase) > 0 and words.iloc[i] == phrase[0]:
#
#             for j in range(len(phrase)):
#                 if (i + j) < len(words):
#                     if phrase[j] == words.iloc[i + j] and j == len(phrase) - 1:
#                         print("Match", phrase)
#                         _, ranges = phrase_num_dict[k]
#                         ranges.append((i, i + j + 1))
#                         phrase_num_dict[k] = (phrase, ranges)
#                     elif phrase[j] != words.iloc[i + j]:
#                         break
#
# with open("table_coref_matches.pickle", "wb") as f:
#     pickle.dump(phrase_num_dict, f)
