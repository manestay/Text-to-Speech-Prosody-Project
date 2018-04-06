from OrganizedBigTable import *
from StanfordDocumentInformation import *
import os
from time import sleep

START_SESSION = 2
# END_SESSION = 13
END_SESSION = 4
FILE_SUFFIX = '_INTERPOLATED.txt'
JAVA_CLASSPATH = "../../corenlp/*:."
COMMAND =  'java -Xmx4g -cp ' + JAVA_CLASSPATH + ' edu.stanford.nlp.pipeline.StanfordCoreNLP \
           -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref \
           -outputDirectory xml \
           -replaceExtension \
           -file '

XML_DIR = 'xml/'
FILENAME_XML_EXT = '_INTERPOLATED.xml'
XML_EXT = '.xml'


def generateStanfordText(order_type):
    for session_number in range(START_SESSION, END_SESSION):
        bigtable = OrganizedBigTable(session_number, order_type=order_type)
        # bigtable.updateDataFrame()
        bigtable.exportToFile()

def main():
    order_type = OrderType.INTERPOLATED
    offset = 0
    # generateStanfordText(order_type)

    for session_number in range(START_SESSION, END_SESSION):
        session_number = str(session_number).zfill(2)

        # WILL OVERWRITE CORRECTED XML FILES

        # Generate XML files
        # print(COMMAND + session_number + FILE_SUFFIX)
        # os.system(COMMAND + session_number + FILE_SUFFIX)
        # filename = XML_DIR + session_number + FILENAME_XML_EXT
        # sleep(5) # make sure Stanford CoreNLP Java code finishes writing to file
        # f = open(filename, "w+")
        # f.close()
        # os.makedirs(path, exist_ok=True)
        # os.rename(session_number + FILE_SUFFIX + XML_EXT, filename)

        bigtable = OrganizedBigTable(session_number, order_type=order_type)
        stanford = StanfordDocumentInformation(session_number, offset)
        offset = stanford.coref_id_end + 1

        parts_of_speech = stanford.getPoSList()
        bigtable.addColumnToDataFrame(parts_of_speech, 'Stanford_PoS')

        coref_information = stanford.getCoreferenceList()
        bigtable.addColumnToDataFrame(coref_information, 'Coreference_IDs')

        bigtable.saveToCSV()

main()
