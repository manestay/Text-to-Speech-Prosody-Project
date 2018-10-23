"""
make_audix_csv.py

Creates a big table from the audix dataset in ~/dataset/audix.

@author: Bryan Li <bl2557@columbia.edu>
"""

import argparse
import logging
import csv
import datetime
import glob
import os
import pandas as pd
import re
import sys

from nltk import tokenize

PUNCTUATION = set(['.', ','])
UNMARKED_BOUNDARIES = set(['H', 'L', '?'])
HEADER = ['token_id', 'session_number', 'segment_number', 'word_start_time','word_number_in_segment',
          'total_number_of_words_in_segment', #'word_number_in_session', 'total_number_of_words_in_session',
          'word', 'word_tobi_pitch_accent', 'segment', 'intermediate_phrase',
          'most_prominent_pitch_accent', 'word_tobi_boundary_tone', 'preceding_word',
          'preceding_word_tobi_pitch_accent', 'preceding_word_tobi_boundary_tone']

parser = argparse.ArgumentParser(description='make csv for audix')
parser.add_argument('--dir', default='datasets/audix/', help='location of ap[n] folders')
parser.add_argument('--sessions', default=[1,6], nargs=2, type=int, metavar='SESSION',
                    help='sessions to use')
parser.add_argument('-v', '--verbose', action="store_const", dest="loglevel", const=logging.INFO,
                    help="enable verbose logging")
parser.add_argument('--csv-name', default='audix-data-{}.csv'.format(datetime.date.today()))

def get_segments(list_fname, do_filter=True):
    with open(list_fname, 'r') as list_f:
        segments = []
        segment = ''
        for line in list_f:
            if line and line[0] == '.':
                if segment:
                    segments.append(segment)
                segment = ''
                continue
            elif '(AP) - ' in line:
                _, text = line.split('(AP) - ')
            elif line[0] == '*':
                text = line[1:]
            else:
                text = line
            segment += ' {}'.format(text.strip())
    if segment:
        segments.append(segment)
    if do_filter:
        return [x.strip().replace('(.hhh)', '').
                replace(' .', '.').replace(' ,', ',') for x in segments]
    return [x.strip() for x in segments]

def gen_additional_columns(csv_name):
    additional_columns = {'sentence': [],
                          'word_number_in_sentence': [],
                          'total_number_of_words_in_sentence': [],
                         }
    df = pd.read_csv(csv_name)

    session_num, segment_num = -1, -1
    curr_sentence_index = 0
    word_count, total_word_count = 0, 0

    for row in df.itertuples():
        if row.session_number != session_num or row.segment_number != segment_num:
            segment = row.segment
            sentences = tokenize.sent_tokenize(segment)
            if "``The pilot, Capt." in segment: # manually fix sent_tokenize issue in ap 5
                sentences[1] += ' ' + sentences.pop()
            curr_sentence_index = 0
            word_count, total_word_count = 0, 0
            session_num, segment_num = row.session_number, row.segment_number

        sentence = sentences[curr_sentence_index]
        words = re.findall(r'\w+', sentence)
        if not total_word_count:
            total_word_count = len(words)
            sent_final = words[-1]
        sent_final = sent_final.replace('.', '')
        word = row.word

        word_count += 1 if word != 'BOUNDARY' else 0
        additional_columns['sentence'].append(sentence)
        additional_columns['word_number_in_sentence'].append(word_count)
        additional_columns['total_number_of_words_in_sentence'].append(total_word_count)
        if len(sentences) > curr_sentence_index + 1 and \
                            row.word_tobi_boundary_tone and word == sent_final:
            curr_sentence_index += 1
            word_count, total_word_count = 0, 0
        # if word_count > total_word_count:
        #     lz = pd.DataFrame(additional_columns)
    # import pdb; pdb.set_trace()

    return pd.DataFrame(additional_columns)


