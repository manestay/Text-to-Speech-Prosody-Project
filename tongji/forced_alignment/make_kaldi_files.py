""" Make the following files for kaldi:
    text segments wav.scp utt2spk spk2utt
Based on https://www.eleanorchodroff.com/tutorial/kaldi/training-acoustic-models.html#create-files-for-datatrain
"""

import os
from praatio import tgio
import jieba

from textgrid_lib import get_ipus

unaccessible_files = []
#     "2-1_宗立志_虞志浩_承载句.TextGrid",
#     "43-2_诸翔云_王宁_giver.TextGrid",
#     "11-2_朱奕_庄艳芳_承载句.TextGrid",
#     "52-1_郭靖_沈浩_分类.TextGrid",
# ]

def make_transcripts(data_dir, transcripts_dir):
    for root, dirnames, filenames in os.walk(data_dir, topdown=False):
        for filename in filenames:
            if filename.endswith('.TextGrid'):
                if filename in unaccessible_files:
                    print(filename, 'not found')
                    continue
                basename = os.path.splitext(filename)[0]
                transcript_subdir = os.path.join(transcript_dir, root.split('/', 1)[-1])
                transcript_name = os.path.join(transcript_subdir, basename + '.txt')

                grid_name = os.path.join(root, filename)
                tg = tgio.openTextgrid(grid_name)
                ipus, _, _ = get_ipus(tg)

                os.makedirs(transcript_subdir, exist_ok=True)
                with open(transcript_name, 'w') as f:
                    for xmin, xmax, ipu in zip(xmins, xmaxs, ipus):
                        f.write('{}\t{}\t{}\n'.format(xmin, xmax, ipu))
                print('wrote to', transcript_name)

def make_kaldi_files(save_dir, data_dir, transcript_dir):
    text_name = os.path.join(save_dir, 'text')
    wavscp_name = os.path.join(save_dir, 'wav.scp')
    utt2spk_name = os.path.join(save_dir, 'utt2spk')
    segments_name = os.path.join(save_dir, 'segments')

    text_f = open(text_name, 'w')
    wavscp_f = open(wavscp_name, 'w')
    utt2spk_f = open(utt2spk_name, 'w')
    segments_f = open(segments_name, 'w')

    for root, dirnames, filenames in os.walk(data_dir):
        for filename in filenames:
            if not filename.endswith('.TextGrid'):
                continue
            file_id = os.path.splitext(filename)[0]
            spk_str, recording_no, session = file_id.split('--')
            speaker = spk_str.split('_')[0]
            wav_name = os.path.join(root, file_id + '.wav')
            if not os.path.exists(wav_name):
                print(wav_name, 'not found')
                continue
            transcript_subdir = os.path.join(transcript_dir, root.split('/', 1)[-1])
            transcript_name = os.path.join(transcript_subdir, file_id + '.txt')
            with open(transcript_name, 'r') as f:
                lines = [x for x in f.readlines()]

            for i, line in enumerate(lines, 1):
                suffix = '{}'.format(str(i).zfill(4))
                utt_id = '{}-{}'.format(file_id, suffix)
                xmin, xmax, ipu = line.split('\t')
                ipu = ipu.strip()
                if not ipu:
                    continue
                segments_f.write('{} {} {} {}\n'.format(utt_id, file_id, xmin, xmax))
                text_f.write('{} {}\n'.format(utt_id, ipu))
                utt2spk_f.write('{} {}\n'.format(utt_id, speaker))
            wavscp_f.write('{} {}\n'.format(file_id, wav_name))
    text_f.close()
    wavscp_f.close()
    utt2spk_f.close()
    segments_f.close()

if __name__ == "__main__":
    data_dir = 'raw_data/'
    transcript_dir = 'transcripts_flat/'
    save_dir = 'tongji_all'
    make_transcripts(data_dir, transcript_dir)
    make_kaldi_files(save_dir, data_dir, transcript_dir)
