#!/bin/bash

. scripts/autobi_lib.sh

readarray -t INPUT_FILES < tongji/train.txt
INPUT_FILES=$(join_by , "${INPUT_FILES[@]}")
# INPUT_FILES=/proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/2picture_classifying_games57groups/classifying_after_ordering_28groups/F-F_9groups/8-王佳-周盼盼/1语料/26-1_王佳_周盼盼_承载句.TextGrid,/proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/2picture_classifying_games57groups/classifying_after_ordering_28groups/F-F_9groups/8-王佳-周盼盼/1语料/29-1_王佳_周盼盼_分类规则.TextGrid
MODEL_DIR=tongji/
MODEL_NAME=tongji
EXT=.TextGrid
train_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $EXT tongji
