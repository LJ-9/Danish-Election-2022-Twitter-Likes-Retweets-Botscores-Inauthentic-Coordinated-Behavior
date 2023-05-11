import os
import pickle
import pandas as pd
import numpy as np
# if import * does not work, try os.getcwd() to see where we are at
try: #wrapped in try so that you can run it without error trigger. If preferred, I can comment out too
    os.chdir('/Users/laurajahn/Documents/Git/fv22-wip/analysis')
except:
    pass
from resources.fv22 import *

# This file splits the userlist into four,
# so we can look up users with four bearertokens in parallel.

#pulldir = '../Pull-june/'
pulldir = '../Pull-All/'
#pulldir = '../Pull-mini/'

# Binary matrices load:
bm_likes = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-likers.pkl'))
bm_retweets = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-retweeters.pkl'))
# tweets_list contains list of tweets IDs from both binary matrices of likers and retweeters:
tweets_list = tweetslist(bm_likes, bm_retweets)

# Divide the list of tweets into number of bearer tokens
tmp_four_lists = np.array_split(np.array(tweets_list), len(bearer_token_list))
four_lists = []
for i in range(0,len(bearer_token_list)):
    four_lists.append(tmp_four_lists[i].tolist())

for i in range(0,len(four_lists)):
    filename = ''.join(('tweetIDlist',str(i)))
    path = os.path.join(pulldir, filename)
    with open(path, 'w') as f:
        for line in four_lists[i]:
            f.write("%s\n" % line)
