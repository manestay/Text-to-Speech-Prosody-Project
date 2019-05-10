"""
This script runs the Stanford CoreNLP pipeline for the Tongji Games Corpus.

@author: Bryan Li (bl2557@columbia.edu)
"""
import jieba
import json
import os

from stanford_document_info import StanfordDocumentInformation
from stanfordcorenlp import StanfordCoreNLP
from tongji_lib import get_transcript_list

OVERWRITE = False
CORE_NLP_PATH = "/proj/speech/tools/stanford-corenlp-3.9.1/"
# taken from http://dailynews.sina.com/bg/international/chinanews/2019-04-23/doc-iuqtnzfz5272842.shtml
ARTICLE = "/proj/afosr/corpora/Tongji_Games_Corpus/example_article.txt"
PROPERTIES_FILE = CORE_NLP_PATH + 'properties/StanfordCoreNLP-chinese.properties'

def get_properties(properties_file):
    properties = {}
    with open(properties_file) as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, value = line.split('=')
        properties[key.strip()] = value.strip()
    return properties

def stanford_tag(client, text, props, offset=0):
    ann = client.annotate(text, properties=props)
    doc_info = StanfordDocumentInformation(ann, offset)
    # doc_info = StanfordDocumentInformation(open('hi.xml').read(), offset)
    doc_info.collapse_punctuation(inplace=True)
    return doc_info

def main(client=None):
    props = get_properties(PROPERTIES_FILE)
    errors = {}
    try:
        local_client = False
        if not client:
            client = StanfordCoreNLP(CORE_NLP_PATH, memory='8g', quiet=False)
            local_client = True
        # transcripts = [ARTICLE]
        transcripts = get_transcript_list()
        # transcripts.sort()
        # print(transcripts); return
        offset = 0
        for transcript_name in transcripts:
            out_name = os.path.splitext(transcript_name)[0] + '_corenlp_features.csv'
            if not OVERWRITE and os.path.exists(out_name):
                print('{} exists, skipping'.format(out_name))
                continue
            with open(transcript_name) as f:
                lines = f.readlines()
            text = ''.join(lines)
            text = text.replace('|', ' 。 ')
            if not text.endswith('。'):
                text += '。'
            try:
                doc_info = stanford_tag(client, text, props, offset)
            except AttributeError as e:
                print('timeout for file {}'.format(transcript_name))
                errors[transcript_name] = e
                continue
            offset = doc_info.coref_id_end + 1
            with open(out_name, 'w') as f:
                f.write('word, coref_id, ner, pos, function, punctuation\n')
                for sentence in doc_info.sentences:
                    for token in sentence:
                        f.write('{}, {}, {}, {}, {}, {}\n'.format(token.word, token.coref_id,
                            token.ner, token.pos, token.function,
                            token.punctuation))
                    f.write('\n')
                print('wrote to ' + out_name)

    finally:
        if local_client:
            print('closing local client')
            client.close()
        print('errors in files: {}'.format(errors))

if __name__ == "__main__":
    main()
