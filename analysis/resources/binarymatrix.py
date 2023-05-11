import os
import glob
import pandas as pd
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
from ast import literal_eval

# Functions in this file are inspired by
# https://stackoverflow.com/a/74825859/1654116

#########
#  LIKERS
#    mirrrored below for retweeters
############

def aggegate_likers(pulldir):
    # set a counter
    counter = 0

    # list all likers files
    list_of_csv_files = glob.glob(os.path.join(pulldir,'CSVs/Likers_of_alarms/*ikers*.csv'))
    print("Making list_of_dfs from CSV files...")
    list_of_dfs = [pd.read_csv(file, usecols = ['Unnamed: 0','likers'], converters={"likers": literal_eval}) for file in list_of_csv_files]
    print("Concatenating list_of_dfs...")
    likers_incomplete = pd.concat(list_of_dfs)
    print("Exploding list_of_dfs...")
    likers_incomplete = likers_incomplete.explode('likers').drop_duplicates(ignore_index=True)
    print("Set index...")
    likers_incomplete.set_index('Unnamed: 0', inplace=True)
    likers_incomplete.index.name = 'tweetID'
    print("Get dummies...")
    likers_incomplete = pd.get_dummies(likers_incomplete, prefix='', prefix_sep='')
    print("Group...")
    likers_incomplete = likers_incomplete.groupby('tweetID').sum()

    print("Final harvest...")
    if os.path.isfile(os.path.join(pulldir,'likers_final_harvest_complete.pkl')):
        finalharvest_l = pd.read_pickle(os.path.join(pulldir,'likers_final_harvest_complete.pkl'))

        # add final harvest to dataframe
        for tweet in finalharvest_l.index:
            for user in finalharvest_l.at[tweet,'likers']:
                        likers_incomplete.at[tweet, user] = 1
        likers_incomplete = likers_incomplete.fillna(0)

    print("Reindex and sort...")
    likers_complete = likers_incomplete
    likers_complete.index.names = ['tweet']
    likers_complete = likers_complete.sort_index(axis=0)
    likers_complete = likers_complete.sort_index(axis=1)

    # likers_complete contain the complete data set of tweet ids, user ids, and
    # who liked what. Export that:
    savepath1 = os.path.join(pulldir,'binary-matrix-likers.pkl')
    print("Saving likers binary matrix to: " + savepath1)
    likers_complete.to_pickle(savepath1)

############
# RETWEETERS
############

def aggegate_retweeters(pulldir):
    # set a counter
    counter = 0

    # list all retweeters files
    list_of_csv_files = glob.glob(os.path.join(pulldir,'CSVs/Retweeters_of_alarms/*etweeters*.csv'))
    print("Making list_of_dfs from CSV files...")
    list_of_dfs = [pd.read_csv(file, usecols = ['Unnamed: 0','retweeters'], converters={"retweeters": literal_eval}) for file in list_of_csv_files]
    print("Concatenating list_of_dfs...")
    retweeters_incomplete = pd.concat(list_of_dfs)
    print("Exploding list_of_dfs...")
    retweeters_incomplete = retweeters_incomplete.explode('retweeters').drop_duplicates(ignore_index=True)
    print("Set index...")
    retweeters_incomplete.set_index('Unnamed: 0', inplace=True)
    retweeters_incomplete.index.name = 'tweetID'
    print("Get dummies...")
    retweeters_incomplete = pd.get_dummies(retweeters_incomplete, prefix='', prefix_sep='')
    print("Group...")
    retweeters_incomplete = retweeters_incomplete.groupby('tweetID').sum()

    print("Final harvest...")
    if os.path.isfile(os.path.join(pulldir,'retweeters_final_harvest_complete.pkl')):
        finalharvest_r = pd.read_pickle(os.path.join(pulldir,'retweeters_final_harvest_complete.pkl'))

        # add final harvest to dataframe
        for tweet in finalharvest_r.index:
            for user in finalharvest_r.at[tweet,'retweeters']:
                        retweeters_incomplete.at[tweet, user] = 1
        retweeters_incomplete = retweeters_incomplete.fillna(0)

    print("Reindex and sort...")
    retweeters_complete = retweeters_incomplete
    retweeters_complete.index.names = ['tweet']
    retweeters_complete = retweeters_complete.sort_index(axis=0)
    retweeters_complete = retweeters_complete.sort_index(axis=1)

    # retweeters_complete contain the complete data set of tweet ids, user ids, and
    # who liked what. Export that:
    savepath2 = os.path.join(pulldir,'binary-matrix-retweeters.pkl')
    print("Saving retweeters binary matrix to: " + savepath2)
    retweeters_complete.to_pickle(savepath2)
