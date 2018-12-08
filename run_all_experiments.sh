#!/bin/bash

echo_and_run() { echo "\$ $@" ; "$@" ; }

audix=audix/audix-data-2018-12-07.csv
burnc=burnc/tables/burnc-20181207.csv
games=games/games-data-20181128.csv

echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $audix > runs/break_audix_audix.txt & \
echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $burnc > runs/break_burnc_burnc.txt &  wait
echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $audix --test $burnc > runs/break_audix_burnc.txt & \
echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $burnc --test $audix > runs/break_burnc_audix.txt & wait
echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $games > runs/break_games_games.txt & \
echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $games --test $burnc > runs/break_games_burnc.txt & wait
echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $games --test $audix > runs/break_games_audix.txt & \
\
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $audix > runs/accent_audix_audix.txt & wait
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $burnc > runs/accent_burnc_burnc.txt & \
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $audix --test $burnc > runs/accent_audix_burnc.txt & wait
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $burnc --test $audix > runs/accent_burnc_audix.txt & \
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $games > runs/accent_games_games.txt & wait
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $games --test $burnc > runs/accent_games_burnc.txt & \
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $games --test $audix > runs/accent_games_audix.txt & wait
\
echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $burnc --test $games > runs/break_burnc_games.txt & \
echo_and_run python3 configurable_classifier.py break --range -1 -1 --train $audix --test $games > runs/break_audix_games.txt & \
\
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $burnc --test $games > runs/accent_burnc_games.txt & \
echo_and_run python3 configurable_classifier.py accent --range -1 -1 --train $audix --test $games > runs/accent_audix_games.txt & wait
