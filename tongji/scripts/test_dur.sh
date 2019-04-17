#!/bin/bash

. scripts/autobi_lib.sh

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
then
    # INPUT_FILES="tongji_files/3-1_无控制_王静_陈姗姗_giver.TextGrid"
    readarray -t INPUT_FILES < tongji/test.txt
    OUT_DIR=$MODEL_NAME/TextGrids_tongji
    EXT=.TextGrid
    run_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
    exit 0
fi

run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
