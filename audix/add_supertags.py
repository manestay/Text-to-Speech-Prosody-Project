import argparse
import glob
import pandas as pd
import string
import sys

from OrganizedBigTable import *

parser = argparse.ArgumentParser(description='add supertags to session tables given supertag files')
parser.add_argument('--folder', help='folder with predicted supertag outputs', default='stag_outputs/')
parser.add_argument('--prefix', help='prefix for existing session bigtables', default=None)

def main(folder=None, prefix=None):
    args = parser.parse_args()
    folder = folder or args.folder
    prefix = prefix or args.prefix

    if not folder:
        parser.print_usage()
        sys.exit(-1)

    stag_files = sorted(glob.glob(folder + '/predicted_stag/*'))
    sent_files = sorted(glob.glob(folder + '/sents/*'))
    for session_number, (stag_fname, sent_fname) in enumerate(zip(stag_files, sent_files), 1):
        if prefix:
            table_name = '{}_session{}.csv'.format(prefix, str(session_number).zfill(2))
            bigtable = OrganizedBigTable(table_name=table_name)
        else:
            bigtable = OrganizedBigTable(session_number)

        with open(stag_fname) as stag_f, open(sent_fname) as sent_f:
            stag_lines = stag_f.readlines()
            sent_lines = sent_f.readlines()
        stags, words = [], []
        for stag_line, sent_line in zip(stag_lines, sent_lines):
            stags.extend(stag_line.split())
            words.extend(sent_line.split())
        assert len(stags) == len(words)
        word_stag_list = [] # list of (word, stag) tuples
        for stag, word in zip(stags, words):
            if any((word[i] not in string.punctuation) for i in range(len(word))):
                word_stag_list.append((word, stag))
        bigtable.addColumnToDataFrame(word_stag_list, 'supertag')
        bigtable.saveToCSV(False)


if __name__ == '__main__':
    main()