def main(args):
    audix_dir = args.dir
    start, end = args.sessions
    dirs = ("ap{}".format(x) for x in range(start, end + 1))
    with open(args.csv_name, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=HEADER)
        writer.writeheader()
        for session in dirs:
            segments = get_segments('{}{}.list'.format(audix_dir, session))

            session_word_count = 0
            labs = glob.glob("{}/{}/label/*.lab".format(audix_dir, session))
            if len(labs) < 2: # should use old for sessions 1 and 5
                labs = glob.glob("{}/{}/label/old/*.lab".format(audix_dir, session))
                logging.warning('session {}: using labels from label/old/'.format(session))
            for lab in labs:
                row_dicts = []
                logging.info('processing {}'.format(lab))
                segment_word_count = 0
                lab_arr = os.path.basename(lab).split('.')
                session_num, segment_num = lab_arr[0][lab_arr[0].index('p') + 1:], lab_arr[1]
                if segment_num.isnumeric():
                    segment_num, suffix = segment_num, ''
                else: # handle 7a, 7b, etc.
                    segment_num, suffix = segment_num[0], segment_num[-1]
                with open(lab, 'r') as f:
                    lines = [x.strip() for x in f.readlines()]
                hash_index = lines.index("#")
                data_rows = lines[hash_index + 1:]

                prev_word = None
                prev_pitch_acc = None
                prev_boundary = None
                ip, pk = 'N', 'N'
                for row in data_rows: # iterate through words

                    row_arr = row.split(';')
                    if not row_arr[-1]: # handle mistake in ap6.8.lab
                        row_arr.pop()
                    boundary = row_arr[-1].rsplit(maxsplit=1)[-1]
                    if boundary in PUNCTUATION:
                        boundary = row_arr[0].rsplit(maxsplit=1)[-1]
                    unmarked_boundary = boundary in UNMARKED_BOUNDARIES
                    punctuation_word = row_arr[-1].strip() in PUNCTUATION
                    ### handle mistakes in ap3
                    if '%' in row_arr[-1] or unmarked_boundary: # boundary
                        d['word_tobi_boundary_tone'] = boundary
                        prev_boundary = boundary
                        continue
                    # elif row_arr[-1] '%' == row_arr[0][-1]: # boundary
                    #     import pdb; pdb.set_trace()
                    #     d['word_tobi_boundary_tone'] = row_arr[0].rsplit(maxsplit=1)[-1]
                    #     prev_boundary = boundary
                    #     continue
                    elif punctuation_word:
                        d['word_tobi_boundary_tone'] = boundary
                        prev_boundary = boundary
                        continue
                    ###

                    if len(row_arr) != 1:
                        d = {'segment_number': segment_num,
                            'session_number': session_num,
                            'segment': segments[int(segment_num) - 1],
                            'intermediate_phrase': ip,
                            'most_prominent_pitch_accent': pk}
                        ip, pk = 'N', 'N'


                    else: # elif len(row_arr) == 1: # ip or pk row
                        if '[ip' == row_arr[0][-3:]:
                            ip = 'START'
                        elif 'ip]' == row_arr[0][-3:]:
                            ip = 'END' # will never get here since [ip always follows ip]
                        elif '[pk' == row_arr[0][-3:]:
                            pk = 'Y'
                        elif 'pk]' == row_arr[0][-3:]:
                            pk = 'N'
                        else: # phrase boundary
                            logging.warning('{}: the following row could not be processed'.format(lab))
                            print(row)
                            # rest = row_arr[0].strip()
                            # word = 'BOUNDARY'
                        continue
                    if len(row_arr) != 2:
                        logging.warning('{}: the following row could not be processed'.format(lab))
                        print(row)
                        continue
                    rest, word = [x.strip() for x in row_arr]
                    rest_arr = rest.split()

                    # session_word_count += 1
                    segment_word_count += 1
                    d['preceding_word_tobi_boundary_tone'] = prev_boundary
                    prev_boundary = ''

                    d['word'] = word
                    d['word_start_time'], _, d['word_tobi_pitch_accent'] = rest_arr
                    d['word_number_in_segment'] = segment_word_count
                    # d['word_number_in_session'] = session_word_count
                    id_arr = [session_num, segment_num, segment_word_count]
                    id_arr = [str.zfill(str(s), 2) for s in id_arr]
                    id_arr[1] = id_arr[1] + suffix
                    token_id = "{}.{}.{}".format(*id_arr)
                    d['token_id'] = token_id

                    d['preceding_word'] = prev_word
                    d['preceding_word_tobi_pitch_accent'] = prev_pitch_acc

                    prev_word, prev_pitch_acc = d['word'], d['word_tobi_pitch_accent']
                    row_dicts.append(d)
                    # except Exception as e:
                    #     logging.warning('{}: the following row could not be processed'.format(lab))
                    #     print(row)
                    #     print(e)
                    #     continue
                for d in row_dicts:
                    d['total_number_of_words_in_segment'] = segment_word_count
                    # d['total_number_of_words_in_session'] = session_word_count
                    writer.writerow(d)

    #post processing
    addtl_cols = gen_additional_columns(args.csv_name)
    df = pd.read_csv(args.csv_name)
    df = pd.concat([df, addtl_cols], axis=1).set_index('token_id').sort_index()
    df.to_csv(args.csv_name)

    print('wrote big table to {}'.format(args.csv_name))

