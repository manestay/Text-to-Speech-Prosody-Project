import json
import logging
import os
import pandas as pd
import string
from time import sleep
from stanfordcorenlp import StanfordCoreNLP
from OrganizedBigTable import OrganizedBigTable
from example_config import config

CORE_NLP_PATH = config.get('core_nlp_path')
START_SESSION = config.get('start_session')
TABLE_PREFIX = config.get('old_table_prefix')
END_SESSION = config.get('end_session')
MEMORY = config.get('java_memory') or '4g'

props = {'annotators': 'tokenize,ssplit,pos','outputFormat':'json'}

def parse_pos(client=None):
    local_client = False
    if not client:
        client = StanfordCoreNLP(CORE_NLP_PATH, memory=MEMORY)
        local_client = True
    for i in range(START_SESSION, END_SESSION+1):
        session_number = str(i).zfill(2)
        filename = "{}_session{}.txt".format(TABLE_PREFIX, session_number)
        stanford_tag(client, filename)
    sleep(5) # make sure all sessions complete before closing client
    if local_client: # close local client
        client.close()

def stanford_tag(client, filename):

    document = open(filename)
    text = document.read()
    ann = client.annotate(text, properties=props)
    parsed = json.loads(ann)
    words_file_name = '{}_words.txt'.format(os.path.splitext(filename)[0])
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
