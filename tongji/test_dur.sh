#!/bin/bash

. ./autobi_lib.sh

INPUT_FILES=/proj/speech/corpora/DUR/test
MODEL_DIR=dur/
MODEL_NAME=dur
OUT_DIR=dur/TextGrids
EXT=.in

MODE=${1:-test} # default mode is test
if [ $MODE = "train" ]
then
    INPUT_FILES=/proj/speech/corpora/DUR/train
    OUT_DIR=dur/TextGrids_train
elif [ $MODE = "tongji" ]
then # need to fix spaces in tongji, use files copied locally for now
    INPUT_FILES="1 space"
    # INPUT_FILES="/proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/1picture_orderding _games60groups/1F-F_11X2groups/11黄竞男-陈晓云/1语料/f-f 黄竞男-陈晓云 3-15-2/27-2有控制 陈晓云-黄竞男 follower.TextGrid"
    OUT_DIR=dur/TextGrids_tongji
    EXT=.TextGrid
fi

run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT
