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
        So, you want to look up some user accounts, huh?${RED}

        The newest data directory I see is
        $NEWEST

        ${RED}Is that the directory of your data? (y/n)${NORMAL}\n
        >>> "
read ynchoice

case "$ynchoice" in
  y|Y ) printf "${GREEN}
        Great, I look up the users from $NEWEST
        This may take a bit!${NORMAL}\n"
        export NEWEST
        python3 -c "import os; from resources.fv22 import *;\
                    laterusers(os.getenv('NEWEST'))"
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
        and will look up the uuuuuuuuuuuuuuuuuusers!
        This may take a bit!${NORMAL}\n"
      export CHOICE
      python3 -c "import os; from resources.fv22 import *;\
                  laterusers(os.getenv('CHOICE'))"
      printf "${MAGENTA_BLINK}\n  DONE!${NORMAL}\n\n"
    else
      printf "${RED}\n        Sorry, I can't find that directory.${NORMAL}\n"; exit;
    fi;;
  * ) printf "${RED}\n        Invalid choice, I'm afraid. Quitting...${NORMAL}\n"; exit;
esac
