#!/bin/bash

#parse text dumps from wiki


fileName=$1 # the only input is the file fileName

# get rid of lines that start with *
cat $fileName | grep -v "\*" > tmp1.txt



# get rid of citation, ex. [12]
cat tmp1.txt | sed "s/\^\[[0-9]*\]//g" > tmp2.txt;
cat tmp2.txt | sed "s/\^\:[0-9,–]*//g" > tmp1.txt

# ret rid of contents stuff
cat tmp1.txt | egrep -v "\+ [0-9.]+" > tmp2.txt

# get rid of notes at end of page
cat tmp2.txt | grep -B9999 -m1 "  [0-9].*\. \^" > tmp1.txt


cat tmp1.txt | sed "s/\^\[citation needed\]//g" > tmp2.txt

cat tmp2.txt | sed "s/\^\[citation//g" > tmp1.txt

cat tmp1.txt | sed "s/needed\]//g" > tmp2.txt
cat tmp2.txt | sed "s/Main article[s]*\://g" > tmp1.txt

cat tmp1.txt | sed "s/\^*\[edit\]//g" > tmp2.txt

cat tmp2.txt | grep -iv 'retrieved\|isbn [0-9].*\-[0-9]' > tmp1.txt

cat tmp1.txt | sed -e '/From Wikipedia.*/,/Jump to/{s///p;d}' > tmp2.txt
cat tmp2.txt | grep -v "alternate copyright Wikipedia Atom feed" > tmp1.txt

cat tmp1.txt | sed -e '/Sorry\, your browser either.*/,/browser/{s///p;d}' > tmp2.txt

cat tmp2.txt | grep -v "Page semi-protected" > tmp1.txt; cat tmp1.txt > tmp2.txt
cat tmp2.txt | grep -v "This article is about the" > tmp1.txt; cat tmp1.txt > tmp2.txt
cat tmp2.txt | grep -v "For other uses, see" > tmp1.txt; cat tmp1.txt > tmp2.txt
cat tmp2.txt | grep -v "Edit this page Wikipedia" > tmp1.txt; cat tmp1.txt > tmp2.txt

cat tmp2.txt | grep -v "This article has multiple issues" > tmp1.txt
cat tmp1.txt | grep -v "these issues on the talk page" > tmp2.txt

cat tmp2.txt | grep -v "This article needs additional citations" > tmp1.txt
cat tmp1.txt | grep -v "improve this article by adding citations" > tmp2.txt
cat tmp2.txt | grep -v "material may be challenged and removed" > tmp1.txt
cat tmp1.txt | grep -v "This article possibly contains original research" > tmp2.txt
cat tmp2.txt | grep -v "verifying the claims made and adding inline citations" > tmp1.txt
cat tmp1.txt | grep -v "consisting only of original research should be removed" > tmp2.txt

cat tmp2.txt  | head -n -3 > tmp1.txt #$fileName

sed 's/^	*$//g' tmp1.txt > tmp2.txt
sed 's/  \+/ /g' tmp2.txt > tmp1.txt

# remove non alphanumeric or punctuation characters
cat tmp1.txt | tr -cd '[:alnum:][:punct:][:space:]' > tmp2.txt

#replace double new-lines with period
#cat tmp2.txt | tr "\n\n" '.' > tmp1.txt

cat tmp2.txt > $fileName

rm tmp1.txt tmp2.txt

