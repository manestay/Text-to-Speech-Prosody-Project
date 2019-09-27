#!/bin/bash
dir=tongji_all
~/software/kaldi-trunk/egs/rm/s5/utils/utt2spk_to_spk2utt.pl $dir/utt2spk > $dir/spk2utt
