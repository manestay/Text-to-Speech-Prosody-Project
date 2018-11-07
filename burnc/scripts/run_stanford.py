'''
This script generates XMLs for each session, and adds the column, Coreference_IDs, 
to table
'''

import os
from time import sleep
from clean_corefs import * 
from organized_big_table import *
from example_config import config
from stanford_document_information import *

FILE_SUFFIX = config['file_suffix'] 
LAST_SPEAKER = config['last_speaker']
NUM_SESSIONS = config['num_sessions']
START_SESSION = config['start_session']
FIRST_SPEAKER = config['first_speaker']
SPEAKER_GENDER = config['speaker_gender']

XML_DIR = config['xml_dir'] 
TXT_DIR = config['txt_dir']
CLEAN_XMLS = config['clean_xmls']
FILENAME_XML_EXT = config['file_xml_ext']

JAVA_CLASS_PATH = config['java_class_path']
COMMAND =  'java -mx4g -cp ' + JAVA_CLASS_PATH + ' edu.stanford.nlp.pipeline.StanfordCoreNLP \
           -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref \
           -outputFormat xml -outputDirectory ' + XML_DIR + ' -replaceExtension -file '

def generateStanfordText(speaker_id):
  os.makedirs(TXT_DIR,exist_ok=True)
  for session_number in range(START_SESSION, NUM_SESSIONS[int(speaker_id[1]) - 1] + 1):
    bigtable = OrganizedBigTable(session_number, speaker_id)
    bigtable.exportToFile()

def generate_xmls(session_number,speaker_id):
  os.makedirs(XML_DIR,exist_ok=True)
  os.system(COMMAND + TXT_DIR + speaker_id + '_' + session_number + FILE_SUFFIX)
  sleep(5) # make sure Stanford CoreNLP Java code finishes writing to file

def main():
  offset = 0

  for speaker_id in range(FIRST_SPEAKER, LAST_SPEAKER + 1):
    speaker_id = SPEAKER_GENDER + str(speaker_id)
    generateStanfordText(speaker_id)
    for session_number in range(1, NUM_SESSIONS[int(speaker_id[1]) - 1] + 1):
      session_number = str(session_number)

      if CLEAN_XMLS:
        generate_xmls(session_number, speaker_id)
        clean_corefs(speaker_id,session_number)

      bigtable = OrganizedBigTable(session_number, speaker_id)

      stanford = StanfordDocumentInformation(speaker_id, session_number, offset)
      offset = stanford.coref_id_end + 1
      coref_information = stanford.getCoreferenceList()

      bigtable.addCorefIDsToDataFrame(coref_information, 'Coreference_IDs', session_number)

      bigtable.saveToCSV()

if __name__ == '__main__':
  main()
