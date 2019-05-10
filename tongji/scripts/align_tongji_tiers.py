"""
For all Tongji Games TextGrids, creates an new breaks tier that is aligned to the breaks of the
syllable tier.

According to Shirley:
"The boundaries in IPU tier was automatically made by SPPAS, so some non-lingual voice from the
speaker or some weak voice from the other interlocutor were also recognized by the software. The
manual check and modification of these boundaries by several annotators were all made in the
Syllable tier. And all the data were extracted from Syllable tier. Thus, all the analyses could be
done by these data from the Syllable tier. At that time, the boundaries automatically recognized in
IPU tier were not modified because it was not necessary. "

@author: Bryan Li (bl2557@columbia.edu)
"""

from textgrid import *
import os
import subprocess

MIN_TIME = .1 # if the syllables tier interval has no mark, assume words longer than this (in sec)
               # are boundaries

def get_break_tier(grid):
    """
    Generates a break tier by considering only the corrected boundaries from the syllables tier.
    """
    breaks_tier = PointTier('breaks')
    for word in grid.getFirst('syllable'):
        if word.mark == '#' or \
           (word.mark == '' and word.maxTime - word.minTime > MIN_TIME):
            breaks_tier.add(word.minTime, '#')
        # elif word.mark == '':
        #     print(word, word.maxTime - word.minTime, grid.name)
    breaks_tier.maxTime = word.minTime
    if breaks_tier.points[0].time == 0:
        breaks_tier.removePoint(breaks_tier.points[0])
    return breaks_tier


def main():
    if not os.path.exists('tongji/all.txt'):
        subprocess.call(". scripts/autobi_lib.sh", shell=True)
        subprocess.call("generate_tongji_list", shell=True)
    with open('tongji/all.txt') as f:
        grids = [x.strip() for x in f]
    # grids = ['/proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/1picture_ordering_games60groups/1F-F_11X2groups/7-董研-姚玲丽/1语料/3-2_姚玲丽_董研_follower.TextGrid']
    for grid_name in grids:
        grid = TextGrid(grid_name)
        grid.read(grid_name)
        while grid.tiers[-1].name == 'breaks':
            grid.pop()
        grid.append(get_break_tier(grid))
        # new_filename = os.path.splitext(grid_name)[0] + '_new.TextGrid'
        grid.write(grid_name)


if __name__ == "__main__":
    main()
