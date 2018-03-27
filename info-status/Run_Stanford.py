from OrganizedBigTable import *
from StanfordDocumentInformation import *
import os

START_SESSION = 2
END_SESSION = 13
FILE_SUFFIX = '_INTERPOLATED.txt'
# JAVA_CLASSPATH = "/Users/amaan/Downloads/corenlp/*"
# COMMAND =  'java -cp ' + JAVA_CLASSPATH + ' edu.stanford.nlp.pipeline.StanfordCoreNLP \
           # -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref \
           # -file '

XML_DIR = 'xml-corrections/'
FILENAME_XML_EXT = '_INTERPOLATED.xml'
XML_EXT = '.xml'


def generateStanfordText(order_type):
    for session_number in range(START_SESSION, END_SESSION):
        bigtable = OrganizedBigTable(session_number)
        # bigtable.updateDataFrame()
        bigtable.exportToFile()

def main():
    order_type = OrderType.INTERPOLATED
    offset = 0
    # generateStanfordText(OrderType.INTERPOLATED)

    for session_number in range(START_SESSION, END_SESSION):
        session_number = str(session_number).zfill(2)

        # WILL OVERWRITE CORRECTED XML FILES

        # Generate XML files
        # os.system(COMMAND + session_number + FILE_SUFFIX)
        # filename = XML_DIR + session_number + FILENAME_XML_EXT
        # f = open(filename, "w+")
        # f.close()
        # os.rename(session_number + FILE_SUFFIX + XML_EXT, filename)

        bigtable = OrganizedBigTable(session_number)
        stanford = StanfordDocumentInformation(session_number, offset)
        offset = stanford.coref_id_end + 1

        parts_of_speech = stanford.getPoSList()
        bigtable.addColumnToDataFrame(parts_of_speech, 'Stanford_PoS')

        coref_information = stanford.getCoreferenceList()
        bigtable.addColumnToDataFrame(coref_information, 'Coreference_IDs')

        bigtable.saveToCSV()

main()
