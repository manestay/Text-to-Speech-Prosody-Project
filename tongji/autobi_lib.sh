#!/bin/bash

# this script contains functions for training and running AuToBI

echo_and_run() { echo "\$ $@" ; "$@" ; }
join_by() { local IFS="$1"; shift; echo "$*"; }

# shuf --random-source=<(get_seeded_random 42)
get_seeded_random() {
    seed="$1"
    openssl enc -aes-256-ctr -pass pass:"$seed" -nosalt </dev/zero 2>/dev/null
}

train_common() {
    INPUT_FILES=$1
    MODEL_DIR=$2
    MODEL_NAME=$3
    MODE=$4
    mkdir -p $MODEL_DIR

    if [[ "$(declare -p INPUT_FILES)" =~ "declare -a" ]]; then
        FILES=$(join_by , "${INPUT_FILES[@]}") # array to comma-delimited string
    elif [ -f "$INPUT_FILES" ]; then
        IFS=""
        FILES="$INPUT_FILES"
    elif [ -d "$INPUT_FILES" ]; then
        FILES="$INPUT_FILES"/*$EXT
    else
        FILES=$INPUT_FILES
    fi

    input_flag="-training_filenames"
    if [[ $MODE = "tongji" ]]; then
        input_flag="-tongji_filenames"
    fi
}

train_autobi() {
    train_common "$@"

    java -cp AuToBI.jar edu.cuny.qc.speech.AuToBI.AuToBITrainer \
    -log4j_config_file=log4j.properties \
    $input_flag=$FILES \
    -pitch_accent_detector=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_det.model \
    -pitch_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_class.model \
    -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
    -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model \
    -phrase_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_class.model \
    -phrase_accent_boundary_tone_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_bt_class.model
}

train_autobi_limited() {
    train_common "$@"

    java -cp AuToBI.jar edu.cuny.qc.speech.AuToBI.AuToBITrainer \
    -log4j_config_file=log4j.properties \
    $input_flag=${FILES[@]} \
    -charset=utf16 \
    -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
    -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model
}

run_common() {
    INPUT_FILES=$1
    MODEL_DIR=$2
    MODEL_NAME=$3
    OUT_DIR=$4
    EXT=$5
    MODE=$6
    mkdir -p $MODEL_DIR
    mkdir -p $OUT_DIR

    if [[ "$(declare -p INPUT_FILES)" =~ "declare -a" ]]; then
        FILES="${INPUT_FILES[@]}"
    elif [ -f "$INPUT_FILES" ]; then
        IFS=""
        FILES="$INPUT_FILES"
    elif [ -d "$INPUT_FILES" ]; then
        FILES="$INPUT_FILES"/*$EXT
    else
        FILES=$INPUT_FILES
    fi

    input_flag="-input_file"
    if [ $MODE = "tongji" ]; then
        input_flag="-tongji_file"
    fi
}

run_autobi() {
    run_common "$@"
    for input_file in $FILES
    do
        WAV="${input_file%.*}".wav
        OUT_FILE=$OUT_DIR/$(basename "$input_file" $EXT)_pred.TextGrid
        OUT_LOG="${OUT_FILE%.*}".log

        # echo_and_run \
        java -jar AuToBI.jar $input_flag="$input_file" \
        -wav_file="$WAV" \
        -log4j_config_file=log4j.properties \
        -pitch_accent_detector=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_det.model \
        -pitch_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_class.model \
        -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
        -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model \
        -phrase_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_class.model \
        -phrase_accent_boundary_tone_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_bt_class.model \
        -out_file=$OUT_FILE |& tee $OUT_LOG
    done
}

run_autobi_limited() {
    run_common "$@"
    for input_file in $FILES
    do
        WAV="${input_file%.*}".wav
        OUT_FILE=$OUT_DIR/$(basename "$input_file" $EXT)_pred.TextGrid
        OUT_LOG="${OUT_FILE%.*}".log

        # echo_and_run \
        java -jar AuToBI.jar $input_flag="$input_file" \
        -wav_file="$WAV" \
        -log4j_config_file=log4j.properties \
        -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
        -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model \
        -charset=utf16 \
        -out_file=$OUT_FILE |& tee $OUT_LOG
    done
}

generate_tongji_list() {
    find /proj/afosr/corpora/Tongji_Games_Corpus/data_annotation/ -name "*.TextGrid" > tongji/all.txt
    python3 -c \
'import os, re
names = ["吴炜洁", "葛慧婷", "邱梦娇", "郇宇", "姚玲丽", "唐光丘"]
patterns = [r"\d{{1,2}}-\d_{}*".format(x) for x in names]
with open("tongji/train.txt", "w") as f_train, open("tongji/test.txt", "w") as f_test, \
     open("tongji/all.txt", "r") as f_all:
    for line in f_all:
        if any([re.match(pattern, os.path.basename(line)) for pattern in patterns]):
            f_test.write(line)
        else:
            f_train.write(line)'
}
