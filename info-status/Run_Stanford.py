'''
This script generates XMLs for each session, and adds the columns
Stanford_PoS
Coreference_IDs
'''

from OrganizedBigTable import *
from StanfordDocumentInformation import *
import os
from time import sleep
from example_config import config

START_SESSION = config['start_session']
END_SESSION = config['end_session']
FILE_SUFFIX = config['file_suffix']
ORDER_TYPE = OrderType[config['order_type']]

XML_DIR = config['xml_dir']
FILENAME_XML_EXT = config['file_xml_ext']
OVERWRITE_XMLS = config['overwrite_xmls']

JAVA_CLASS_PATH = config['java_class_path']
COMMAND =  'java -Xmx4g -cp ' + JAVA_CLASS_PATH + ' edu.stanford.nlp.pipeline.StanfordCoreNLP \
           -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref \
           -outputDirectory xml -replaceExtension -file '

def generateStanfordText(order_type=ORDER_TYPE):
    for session_number in range(START_SESSION, END_SESSION + 1):
        bigtable = OrganizedBigTable(session_number, order_type=ORDER_TYPE)
        # bigtable.updateDataFrame()
        bigtable.exportToFile()

def generate_xmls(session_number):
    os.makedirs(XML_DIR, exist_ok=True)
    os.system(COMMAND + session_number + FILE_SUFFIX)
    sleep(5) # make sure Stanford CoreNLP Java code finishes writing to file

def main():
    offset = 0
    # generateStanfordText(ORDER_TYPE)

    for session_number in range(START_SESSION, END_SESSION + 1):
        session_number = str(session_number).zfill(2)

        if OVERWRITE_XMLS:
            generate_xmls(session_number)

        bigtable = OrganizedBigTable(session_number, order_type=ORDER_TYPE)
        stanford = StanfordDocumentInformation(session_number, offset)
        offset = stanford.coref_id_end + 1

        parts_of_speech = stanford.getPoSList()
        bigtable.addColumnToDataFrame(parts_of_speech, 'Stanford_PoS')

        coref_information = stanford.getCoreferenceList()
        bigtable.addColumnToDataFrame(coref_information, 'Coreference_IDs')

        bigtable.saveToCSV()

if __name__ == '__main__':
    main()
