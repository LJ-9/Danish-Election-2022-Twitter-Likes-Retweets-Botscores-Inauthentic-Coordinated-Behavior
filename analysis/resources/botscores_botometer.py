#### BOTOMETER LOOKUP ####

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


def botlite_lookup(users):
    #######################
    # Botometer Lite
    # To check users in bulk, tested, subscription to botometer lite (50USD/month)
    #######################
    bomlite = botometer.BotometerLite(rapidapi_key=rapidapi_key, **twitter_app_auth)
    
    blt_scores = botlite(users, bomlite)

    # blt_scores[1][0] # {'botscore': 0.01, 'tweet_id': None, 'user_id': 2488744704}
    scores_df_lite = process_blt_scores(blt_scores) # parse results into dataframe
    
    return scores_df_lite
   

def botv4_lookup(users):
    #######################
    # Botometer v4
    # extensive results, not sure about rate limits in ultra plan, slower
    #######################

    bom = botometer.Botometer(wait_on_ratelimit=True,rapidapi_key=rapidapi_key,**twitter_app_auth)

    # get normal botometer scores for suspicious users: not possible to check in bulk
    scores_df_v4 = botometer_v4(users, bom)

    return scores_df_v4


def likers_botlite(pulldir):
    ########################
    # DATA LOAD
    # Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
    ########################
    print('Loading likers from  bins from', pulldir)

    # bins
    with open(os.path.join(pulldir,'bins_likers.pkl'), 'rb') as f:
        bins_likers = pickle.load(f)

    # Flatten bins_likers and #bins_retweeters to one list as input for blt_scores
    botcheck_users = flatten(bins_likers)
    
    print('Starting to look up botscores for likers')

    scores = botlite_lookup(botcheck_users)
        
    print('Saving botscores for likers in dataframe...')

    scores.to_pickle(os.path.join(pulldir,'botscores_likers_lite.pkl'))
    print('Done with likers.')


def likers_botv4(pulldir):
    ########################
    # DATA LOAD
    # Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
    ########################
    print('Loading likers from  bins from', pulldir)

    # bins
    with open(os.path.join(pulldir,'bins_likers.pkl'), 'rb') as f:
        bins_likers = pickle.load(f)

    # Flatten bins_likers and #bins_retweeters to one list as input for blt_scores
    botcheck_users = flatten(bins_likers)
   
    print('Starting to look up botscores for likers')

    scores = botv4_lookup(botcheck_users)
        
    print('Saving botscores for likers in dataframe...')

    scores.to_pickle(os.path.join(pulldir,'botscores_likers_v4.pkl'))

    print('Done with likers.')

def retweeters_botlite(pulldir):
    ########################
    # DATA LOAD
    # Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
    ########################
    print('Loading retweeters from  bins from', pulldir)

    # bins
    with open(os.path.join(pulldir,'bins_retweeters.pkl'), 'rb') as f:
        bins_retweeters = pickle.load(f)
    
    print('Starting lookup of botscores for retweeters...')
    
    # Flatten bins_likers and #bins_retweeters to one list as input for blt_scores
    botcheck_users = flatten(bins_retweeters)
    scores = botlite_lookup(botcheck_users)
    
    print('Save dataframe for retweeters...')

    scores.to_pickle(os.path.join(pulldir,'botscores_retweeters_lite.pkl'))

    print('Done with retweeters.')

def retweeters_botlite_junedataset(pulldir):
    ########################
    # DATA LOAD
    # Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
    ########################
    print('Loading retweeters from  bins from', pulldir)

    # bins
    with open(os.path.join(pulldir,'june/bins_retweeters.pkl'), 'rb') as f:
        bins_retweeters = pickle.load(f)
    
    print('Starting lookup of botscores for retweeters...')
    
    # Flatten bins_likers and #bins_retweeters to one list as input for blt_scores
    botcheck_users = flatten(bins_retweeters)
    scores = botlite_lookup(botcheck_users)
    
    print('Save dataframe for retweeters...')

    scores.to_pickle(os.path.join(pulldir,'june/botscores_retweeters_lite.pkl'))

    print('Done with retweeters.')

def retweeters_botv4(pulldir):

    ########################
    # DATA LOAD
    # Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
    ########################
    print('Loading retweeters from  bins from', pulldir)

    # bins
    with open(os.path.join(pulldir,'bins_retweeters.pkl'), 'rb') as f:
        bins_retweeters = pickle.load(f)

    print('Starting lookup of botscores for retweeters...')

    # Flatten bins_likers and #bins_retweeters to one list as input for blt_scores
    botcheck_users = flatten(bins_retweeters)
    scores = botv4_lookup(botcheck_users)
    
    print('Save dataframe for retweeters...')

    scores.to_pickle(os.path.join(pulldir,'botscores_retweeters_v4.pkl'))

    print('Done with retweeters.')

def retweeters_botv4_junedataset(pulldir):

    ########################
    # DATA LOAD
    # Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
    ########################
    print('Loading retweeters from  bins from', pulldir)

    # bins
    with open(os.path.join(pulldir,'june/bins_retweeters.pkl'), 'rb') as f:
        bins_retweeters = pickle.load(f)

    print('Starting lookup of botscores for retweeters...')

    # Flatten bins_likers and #bins_retweeters to one list as input for blt_scores
    botcheck_users = flatten(bins_retweeters)
    scores = botv4_lookup(botcheck_users)
    
    print('Save dataframe for retweeters...')

    scores.to_pickle(os.path.join(pulldir,'june/botscores_retweeters_v4.pkl'))

    print('Done with retweeters.')


### To look up botscores for June dkpol dataset: bins come in slightly different format

def likers_botlite_junedataset(pulldir):
    ########################
    # DATA LOAD
    # Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
    ########################
    print('Loading likers from  bins from', pulldir)

    # bins
  
    with open(os.path.join(pulldir,'Cluster_overview.pkl'), 'rb') as f:
        bins_likers = pickle.load(f)
    # Flatten bins_likers and #bins_retweeters to one list as input for blt_scores

    members = bins_likers['clustermembers_username']
    botcheck_users = flatten(members)

    print('Starting to look up botscores for likers')

    scores = botlite_lookup(botcheck_users)
        
    print('Saving botscores for likers in dataframe...')

    scores.to_pickle(os.path.join(pulldir,'botscores_likers_lite.pkl'))
    print('Done with likers.')


def likers_botv4_junedataset(pulldir):
    ########################
    # DATA LOAD
    # Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
    ########################
    print('Loading likers from  bins from', pulldir)

    # bins
    with open(os.path.join(pulldir,'Cluster_overview.pkl'), 'rb') as f:
        bins_likers = pickle.load(f)

    # Flatten bins_likers and #bins_retweeters to one list as input for blt_scores
    members = bins_likers['clustermembers_username']
    botcheck_users = flatten(members)
   
    print('Starting to look up botscores for likers')

    scores = botv4_lookup(botcheck_users)
        
    print('Saving botscores for likers in dataframe...')

    scores.to_pickle(os.path.join(pulldir,'botscores_likers_v4.pkl'))

    print('Done with likers.')