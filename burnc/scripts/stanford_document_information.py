'''
StanfordDocumentInformation stores  information from Stanford about a file.
Right now it stores coreferent data (I will add POS info from savePoS.py and syntax information)
It takes the coreferences for a particular document's XML output
(from Stanford CoreNLP) and stores them as Mention objects, which contain
the start char of the word in the document, its end char, and its coreference ID
for the chain of coreferences.
'''

from example_config import config
import xml.etree.ElementTree as ET

XML_DIR = config['xml_dir']
XML_EXTENSION = config['file_xml_ext']
DOCUMENT = 'document'

# for accessing the coreferent information and tags in the XML
END = 'end'
START = 'start'
HEAD = 'head'
MENTION = 'mention'
SENTENCE = 'sentence'
COREFERENCE = 'coreference'

# for accessing the sentence information and tags in the XML
SENTENCES = 'sentences'
SENTENCE = 'sentence'
TOKENS = 'tokens'
TOKEN = 'token'
WORD = 'word'
ID = 'id'

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
  def __init__(self, speaker_id, session_number, mention_offset):
    # document parse
    TREE = ET.parse(XML_DIR + speaker_id + '_' + session_number + XML_EXTENSION).getroot().find(DOCUMENT)
    # the sentence data has the offset characters, while the coreferent
    # data has the coreferent mention information we want. So we associate
    # both and store the resulting mentions.
    sentence_data = TREE.find(SENTENCES).findall(SENTENCE)
    sentences = _OrganizeSentenceData(sentence_data)
    coreference_data = TREE.find(COREFERENCE).findall(COREFERENCE)
    self.sentences, self.coref_id_end = _AssociateCoreferentData(coreference_data,
                                          sentences,
                                          mention_offset)
    self.session_number = session_number
    self.speaker_id = speaker_id

  def getCoreferenceList(self):
    '''
    ::return List of tuples, including word and coreference_id
    '''
    return [(token.word, token.coref_id)
            for sentence in self.sentences
            for token in sentence
            if token.word != '.']

