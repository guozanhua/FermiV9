#!/bin/bash

SCRIPT_PATH="${BASH_SOURCE[0]}";
if ([ -h "${SCRIPT_PATH}" ]) then
  while([ -h "${SCRIPT_PATH}" ]) do SCRIPT_PATH=`readlink "${SCRIPT_PATH}"`; done
fi
pushd . > /dev/null
cd `dirname ${SCRIPT_PATH}` > /dev/null

infoSource=$1
origInfoSource=$infoSource
infoSource="${infoSource// /_}" #replace spaces with '_' (should already be this way)

fileName=${origInfoSource,,}
fileName=${fileName// /_}
fileName="../Docs/"$fileName".txt"

touch "$fileName"
echo "" > "$fileName"

fileNameTmp="../Docs/source_concat_tmp.txt"

touch "$fileNameTmp"



#echo "Searching Wikipedia for $infoSource..."

lynx -dump -nolist http://en.wikipedia.org/wiki/$infoSource > "$fileNameTmp"

# check if it didn't work, and try a different capitalization
if [ $? != 0 ]
then

	#echo "Orig infoSource = $origInfoSource"
	IFS=' '
	#try different capitalization
	infoSource=${origInfoSource,,}
	infoSource="${infoSource//_/ }"
	infoSource=( $infoSource )
	infoSource=${infoSource[*]^}
	infoSource="${infoSource// /_}"
	#echo "Searching Wikipedia for $infoSource..."
	lynx -dump -nolist http://en.wikipedia.org/wiki/$infoSource > "$fileNameTmp"
fi

if [ $? != 0 ]
then
	#echo "Wikipedia text dump with lynx failed on article $infoSource."
	rm $fileNameTmp
else
	bash wikiParse.sh "$fileNameTmp"

	cat "$fileNameTmp" >> "$fileName"
fi
