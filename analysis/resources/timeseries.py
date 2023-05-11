import os
import glob
import pandas as pd
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


# This takes forever, faster below.
def timeseries(pulldir):
    # list all timestep files
    csvs = glob.glob(os.path.join(pulldir,'CSVs/*.csv'))
    print('Number of files:', len(csvs))
    # sort the list, so sort by file name, i.e. timestamp, earliest first.
    csvs.sort()

    likes_incomplete = pd.DataFrame()
    retweets_incomplete = pd.DataFrame()

    # use time counter to name columns instead of long file names
    time = 0
    for file in csvs: # for each timestep csv,
        df = pd.read_csv(file) # read it as a dataframe
        df.set_index('id', inplace=True) # set tweet id as index for easy access
        for tweet in df.index: # for each idnex = tweet
            likes_incomplete.at[tweet,time] = df.at[tweet,'like_count'] # record the like_count under the right time
            retweets_incomplete.at[tweet,time] = df.at[tweet,'retweet_count'] # record the retweet_count under the right time
        time = time+1 # "move to next column"
        print('Done with file ',time,' of ',len(csvs))

    # When through all the csvs, save:

    likes_over_time = likes_incomplete
    retweets_over_time = retweets_incomplete

    savepath1 = os.path.join(pulldir,'timeseries_likes.pkl')
    print("        Saving likes timeseries to: " + savepath1)
    likes_over_time.to_pickle(savepath1)

    savepath2 = os.path.join(pulldir,'timeseries_retweets.pkl')
    print("        Saving retweets timeseries to: " + savepath2)
    retweets_over_time.to_pickle(savepath2)

# Infinitely faster:
#https://stackoverflow.com/questions/20906474/import-multiple-csv-files-into-pandas-and-concatenate-into-one-dataframe
def timeseries3(pulldir):
    # list all timestep files
    csvs = glob.glob(os.path.join(pulldir,'CSVs/*.csv'))
    print('Number of files:', len(csvs))
    # sort the list, so sort by file name, i.e. timestamp, earliest first.
    csvs.sort()

    # initiate lists of dataframes for like and retweet timelines
    likes_list = []
    retweets_list = []
    counter = 0

    # populate the dataframe lists:
    for filename in csvs:
        counter = counter + 1
        # read each csv only once, with tweet id as index:
        df = pd.read_csv(filename, index_col='id')[['like_count','retweet_count']]
        # add the likes part to the likes_list, renaming the 'like_count' column
        # to the timestamp part of the csv name:
        likes_list.append(df[['like_count']].rename(columns={"like_count": filename[len(pulldir)+5:-9]}))
        # ditto for retweets:
        retweets_list.append(df[['retweet_count']].rename(columns={"retweet_count": filename[len(pulldir)+5:-9]}))
        print('Through file', counter, 'of', len(csvs))

    # concatenate:
    print('Concatenating...')
    likes_timeseries = pd.concat(likes_list, axis=1, ignore_index=False)
    retweets_timeseries = pd.concat(retweets_list, axis=1, ignore_index=False)

    print('Saving...')
    savepath1 = os.path.join(pulldir,'timeseries3_likes.pkl')
    print("        Saving likes timeseries to: " + savepath1)
    likes_timeseries.to_pickle(savepath1)

    savepath2 = os.path.join(pulldir,'timeseries3_retweets.pkl')
    print("        Saving retweets timeseries to: " + savepath2)
    retweets_timeseries.to_pickle(savepath2)
