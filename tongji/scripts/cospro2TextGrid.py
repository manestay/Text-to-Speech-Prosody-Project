'''
Converts Cospro files to TextGrid format, adding information from the folders.
* adjusted
* break
* corpus

@author: Bryan Li (bl2557@columbia.edu)
'''

import glob
import os
import string
import unicodedata
from collections import deque
from textgrid import *
from cospro_lib import *

LETTERS = set(string.ascii_letters)
SILENCE_PHONEMES = set(['sp', 'sil'])
def read_lines(filename):
    try: # TODO: make code less hacky, or set COSPRO transcripts to the same format
        with open(filename, encoding='big5') as f_corpus:
            lines = f_corpus.read().splitlines()
    except UnicodeDecodeError as e:
        try:
            with open(filename, encoding='big5hkscs') as f_corpus:
                lines = f_corpus.read().splitlines()
        except UnicodeDecodeError as e:
            with open(filename, encoding='utf16') as f_corpus:
                lines = f_corpus.read().splitlines()
    lines = [line.strip().split(' ', 2) for line in lines]
    lines = [line for line in lines if line != ['']]
    lines = [['{} {}'.format(line[0], line[1]), line[2]] for line in lines]
    return lines

def read_label_file(filename):
    to_sec = lambda x: int(float(x)) / 1000
    with open(filename) as f:
        lines = f.read().splitlines()[2:]
        lines = [line.split() for line in lines]
        lines = [[to_sec(line[0]), to_sec(line[1]), line[2]] for line in lines]
        return lines

def main():
    folders = get_folders()
    for folder in folders:
        grid_folder = '{}/TextGrids'.format(folder)
        # os.chmod(folder, 0o755)
        os.makedirs(grid_folder, exist_ok=True)
        corpus = glob.glob('{}/corpus/**.txt'.format(folder))
        if not corpus:
            continue
        lines = read_lines(corpus[0])
        for name, transcript in lines:
            characters = deque(remove_punctuation(transcript))
            break_name = '{}/break/{}.break'.format(folder, name)
            # print(break_name)
            adj_name = '{}/adjusted/{}.adjusted'.format(folder, name)
            grid_name = '{}/TextGrids/{}.TextGrid'.format(folder, name)
            try:
                breaks = read_label_file(break_name)
            except FileNotFoundError:
                print('{} not found, skipping'.format(break_name))
                continue
            try:
                phones = read_label_file(adj_name)
            except FileNotFoundError:
                print('{} not found, skipping'.format(adj_name))
                continue
            # if we made it here, then we have both break and adjusted files
            if os.path.exists(grid_name):
                continue
            grid = TextGrid()
            break_tier = PointTier('breaks')
            for b in breaks:
                break_tier.add(b[1], b[2])
            break_tier.maxTime = b[1]

            phone_tier = IntervalTier('phones')
            character_tier = IntervalTier('characters')
            character_start = 0
            character_tier_error = ''
            for p in phones:
                if p[0] == p[1]:
                    continue
                phone_tier.add(p[0], p[1], p[2])
                if p[2] in SILENCE_PHONEMES:
                    character_tier.add(p[0], p[1], '#')
                    character_start = p[1]
                elif p[2][-1].isdigit(): # SAMPA-T final
                    if not characters:
                        character_tier_error =' misalignment between transcript and adjusted file, too few characters'
                        break
                    if characters[0] in LETTERS:
                        character_tier_error ='transcript has latin characters, which are not supported'
                        break
                    if not character_tier_error:
                        character_tier.add(character_start, p[1], characters.popleft())
                    character_start = p[1]
                else: # SAMPA-T initial
                    character_start = max(character_start, p[0])
            if characters:
                character_tier_error = ' misalignment between transcript and adjusted file, too many characters'
            phone_tier.maxTime = p[1]
            character_tier.maxTime = p[1]

            grid.append(break_tier)
            grid.append(phone_tier)
            if not character_tier_error:
                grid.append(character_tier)
            else:
                print('error in {}: {}'.format(adj_name, character_tier_error))
                grid_name += '_no_character_tier' # change extension so AuToBI won't read these grids and get confused
            grid.write(grid_name)


if __name__ == "__main__":
    main()
