#!/bin/bash

. ./autobi_lib.sh
readarray -t INPUT_FILES < tongji/test.txt
INPUT_FILES=/proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/1picture_ordering_games60groups/1F-F_11X2groups/7-董研-姚玲丽/1语料/3-2_姚玲丽_董研_follower.TextGrid

MODEL_DIR=tongji/
MODEL_NAME=tongji

OUT_DIR=$MODEL_NAME/TextGrids
EXT=.TextGrid

MODE=${1:-tongji} # default mode is tongji
if [ $MODE = "train" ]
then
    readarray -t INPUT_FILES < tongji/train.txt
    OUT_DIR=dur/TextGrids_train
elif [ $MODE = "dur" ]
then
    INPUT_FILES=/proj/speech/corpora/DUR/test
    OUT_DIR=dur/TextGrids_dur
    EXT=.in
    run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
    exit 1
fi

run_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
