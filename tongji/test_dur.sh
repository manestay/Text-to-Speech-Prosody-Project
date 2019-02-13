#!/bin/bash

. ./autobi_lib.sh

INPUT_FILES=/proj/speech/corpora/DUR/test/*.in
MODEL_DIR=dur/
MODEL_NAME=dur
OUT_DIR=dur/TextGrids

MODE=${1:-test}
if [ $MODE = "train" ]
then
    INPUT_FILES=/proj/speech/corpora/DUR/train/*.in
    OUT_DIR=dur/TextGrids_train
fi

run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR
