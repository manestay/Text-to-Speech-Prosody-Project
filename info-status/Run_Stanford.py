from OrganizedBigTable import *
from StanfordDocumentInformation import *
import os

START_SESSION = 1
END_SESSION = 2
# END_SESSION = 13
FILE_SUFFIX = '_INTERPOLATED.txt'
COMMAND =  'java -cp "/Users/amaan/Downloads/corenlp/*" edu.stanford.nlp.pipeline.StanfordCoreNLP  \
           -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref \
           -file '
XML_DIR = 'xml/'
FILENAME_XML_EXT = '_INTERPOLATED.xml'
XML_EXT = '.xml'

def generateStanfordText(order_type):
    for session_number in range(START_SESSION, END_SESSION):
        bigtable = OrganizedBigTable(session_number)
        bigtable.exportToFile(order_type)

order_type = OrderType.INTERPOLATED
offset = 0

generateStanfordText(OrderType.INTERPOLATED)

for session_number in range(START_SESSION, END_SESSION):
    session_number = str(session_number).zfill(2)
    os.system(COMMAND + session_number + FILE_SUFFIX)
    filename = XML_DIR + session_number + FILENAME_XML_EXT
    f = open(filename, "w+")
    f.close()
    os.rename(session_number + FILE_SUFFIX + XML_EXT, filename)
    bigtable = OrganizedBigTable(session_number)
    stanford = StanfordDocumentInformation(session_number, offset)
    offset = stanford.coref_id_end + 1
    parts_of_speech = stanford.getPoSList()
    # print(parts_of_speech)
    bigtable.addColumnToDataFrame(order_type, parts_of_speech, 'Stanford_PoS')
    coref_information = stanford.getCoreferenceList()
    # print(coref_information)
    bigtable.addColumnToDataFrame(order_type, coref_information, 'Coreference_IDs')
    mentions_list = stanford.getMentionList()
    bigtable.addColumnToDataFrame(order_type, mentions_list, 'Explicit_Mentions_In_Session')
    bigtable.saveToCSV()
