#!/bin/bash

. scripts/autobi_lib.sh

readarray -t INPUT_FILES < /proj/tts/data/COSPRO/test.txt
INPUT_FILES=( "${INPUT_FILES[@]/%/\/TextGrids\/*.TextGrid}" ) # append *.TextGrid to array
INPUT_FILES=$(join_by , "${INPUT_FILES[@]}")
MODEL_DIR=cospro/
MODEL_NAME=cospro
OUT_DIR=cospro/TextGrids
EXT=.TextGrid

MODE=${1:-cospro}
if [ $MODE = "train" ]
then
    INPUT_FILES=/proj/speech/corpora/DUR/train
    OUT_DIR=dur/TextGrids_train
elif [ $MODE = "tongji" ]
then
    # INPUT_FILES="tongji_files/3-1_无控制_王静_陈姗姗_giver.TextGrid"
    readarray -t INPUT_FILES < tongji/test.txt
    INPUT_FILES=$(join_by , "${INPUT_FILES[@]}")
    OUT_DIR=$MODEL_NAME/TextGrids_tongji
    run_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
    exit 0
elif [ $MODE = "dur" ]
then
    MODE=input
    INPUT_FILES=/proj/speech/corpora/DUR/test
    OUT_DIR=cospro/TextGrids_dur
    EXT=.in
fi


run_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT $MODE
