#!/bin/bash
kaldi_root=~/software/kaldi-trunk/
mfccdir=mfcc
train_cmd=run.pl
tongji_dir=/efs/users/bryali/corpora/tongji/data_annotation/

for x in $(find $tongji_dir -name "*.wav")
do
    steps/make_mfcc_pitch.sh --cmd "$train_cmd" --nj 20 --pitch_conf /conf/pitch.conf \
    $x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data_annotation
    steps/compute_cmvn_stats.sh $x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data_annotation
done
