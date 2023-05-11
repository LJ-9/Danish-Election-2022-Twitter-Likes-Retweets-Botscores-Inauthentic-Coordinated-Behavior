# PRELIM: Create a virtual environment to run this script in and install older tweepy version in it. Doesn't affect latest tweepy version outside the envionment
# 1. download conda (to create virtual envionemnts) https://conda.io/projects/conda/en/latest/user-guide/install/index.html
# 2. in terminal, create a virtual env "conda create --name botometer python=3.10.8"
# 3. activate environment "conda activate botometer"
# 4. install tweepy version in it "pip install tweepy==3.10.0" (Didn't work for me: "conda install tweepy=3.10.0") and other relevant packages: pip install botometer
# 5. check which packages are installed in environment "conda list -n botometer" (when outside env, otherwise "conda list")
# 6. deactivate environment "conda deactivate" when changing to other scripts that rely on latest tweepy version. I have the latest tweepy installed in "base" environment

import os
import tweepy
import pickle
import pandas as pd
import numpy as np
import botometer
# if import * does not work, try the following:
# os.getcwd() fyi, to see where we are at
try: #wrapped in try so that you can run it without error trigger. If preferred, I can comment out too
    os.chdir('/Users/qbj218/Documents/Git/fv22-wip/analysis') #on M1 change qbj218 to laurajahn
except:
    pass
from resources.fv22 import *
# bearer_token = '<your bearer token here or in bearertoken.py>'
from bearertoken import *
from collections import namedtuple

########################
# BOTOMETER SETUP
# Set rapidapi_key in bearertoken.py
# set twitter_app_auth in bearertoken.py
########################

bom = botometer.Botometer(wait_on_ratelimit=True,rapidapi_key=rapidapi_key,**twitter_app_auth)
bomlite = botometer.BotometerLite(rapidapi_key=rapidapi_key, **twitter_app_auth)


########################
# DATA LOAD
# Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
########################

pulldir = '../Pull-mini/'

bm_likes = pd.read_pickle(os.path.join(pulldir,'binary-matrix-likers.pkl'))
bm_retweets = pd.read_pickle(os.path.join(pulldir,'binary-matrix-retweeters.pkl'))

with open(os.path.join(pulldir,'bins_likers.pkl'), 'rb') as f:
    bins_likers = pickle.load(f)

with open(os.path.join(pulldir,'bins_retweeters.pkl'), 'rb') as f:
    bins_retweeters = pickle.load(f)

timeseries_likes = pd.read_pickle(os.path.join(pulldir,'timeseries_likes.pkl'))
timeseries_retweets = pd.read_pickle(os.path.join(pulldir,'timeseries_retweets.pkl'))

users_list = userlist(bm_likes, bm_retweets) # since this contains a list of users, I'll rename it from tweets_list to user_list, contains list of users IDs from both binary matrices of likers and retweeters
tweets_list = tweetslist(bm_likes, bm_retweets) # tweets_list contains list of tweets IDs from both binary matrices of likers and retweeters




#######################
# Bins
#######################

# The bins are here:
#bins_likers
#bins_retweeters

# consider users in n largest bins to check deletions, botometer etc.:
n = 10
sus_bins_likers = sorted(bins_likers, key=len, reverse = True)[0:n] # suspicious n largest bins
sus_bins_likers_together = flatten(sus_bins_likers) # for botometer check later
#sus_bins[0] # users in largest bin
len(sus_bins_likers[0]) # size of largest bin

# consider users in bins of min size m to check deletions, botometer etc.:
m = 120
sus_large_bins_likers = [x for x in bins_likers if len(x) >= m] # suspicious users in bins of size m or larger
sus_large_bins_likers_together = flatten(sus_large_bins) # for botometer check later
len(sus_large_bins_likers) # number of bins of size m or larger


#######################
# Botometer
#######################

# Check a single account by screen name
result = bom.check_account('@laurajahnx')
# Check a single account by id
result = bom.check_account(1548959833)

# Flatten bins_likers and #bins_retweeters to one list as input for blt_scores
likers_botcheck = flatten(bins_likers)
retweeters_botcheck = flatten(bins_retweeters)
# Botometer lite: check users in bulk, tested, subscription to botometer lite (50USD/month): DONE
blt_scores = botlite(likers_botcheck[0:300], bomlite)
len(blt_scores) # should correspond to len(users)/100

# blt_scores[1][0] # {'botscore': 0.01, 'tweet_id': None, 'user_id': 2488744704}
scores_df = process_blt_scores(blt_scores) # parse results into dataframe
# scores_df.to_pickle("botscores_to pickle.pkl")

blt_hist(scores_df) # plot histogram of bot scores

# get normal botometer scores for suspicious users: not possible to check in bulk
scores = botometer_v4(likers_botcheck[0:1], bom)
# scores.to_pickle("botscores.pkl")