'''
manual corrections:
## remember to change prev columns
* 01.02.25 'panel's' instead of 'panel'
* 01.05.08 'nation's' instead of 'nation'
* 01.06.08 'A's' instead of 'A'
* 01.07a.38 to 50 disfluency/repetition of previous words, delete
* 01.08.08, 01.08.09: change the two U.S. to U. and S.
* 02.07.05 'defendants' is mispelled
* 03.01.02 'Chi's' instead of 'Chi'
* 03.05.12 'wished' instead of 'wish'
* 03.05.30 'have' instead of 'of'
* 03.07.04 'Kilroy's' instead of 'Kilroy'
* 03.07.07 'Kilroy's' instead of 'Kilroy'
* 03.06.17 'school's' instead of 'school'
* 04.01.14, 15 combine into 'multi-billion'
* 04.01.27, 28 combine into 're-regulated'
* 04.02.11, 12 combine into 'de-regulated'
* 04.04.24, 25 combine into 'un-regulated'
* 04.05.* 'now is' -> 'is now' in segment and sentence columns
* 04.05.04, 05 combine into 'TV'
* 04.08.09, 10 combine into 'anti-trust'
* 04.09.10, 11 combine into 'anti-trust'
* 04.10.21 'nation's' instead of 'nation
* 04.16.34, 35 combine into 'anti-competitive'
* 04.17.* 'Co.' -> 'Company' in segment and sentence columns
* 04.19.18, 19 combine into 'anti-trust'
* 04.19.29, 30 combine into 'anti-trust'
* 04.19.68 'team's' instead of 'team'
* 04.20.* 'also should' -> 'should also' in segment and sentence columns
* 05.14.27 'everybody' instead of 'everyone'
* 05.17.15 'Broadcasting' instead of 'Broadcast'
* 05.18.15 'incidents' instead of 'accidents'
* 06.07a.47 'RISC' instead of 'risk'
* 06.07a.* 'thousand dollars' -> '' in sentence column
* 06.08.33 to 42 missing sentence 'The companies control about fifty percent of the workstation market.'
* 06.09.* 'Shaffer' -> 'Schaffer' in segment and sentence columns
* 06.10.04, 05 delete typo rows
* 06.11.11, 12 combine into 'Dataquest'
* 06.11.11, 12 combine into 'Dataquest'
* 06.11.* 'Inc.' -> 'Incorporated' in segment and sentence columns
* 06.12.14 'instruction' instead of 'instructions'
* 06.13.05 'unveil' instead of 'unvail'
* 06.13.* 'Civil' -> 'Civic' in segment and sentence columns
* 06.14.01, 02 typo: 'all' 'the' -> 'other'
* 06.14.51 'RISC' instead of 'risk'
* 06.14.27 'oh' instead of '0'
'''

if __name__ == '__main__':
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    main(args)
