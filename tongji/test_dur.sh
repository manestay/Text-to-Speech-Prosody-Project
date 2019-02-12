#!/bin/bash

. ./autobi_lib.sh

INPUT_FILES=/proj/speech/corpora/DUR/test/*.in
MODEL_DIR=dur/
MODEL_NAME=dur
OUT_DIR=dur/TextGrids

run_autobi "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $OUT_DIR
