'''
Library for various functions for the Cospro corpus.

@author: Bryan Li (bl2557@columbia.edu)
'''

import glob
import os
import sys
import unicodedata

tbl = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))
ALL_LIST = '/proj/tts/data/COSPRO/folders.txt'
TRAIN_LIST = '/proj/tts/data/COSPRO/train.txt'
TEST_LIST = '/proj/tts/data/COSPRO/test.txt'

def remove_punctuation(text):
    return text.translate(tbl)

def get_folders(out_name=ALL_LIST):
    if os.path.exists(out_name):
        print('reading folders from {}...'.format(out_name))
        with open(out_name) as f:
            return f.read().splitlines()

    print('searching for break folders in Cospro...')
    folders = set()
    for root, dirs, files in os.walk("/proj/tts/data/COSPRO/"):
        if not root.startswith('/proj/tts/data/COSPRO/Cospro'): # only process Cospro discs
            continue
        for d in sorted(dirs):
            if d.endswith('break'): # only process folders with break info
                folder = os.path.join(root, d[:-6])
                folders.add(folder)

    with open(out_name, 'w') as f:
        for folder in sorted(folders):
            f.write(folder +'\n')
    return folders

def get_textgrids(out_name=None):
    """
    Returns a list of Cospro TextGrid files.
    """
    folders = get_folders()
    print("getting textgrids...")
    grids = []
    for folder in folders:
        grids.extend(glob.glob('{}/TextGrids/*'.format(folder)))
    if out_name:
        print('writing to {}...'.format(out_name))
        with open(out_name, 'w') as f:
            for grid in grids:
                f.write(grid + '\n')

    return grids

def make_symlinks():
    """
    AuToBITrainer requires wav files to be in the same folder as TextGrid files. This function
    creates symlinks to wav files in the TextGrid folders.
    """
    folders = get_folders()
    print("making symlinks...")
    for folder in folders:
        # print("making symlinks for {}...".format(folder))
        wavs = glob.glob("{}/wav/*.wav".format(folder))
        grid_folder = "{}/TextGrids/".format(folder)
        for wav in wavs:
            if 'TOSPRO' in wav:
                basename = 'C' + os.path.basename(wav)[1:]
            else:
                basename = os.path.basename(wav)
            symlink_name = grid_folder + basename
            if not os.path.exists(symlink_name):
                os.symlink(wav, grid_folder + basename)

def generate_cospro_list(all_list=ALL_LIST, train_list=TRAIN_LIST, test_list=TEST_LIST):
    with open(train_list, "w") as f_train, open(test_list, "w") as f_test, open(all_list, "r") as f_all:
        for line in f_all:
            if "COSPRO_02/Female/F01" in line or "COSPRO_02/Male/M00" in line:
                f_test.write(line)
            else:
                f_train.write(line)

if __name__ == "__main__":
    generate_cospro_list()
