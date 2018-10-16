import json
import logging
import os
import pandas as pd
import string
from time import sleep
from stanfordcorenlp import StanfordCoreNLP
from OrganizedBigTable import OrganizedBigTable, OrderType, _turnsToText
from CombineSessionTables import combine
from example_config import config

CORE_NLP_PATH = config.get('core_nlp_path')
START_SESSION = config.get('start_session')
END_SESSION = config.get('end_session')
ORDER_TYPE = config.get('order_type')
MEMORY = config.get('java_memory') or '4g'

props = {'annotators': 'tokenize,ssplit,pos','outputFormat':'json'}

def parse_pos():
    with StanfordCoreNLP(CORE_NLP_PATH, memory=MEMORY, quiet=True) as client:
        for i in range(START_SESSION, END_SESSION+1):
            session_number = str(i).zfill(2)
            filename = "{}_{}.txt".format(session_number, ORDER_TYPE)
            stanford_tag(client, filename)
        sleep(5) # make sure all sessions complete before closing client

def stanford_tag(client, filename):
    document = open(filename)
    text = document.read()
    ann = client.annotate(text, properties=props)
    parsed = json.loads(ann)
    words_file_name = '{}words.txt'.format(os.path.splitext(filename)[0])
    words_file = open(words_file_name, 'w')
    for item in parsed['sentences']:
        for token in item['tokens']:
            word = token['word']
            pos = token['pos']
            words_file.write('{} {}\n'.format(word, pos))

    document.close()
    words_file.close()

if __name__ == '__main__':
    parse_pos()
