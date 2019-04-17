#!/bin/bash

. scripts/autobi_lib.sh

readarray -t INPUT_FILES < /proj/tts/data/COSPRO/folders.txt
INPUT_FILES=( "${INPUT_FILES[@]/%/TextGrids\/*.TextGrid}" )
# INPUT_FILES="/proj/tts/data/COSPRO/Cospro3/COSPRO_09/M053/sptn_read/TextGrids/*.TextGrid"
MODEL_DIR=cospro/
MODEL_NAME=cospro
EXT=.TextGrid

train_autobi_limited "$INPUT_FILES" $MODEL_DIR $MODEL_NAME $EXT cospro
