#!/bin/bash

. ./autobi_lib.sh

INPUT_FILES=/proj/speech/corpora/boston_radio/**/labnews/**/** # files not used for training
MODEL_DIR=burnc/
MODEL_NAME=burnc
OUT_DIR=burnc1/TextGrids
EXT=.ala

MODE=${1:-test}
if [ $MODE = "train" ]
then
    INPUT_FILES=/proj/speech/corpora/boston_radio/**/radio/**
    OUT_DIR=burnc/TextGrids_train
fi

run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR $EXT
