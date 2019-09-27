header=/efs/users/bryali/corpora/tongji/header.txt

# direct the terminal to the directory with the newly split session files
# ensure that the RegEx below will capture only the session files
# otherwise change this or move the other .txt files to a different folder

mkdir -p ~/tmp/
cd split_alignments/
for i in *.txt;
do
    cat "$header" "$i" > ~/tmp/xx.$$
    mv ~/tmp/xx.$$ "$i"
done;
