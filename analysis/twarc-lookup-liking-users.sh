#!/bin/bash

# Cool terminal print colors:
NORMAL=$(tput sgr0)
RED=$(tput setaf 202)
GREEN=$(tput setaf 046)
BLUE=$(tput setaf 153)
ORANGE=$(tput setaf 130)
MAGENTA_BLINK=$(tput blink setaf 201)

# NEWEST=$(ls -td ../Pull*/ | head -1)

printf "${GREEN}
        So, you want to look up some liking users, ai?

        Please put your bearer token as the only thing in a file,
        then supply the full path (e.g. './token1')
        >>> "
read BEARERFILE

mkdir -p ./Late-liking-users

if [ -f $BEARERFILE ]; then
  BEARER=$(cat "$BEARERFILE")
  printf "${GREEN}
        Neat, I see $BEARERFILE
        What file with tweet IDs should we loop through?${RED}
        >>> "
else
printf "${RED}
        Can't find that file. Quitting.
"${NORMAL}
exit
fi

read FILE
if [ -f $FILE ]; then
  NUMBER_OF_TWEETS_IN_FILE=$(cat $FILE | wc -l)
  printf "${GREEN}
        Neat, I see $FILE with $NUMBER_OF_TWEETS_IN_FILE lines
        and go in 3 seconds!
"${NORMAL}
  sleep 3
  COUNTER=0
else
  printf "${RED}
        Can't find that file. Quitting.
"${NORMAL}
  exit
fi

while IFS= read -r line; do
    let COUNTER=COUNTER+1
    printf "${GREEN}
        Line $COUNTER of $NUMBER_OF_TWEETS_IN_FILE
"${NORMAL}
    SAVEPATH=./Late-liking-users/$line.jsonl
    if [ -f $SAVEPATH ]
    then
      echo "Tweet ID: $line -- File exists"
    else
      echo "Tweet ID: $line"
      twarc2 --bearer-token $BEARER liking-users $line $SAVEPATH
    fi

done < "$FILE"

printf "${MAGENTA_BLINK}
        DONE!${NORMAL}
"
