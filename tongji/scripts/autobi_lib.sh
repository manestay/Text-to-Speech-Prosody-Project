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
    EXT=$4
    MODE=${5:-training}
    mkdir -p $MODEL_DIR

    if [ -f "$INPUT_FILES" ]; then
        IFS=""
        FILES="$INPUT_FILES"
    elif [ -d "$INPUT_FILES" ]; then
        FILES="$INPUT_FILES"/*$EXT
    else
        IFS="," # array with commas
        FILES=$INPUT_FILES
    fi

    input_flag="-${MODE}_filenames"

}

train_autobi() {
    train_common "$@"

    java -cp AuToBI.jar edu.cuny.qc.speech.AuToBI.AuToBITrainer \
    -log4j_config_file=log4j.properties \
    $input_flag="$FILES" \
    -pitch_accent_detector=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_det.model \
    -pitch_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.pitch_acc_class.model \
    -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
    -intermediate_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inter_pb_det.model \
    -phrase_accent_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_class.model \
    -phrase_accent_boundary_tone_classifier=${MODEL_DIR}/${MODEL_NAME}.phrase_acc_bt_class.model
}

train_autobi_limited() {
    train_common "$@"

    java -Xmx10g -cp AuToBI.jar edu.cuny.qc.speech.AuToBI.AuToBITrainer \
    -log4j_config_file=log4j.properties \
    $input_flag="$FILES" \
    -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model
}

run_common() {
    INPUT_FILES=$1
    MODEL_DIR=$2
    MODEL_NAME=$3
    OUT_DIR=$4
    EXT=$5
    MODE=${6:-input}
    mkdir -p $MODEL_DIR
    mkdir -p $OUT_DIR
    if [ -f "$INPUT_FILES" ]; then
        IFS=""
        FILES="$INPUT_FILES"
    elif [ -d "$INPUT_FILES" ]; then
        FILES="$INPUT_FILES"/*$EXT
    else
        IFS="," # array with commas
        FILES=$INPUT_FILES
    fi

    input_flag="-${MODE}_file"
}

run_autobi() {
    run_common "$@"
    for input_file in $FILES
    do
        WAV="${input_file%.*}".wav
        OUT_FILE=$OUT_DIR/$(basename "$input_file" $EXT)_pred.TextGrid
        OUT_LOG="${OUT_FILE%.*}".log

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

        java -jar AuToBI.jar $input_flag="$input_file" \
        -wav_file="$WAV" \
        -log4j_config_file=log4j.properties \
        -intonational_phrase_boundary_detector=${MODEL_DIR}/${MODEL_NAME}.inton_pb_det.model \
        -out_file=$OUT_FILE |& tee $OUT_LOG
    done
}
