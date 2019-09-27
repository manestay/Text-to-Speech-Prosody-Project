import itertools
import os

import pandas as pd
from praatio import tgio

from textgrid_lib import get_ipus, load_flat2orig, load_word2phone

ALIGNMENTS_DIR = "./split_alignments"
GRIDS_DIR = "./TextGrids"
os.makedirs(GRIDS_DIR, exist_ok=True)
HEADER = "file_utt file id ali startinutt dur phone start_utt end_utt start end".split()
UNK = set(['spn', 'sil'])
def make_textgrid(df, out_name, orig_name=None, word2phone=None):
    if orig_name:
        tg = tgio.openTextgrid(orig_name)
    else:
        tg = tgio.Textgrid()
    phones_list = []
    syllables_list = []
    curr_syllable = []
    for tup in df[['start', 'end', 'phone']].itertuples():
        phones_list.append((tup.start, tup.end, tup.phone))
        if tup.phone in set(['spn', 'sil']):
            # pass
            syllables_list.append((tup.start, tup.end, tup.phone))
            curr_syllable = []
        elif len(tup.phone) > 2 and tup.phone[-2] == '_': # final
            curr_syllable.append(tup.phone)
            syllables_list.append((initial_start, tup.end, ' '.join(curr_syllable)))
            curr_syllable = []
        else: # initial
            curr_syllable.append(tup.phone)
            initial_start = tup.start

    phone_tier = tgio.IntervalTier('phone', phones_list)
    syllable_tier = tgio.IntervalTier('syllable\_phones', syllables_list)
    if orig_name and word2phone:
        ipus, xmins, xmaxs = get_ipus(tg)
        word_list, unmatched_words, break_list = make_word_list(syllable_tier, ipus, word2phone, out_name, xmaxs)
        word_tier = tgio.IntervalTier('word', word_list)
        tg.addTier(word_tier)

    tg.addTier(phone_tier)
    tg.addTier(syllable_tier)

    if not tg.tierDict['breaks'].entryList:
        tg.removeTier('breaks')
        break_tier = tgio.PointTier('break', break_list)
        tg.addTier(break_tier)
    else:
        print(out_name, 'has break tier, did not write new one')
    os.makedirs(os.path.dirname(out_name), exist_ok=True)
    tg.save(out_name, useShortForm=False)
    print('wrote to {}, # matched: {}, # unmatched: {}'.format(
        out_name, len(word_list), len(unmatched_words)))
    return len(word_list), len(unmatched_words)

def make_word_list(syllable_list, ipus, word2phone, out_name='', ipu_ends=[]):
    """
    Returns
        1) list of words with start and end timestamps.
        2) list of unmatched words and information about them
        3) list of breaks with timestamp.
    """
    syllable_entries = syllable_list.entryList
    ipu_words_list = [ipu.split(' ') for ipu in ipus]
    num_chars = sum([len(x) for x in ipu_words_list])
    num_syllabs = len(syllable_entries)

    word_tier_list = []
    break_tier_list = []
    unmatched_words = []
    ii = 0
    if ipu_ends:
        assert len(ipu_ends) == len(ipu_words_list)
    for idx, (ipu, ipu_end) in enumerate(zip(ipu_words_list, ipu_ends)):
        if ii >= len(syllable_entries): break
        for idx2, word in enumerate(ipu):
            if not word: continue
            chars_in_word = len(word)
            offset = 1
            while ii < len(syllable_entries) and syllable_entries[ii].label in UNK:
                ii += 1
                offset += 1
            if ii >= len(syllable_entries): break
            curr_entries = syllable_entries[ii:ii+chars_in_word]
            start, end = curr_entries[0].start, curr_entries[-1].end
            if ipu_ends and end > ipu_end:
                # impossible to have end stamp of the candidate > the ipu, so skip
                continue

            if not curr_entries: continue
            phones = tuple([x.label for x in curr_entries])
            word_prons = word2phone.get(word, get_unk_word(word, word2phone))
            matched = match_word_phones(word_prons, phones)
            if not matched:
                unmatched_words.append((word, word_prons, phones, idx, ipu))
            else:
                ii += len(word)
                word_tier_list.append((start, end, word))
                break_label = 4 if idx2 == len(ipu) - 1 else 1
                break_tier_list.append((end, break_label))
    return word_tier_list, unmatched_words, break_tier_list

def get_unk_word(word, word2phone):
    # [word2phone[x][0] for x in word]
    char_prons_all = [word2phone[x] for x in word]
    for i, char_prons in enumerate(char_prons_all):
        char_prons_all[i] = [x[0] for x in char_prons]
    possible_prons = list(itertools.product(*char_prons_all))
    return possible_prons

def match_word_phones(word_prons, phones):
    # print(word_prons, phones)
    return phones in word_prons

def main(flat=True):
    flat2orig = load_flat2orig()
    word2phone = load_word2phone()
    total_matched, total_unmatched = 0, 0
    for fname in os.listdir(ALIGNMENTS_DIR):
        txt_name = os.path.join(ALIGNMENTS_DIR, fname)
        basename = fname.rsplit('.', 1)[0] + '.TextGrid'
        orig_name = flat2orig[basename]
        if flat:
            out_name = os.path.join(GRIDS_DIR, basename)
        else:
            out_name = os.path.join(GRIDS_DIR, orig_name)
        with open(txt_name, 'r') as f:
            df = pd.read_csv(f, sep='\t', names=HEADER)
        num_matched, num_unmatched = make_textgrid(df, out_name, orig_name=orig_name, word2phone=word2phone)
        total_matched += num_matched
        total_unmatched += num_unmatched
    print('matched {} total, unmatched {} total ({}%)'.format(
        total_matched, total_unmatched, total_unmatched * 100 / (total_matched + total_unmatched)))

if __name__ == "__main__":
    flat = False
    main(flat)
