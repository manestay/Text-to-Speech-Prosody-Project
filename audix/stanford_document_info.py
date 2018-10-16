'''
stanford_document_info stores  information from Stanford about a file.
Right now it stores coreferent data
It takes the coreferences for a particular document's XML output
(from Stanford CoreNLP) and stores them as Mention objects, which contain
the start char of the word in the document, its end char, and its coreference ID
for the chain of coreferences.
'''

from example_config import config
import xml.etree.ElementTree as ET
import re
import string

# for accessing the XML files
XML_DIR = config['xml_dir']
XML_EXTENSION = config['file_xml_ext']
# for accessing the document in the XML
DOCUMENT = 'document'

# for accessing the coreferent information and tags in the XML
COREFERENCE = 'coreference'
MENTION = 'mention'
START = 'start'
END = 'end'

# for accessing the sentence information and tags in the XML
SENTENCES = 'sentences'
SENTENCE = 'sentence'
TOKENS = 'tokens'
TOKEN = 'token'
WORD = 'word'
ID = 'id'

# for accessing part of speech information
OLD_PREFIX = config['old_table_prefix']
POS_SUFFIX = '_words.txt'

'''
Represent a token in a document, with its token id in the sentence.
'''
class Token(object):
    def __init__(self, token_id, word):
        self.id = int(token_id)
        self.coref_id = ''
        self.word = word

'''
Take sentence data from the XML and organizes into a dictionary,
where keys are sentence IDs, and values are a list of Tokens in that
sentence (in Token object form)
:param: sentence_data the information under the <sentences> tag in the XML
:return: the dictionary described above
'''
def _OrganizeSentenceData(sentence_data):
    sentences_dict = {}
    for sentence in sentence_data:
        sentence_ID = int(sentence.get(ID))
        xml_tokens = sentence.find(TOKENS).findall(TOKEN)
        sentences_dict[sentence_ID] = [Token(xml_token.get(ID),
                                  xml_token.find(WORD).text)
                                  for xml_token in xml_tokens]

    # change to list
    sentences = [None] * (len(sentences_dict))
    for key in sentences_dict:
        sentences[key-1] = sentences_dict[key]
    return sentences

'''
From XML data about coreferent information and a dictionary of sentences
with character information, associate coreference data with character offsets.
:param: coref_data the coreference information under the first <coreference>
tag in the XML
:return: a list of all mentions in the document, each with an ID that is
equal to the ID of other mentions
'''
def _AssociateCoreferentData(coreference_data, sentences, mention_offset):
    mentions = []

    coref_id = mention_offset # ensures unique identity across sessions

    for coreference in coreference_data:
        # we go through every mention for the coreferent ID
        xml_mentions = coreference.findall(MENTION)
        for xml_mention in xml_mentions:
            sentence_ID = int(xml_mention.find(SENTENCE).text)
            start_word, end_word = xml_mention.find(START).text, xml_mention.find(END).text
            # getting the Token object and storing coreference ID
            tokens = sentences[sentence_ID - 1]
            for token in tokens:
                if token.id >= int(start_word) and token.id < int(end_word):
                    token.coref_id = str(coref_id)
            sentences[sentence_ID - 1] = tokens
        coref_id+=1
    return sentences, coref_id

'''
Represent coreferent information about a document.
'''
class StanfordDocumentInformation(object):

    '''
    Constructor for document information.
    :param: num the number of the document
    :param: the offset at which to start coreferent IDs (to avoid duplicate IDs)
    '''
    def __init__(self, session_number, mention_offset, xml_dir=XML_DIR):
        # document parse
        self.session_number = str(session_number).zfill(2)
        xml_name = '{}{}_session{}.xml'.format(xml_dir, OLD_PREFIX, self.session_number)
        TREE = ET.parse(xml_name).getroot().find(DOCUMENT)
        # the sentence data has the offset characters, while the coreferent
        # data has the coreferent mention information we want. So we associate
        # both and store the resulting mentions.
        sentence_data = TREE.find(SENTENCES).findall(SENTENCE)
        sentences = _OrganizeSentenceData(sentence_data)
        coreference_data = TREE.find(COREFERENCE).findall(COREFERENCE)
        self.sentences, self.coref_id_end = _AssociateCoreferentData(coreference_data,
                                                 sentences,
                                                 mention_offset)

    def getCoreferenceList(self):
        '''
        Gets a list of the coreferent words in the document.
        '''
        coref_list = [(token.word, token.coref_id)
                for sentence in self.sentences
                for token in sentence
                if any((token.word[i] not in string.punctuation) for i in range(len(token.word)))]
        return coref_list

    '''
    Get parts of speech processed from Stanford as a list of words, parts of speech.
    NOTE: right now this is still getting data from the Java-generated file rather than
    the XML parse.
    '''
    def getPoSList(self):
        words_order = []
        filename = '{}_session{}{}'.format(OLD_PREFIX, self.session_number, POS_SUFFIX)
        with open(filename) as stanford:
            for line in stanford:
                word_pos = tuple(str.split(line))
                word = word_pos[0]
                if any((word[i] not in string.punctuation) for i in range(len(word))):
                    words_order.append(word_pos)
        return words_order
