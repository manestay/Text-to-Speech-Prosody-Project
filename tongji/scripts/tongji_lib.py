'''
Library for various functions for the Tongji corpus.

@author: Bryan Li (bl2557@columbia.edu)
'''

import os
import re
import subprocess

TRANSCRIPTS_DIR = "/proj/afosr/corpora/Tongji_Games_Corpus/transcripts"
command = "find /proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/ -name '*.TextGrid' > tongji/all.txt"

def generate_list():
    subprocess.call(command, shell=True)
    names = ["吴炜洁", "葛慧婷", "邱梦娇", "郇宇", "姚玲丽", "唐光丘"] # arbitrarily selected test names
    patterns = [r"\d{{1,2}}-\d_{}*".format(x) for x in names]
    with open("tongji/train.txt", "w") as f_train, open("tongji/test.txt", "w") as f_test, \
        open("tongji/all.txt", "r") as f_all:
        for line in f_all:
            if any([re.match(pattern, os.path.basename(line)) for pattern in patterns]):
                # if "giver" not in line and "follower" not in line:
                    f_test.write(line)
            else:
                # if "giver" not in line and "follower" not in line:
                    f_train.write(line)

def check_list():
    with open("tongji/all.txt", "r") as f_all:
        for line in f_all:
            wav = os.path.splitext(line.strip())[0] + ".wav"
            if not os.path.exists(wav):
                print(line.strip())
                print("{} does not exist".format(wav))

def get_transcript_list(transcripts_dir=TRANSCRIPTS_DIR):
    transcripts = []
    for root, dirs, files in os.walk(transcripts_dir, topdown=False):
        for name in files:
            if name.endswith('.txt'):
                transcripts.append(os.path.join(root, name))
    return transcripts

if __name__ == "__main__":
    pass
