'''
This script generates XMLs for each session, and adds the columns
Stanford_PoS
Coreference_IDs
'''

import CleanCorefs
from OrganizedBigTable import *
from stanford_document_info import *
import os
from time import sleep
from example_config import config

START_SESSION = config['start_session']
END_SESSION = config['end_session']
FILE_SUFFIX = config['file_suffix']
ORIG_XML_DIR = config['xml_dir']
CLEANED_XML_DIR = config['xml_dir_cleaned']

FILENAME_XML_EXT = config['file_xml_ext']
OVERWRITE_XMLS = config['overwrite_xmls']
CLEAN_XMLS = config['clean_xmls']

JAVA_CLASS_PATH = config['java_class_path']
COMMAND =  'java -Xmx8g -cp {} edu.stanford.nlp.pipeline.StanfordCoreNLP \
           -annotators tokenize,ssplit,pos,lemma,ner,parse,coref -coref.algorithm neural \
           -outputDirectory {} -replaceExtension -file '.format(JAVA_CLASS_PATH, config['xml_dir'])

# TODO: refactor to use stanfordcorenlp Python wrapper
def generate_stanford_text():
    for session_number in range(START_SESSION, END_SESSION + 1):
        bigtable = OrganizedBigTable(session_number)
        bigtable.export_txt()

def generate_xmls(session_number, overwrite=False):
    os.makedirs(CLEANED_XML_DIR, exist_ok=True)
    text_filename = '{}_session{}.txt'.format(OLD_PREFIX, session_number)
    xml_filename = '{}/{}_session{}.xml'.format(ORIG_XML_DIR, OLD_PREFIX, session_number)
    if overwrite or not os.path.exists(xml_filename):
        os.system(COMMAND + text_filename)
    sleep(5) # make sure Stanford CoreNLP Java code finishes writing to file
    return xml_filename

def main():
    offset = 0

    for session_number in range(START_SESSION, END_SESSION + 1):
        session_number = str(session_number).zfill(2)

        xml_name = generate_xmls(session_number, OVERWRITE_XMLS)
        if CLEAN_XMLS:
            print('cleaning corefs')
            CleanCorefs.clean_xml(xml_name)
            XML_DIR = CLEANED_XML_DIR
        else:
            XML_DIR = ORIG_XML_DIR

        bigtable = OrganizedBigTable(session_number)
        stanford = StanfordDocumentInformation(session_number, offset, XML_DIR)
        offset = stanford.coref_id_end + 1

        parts_of_speech = stanford.getPoSList()

        bigtable.addColumnToDataFrame(parts_of_speech, 'Stanford_PoS')

        coref_information = stanford.getCoreferenceList()
        bigtable.addColumnToDataFrame(coref_information, 'Coreference_IDs')

        bigtable.saveToCSV()

if __name__ == '__main__':
    main()
