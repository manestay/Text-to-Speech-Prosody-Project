'''
stanford_document_info stores  information from Stanford about a file.
Right now it stores coreferent data
It takes the coreferences for a particular document's XML output
(from Stanford CoreNLP) and stores them as Mention objects, which contain
the start char of the word in the document, its end char, and its coreference ID
for the chain of coreferences.

Adapted for Tongji.
'''

from copy import deepcopy
import lxml.etree as ET
import re
import string

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
NER = 'NER'
POS = 'POS'

# some Chinese and Western punctuation symbols
PUNCTUATION = r"[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）：；《）《》“”()»〔〕-]+"
ENDING_PUNCTUATION = "，。？、：；"
'''
Represent a token in a document, with its token id in the sentence.
'''
class Token(object):
    def __init__(self, token_id, word, coref_id=None, ner=None, pos=None,punctuation=None, function=None, parse_tree=None):
        self.id = int(token_id)
        self.word = word
        self.coref_id = coref_id
        self.ner = ner
        self.pos = pos
        self.punctuation = punctuation
        self.function = function
        self.parse_tree = parse_tree
    def __repr__(self):
        return 'Token(id={}, word={})'.format(self.id, self.word)
    def __str__(self):
        return 'id={}, word={}'.format(self.id, self.word)

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
                                             xml_token.find(WORD).text,
                                             ner=xml_token.find(NER).text,
                                             pos=xml_token.find(POS).text)
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
    def __init__(self, xml_string, mention_offset):
        # document parse
        parser = ET.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        self.tree = ET.fromstring(xml_string.encode('utf-8'), parser=parser).find(DOCUMENT)
        # self.tree = ET.fromstring(xml_string.encode('utf-8'), parser=parser)
        # the sentence data has the offset characters, while the coreferent
        # data has the coreferent mention information we want. So we associate
        # both and store the resulting mentions.
        sentence_data = self.tree.find(SENTENCES).findall(SENTENCE)
        sentences = _OrganizeSentenceData(sentence_data)
        coreference_data = self.tree.find(COREFERENCE).findall(COREFERENCE)
        self.sentences, self.coref_id_end = _AssociateCoreferentData(coreference_data, sentences, mention_offset)
        syntactic = self.add_function_and_parse_tree(sentence_data)

    def collapse_punctuation(self, inplace=False):
        '''
        Iterates through tokens in all the sentences and collapses punctuation tokens with the
        previous token. For example:
            [Token('Previously'), Token(','), ...] -> [Token('Previously', punctuation=','), ...]
        '''
        sentences = []
        for sentence in self.sentences:
            sentence_new = []
            prev_token = None
            for token in sentence:
                if re.match(PUNCTUATION, token.word):
                    if prev_token and token.word in ENDING_PUNCTUATION:
                        prev_token.punctuation = token.word
                else:
                    sentence_new.append(prev_token)
                    prev_token = token
            if prev_token and not re.match(PUNCTUATION, prev_token.word): # add last token if not punctuation
                sentence_new.append(prev_token)
            if sentence_new:
                sentence_new.pop(0) # remove None at beginning of list
            sentences.append(sentence_new)
        if inplace:
            self.sentences = sentences
        return sentences

    def add_function_and_parse_tree(self, sentence_data):
        def get_dep_idx(dep):
            return int(dep.find('dependent').attrib['idx'])

        def clean_dep_list(dep_list):
            dep_list.sort(key=get_dep_idx)
            seen = set()
            cleaned_dep_list = []
            for dep in dep_list:
                if not dep.get('extra'):
                    cleaned_dep_list.append(dep)
            return cleaned_dep_list

        for sent_xml, sent_internal in zip(sentence_data, self.sentences):
            parse_tree = sent_xml.find('parse').text
            parse_tree = ' '.join(parse_tree.split()) # collapse whitespace
            deps = sent_xml.find("dependencies[@type='enhanced-plus-plus-dependencies']")
            dep_list = list(deps)
            dep_list = clean_dep_list(dep_list)

            for dep, token in zip(dep_list, sent_internal):
                word = dep.find('dependent').text
                if token.word != word:
                    print('mismatch found')
                token.parse_tree = parse_tree
                token.function = dep.get('type')

    def get_ner_list(self):
        '''
        Gets NER tags for words in document.
        '''
        ner_list = [(token.word, token.ner)
                for sentence in self.sentences
                for token in sentence]
        return ner_list

    def get_coref_list(self):
        '''
        Gets a list of the coreferent words in the document.
        '''
        coref_list = [(token.word, token.coref_id)
                for sentence in self.sentences
                for token in sentence]
        return coref_list


    def get_pos_list(self, return_punct=False):
        '''
        Get parts of speech processed from Stanford as a list of words, parts of speech.
        '''
        pos_list = [(token.word, token.pos)
                for sentence in self.sentences
                for token in sentence
                for i in range(len(token.word))]
        return pos_list
