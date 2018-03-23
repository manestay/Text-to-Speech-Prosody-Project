from OrganizedBigTable import *
from StanfordDocumentInformation import *
import os

START_SESSION = 1
# END_SESSION = 2
END_SESSION = 13
FILE_SUFFIX = '_INTERPOLATED.txt'
COMMAND =  'java -cp "../../corenlp/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP  \
           -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref \
           -file '

XML_DIR = 'xml-corrections/'
FILENAME_XML_EXT = '_INTERPOLATED.xml'
XML_EXT = '.xml'

def generateStanfordText(order_type):
    for session_number in range(START_SESSION, END_SESSION):
        bigtable = OrganizedBigTable(session_number)
        # bigtable.updateDataFrame()
        bigtable.exportToFile()

if __name__ == '__main__':
    order_type = OrderType.INTERPOLATED
    offset = 0

    for session_number in range(START_SESSION, END_SESSION):
        session_number = str(session_number).zfill(2)
        print('processing session {}'.format(session_number))

        # generate the xml file
        os.system(COMMAND + session_number + FILE_SUFFIX)
        filename = XML_DIR + session_number + FILENAME_XML_EXT
        f = open(filename, "w+")
        f.close()
        os.rename(session_number + FILE_SUFFIX + XML_EXT, filename)
        bigtable = OrganizedBigTable(session_number, order_type=order_type)

        stanford = StanfordDocumentInformation(session_number, offset)
        print('offset is {}'.format(offset))
        offset = stanford.coref_id_end + 1
        parts_of_speech = stanford.getPoSList()
        # print(parts_of_speech)
        bigtable.addColumnToDataFrame(parts_of_speech, 'Stanford_PoS')
        coref_information = stanford.getCoreferenceList()
        # print(coref_information)
        bigtable.addColumnToDataFrame(coref_information, 'Coreference_IDs')
        # mentions_list = stanford.getMentionList()
        # bigtable.addColumnToDataFrame(mentions_list, 'Explicit_Mentions_In_Session')
        bigtable.saveToCSV()
