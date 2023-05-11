#!/bin/bash

# Cool terminal print colors:
NORMAL=$(tput sgr0)
RED=$(tput setaf 202)
GREEN=$(tput setaf 046)
BLUE=$(tput setaf 153)
ORANGE=$(tput setaf 130)
MAGENTA_BLINK=$(tput blink setaf 201)

NEWEST=$(ls -td ../Pull*/ | head -1)

printf "${GREEN}
        So, you want to look up botscores of users (likers and retweeters) 
        using Botometer *Lite*?
        ${RED}

        The newest data directory I see is
        $NEWEST

        ${RED}Is that the directory of your data? (y/n)${NORMAL}\n
        >>> "
read ynchoice

case "$ynchoice" in
  y|Y ) printf "${GREEN}
        Great, I look up the botscore of users from $NEWEST
        FYI: Looking up around 60.000 users takes less than one hour. 
        One API call can look up 100 users' score.
        The ULTRA plan for the botometer API gives you 200 calls per day
        and charges 0.01$ for each additionl call.
        So, say looking up additional 50.000 users will cost 5$.
         ${NORMAL}\n"
        export NEWEST
        python3 -c "import os; from resources.botscores_botometer import *;\
                    likers_botlite(os.getenv('NEWEST')); retweeters_botlite(os.getenv('NEWEST'))"
        printf "${MAGENTA_BLINK}\n  DONE!${NORMAL}\n\n";;
  n|N ) printf "
        Then please supply the path of the pull data folder:${ORANGE}
        (use ../Pull-DD-MM-YYYY-hour:minute:second
        for Pull-... in the directory above this one)${NORMAL}\n
        >>> "
    read CHOICE
    if [ -d $CHOICE ]; then
      printf "${GREEN}
        Great, I see $CHOICE
        and will look up botscores!
        We don't quite know how long this takes! 
        Shouldn't take too long though!${NORMAL}\n"
      export CHOICE
      python3 -c "import os; from resources.botscores_botometer import *;\
                  likers_botlite(os.getenv('CHOICE')); retweeters_botlite(os.getenv('CHOICE'))"
      printf "${MAGENTA_BLINK}\n  DONE!${NORMAL}\n\n"
    else
      printf "${RED}\n        Sorry, I can't find that directory.${NORMAL}\n"; exit;
    fi;;
  * ) printf "${RED}\n        Invalid choice, I'm afraid. Quitting...${NORMAL}\n"; exit;
esac
