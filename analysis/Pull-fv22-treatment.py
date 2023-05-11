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

########################
# DATA LOAD
#
# Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
# Requires that latercounts.py and laterusers.py have been run
#
########################


pulldir = '../Pull-All_fv22/'
#pulldir = '../Pull-mini/'

bm_likes = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-likers.pkl'))
bm_retweets = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-retweeters.pkl'))
latercounts_df = pd.read_pickle(os.path.join(pulldir, 'latercounts.pkl'))
laterusers_df = pd.read_pickle(os.path.join(pulldir, 'laterusers.pkl'))

with open(os.path.join(pulldir, 'bins_likers.pkl'), 'rb') as f:
    bins_likers = pickle.load(f)

with open(os.path.join(pulldir, 'bins_retweeters.pkl'), 'rb') as f:
    bins_retweeters = pickle.load(f)


# Build a "time series" dataframe from all the observation time points, so we can check e.g. the maximum number of likes that a tweet got. 
# 
# TODO:
# Timeseries with final harvest: Include in timeseries3.
# Current code gets PerformanceWarning
try:
    timeseries_with_finalharvest_likes = pd.read_pickle(os.path.join(pulldir, 'timeseries3_with_finalharvest_likes.pkl'))
except:
    timeseries_with_finalharvest_likes = pd.read_pickle(os.path.join(pulldir, 'timeseries3_likes.pkl'))
    finalharvest_likes = pd.read_pickle(os.path.join(pulldir, 'likers_final_harvest_complete.pkl'))
    for tweet in finalharvest_likes.index:
        timeseries_with_finalharvest_likes.at[tweet, 'final'] = finalharvest_likes.at[tweet, 'like_count']
    timeseries_with_finalharvest_likes.to_pickle(os.path.join(pulldir, 'timeseries3_with_finalharvest_likes.pkl'))

try:
    timeseries_with_finalharvest_retweets = pd.read_pickle(os.path.join(pulldir, 'timeseries3_with_finalharvest_retweets.pkl'))
except:
    timeseries_with_finalharvest_retweets = pd.read_pickle(os.path.join(pulldir, 'timeseries3_retweets.pkl'))
    finalharvest_retweets = pd.read_pickle(os.path.join(pulldir, 'retweeters_final_harvest_complete.pkl'))
    for tweet in finalharvest_retweets.index:
        timeseries_with_finalharvest_retweets.at[tweet, 'final'] = finalharvest_retweets.at[tweet, 'retweet_count']
    timeseries_with_finalharvest_retweets.to_pickle(os.path.join(pulldir, 'timeseries3_with_finalharvest_retweets.pkl'))

# Observed max like_count and retweet_count
# Add the final harvest like/retweet count to the timeseries dataframes
# to find the maximum number of likes/retweets across all observations:
try:
    max_likes = pd.read_pickle(os.path.join(pulldir, 'max_likes.pkl'))
except:
    max_likes = timeseries_with_finalharvest_likes.max(axis=1)
    max_likes.to_pickle(os.path.join(pulldir, 'max_likes.pkl'))

try:
    max_retweets = pd.read_pickle(os.path.join(pulldir, 'max_retweets.pkl'))
except:
    max_retweets = timeseries_with_finalharvest_retweets.max(axis=1)
    max_retweets.to_pickle(os.path.join(pulldir, 'max_retweets.pkl'))

users_list = userlist(bm_likes, bm_retweets)  # Contains list of users IDs from both binary matrices of likers and retweeters
tweets_list = tweetslist(bm_likes, bm_retweets)  # tweets_list contains list of tweets IDs from both binary matrices of likers and retweeters


#######################
# Bins
#######################

# The bins are here:
len(bins_likers)
len(bins_retweeters)

len(users_list)

# consider users in n largest bins to check deletions, botometer etc.:
n = 10
sus_bins = sorted(bins_likers, key=len, reverse=True)[0:n]  # suspicious n largest bins
sus_bins_together = flatten(sus_bins)  # for botometer check later
# sus_bins[0] # users in largest bin
len(sus_bins[0])  # size of largest bin

# consider users in bins of min size m to check deletions, botometer etc.:
m = 21 # 21 is largest where all bins like a unique tweet, see below.
sus_large_bins = [x for x in bins_likers if len(x) >= m]  # suspicious users in bins of size m or larger
sus_large_bins_together = flatten(sus_large_bins)  # for botometer check later
len(sus_large_bins)  # number of bins of size m or larger

# map bins to tweets: what tweets did a bin like?
bins_and_tweets = bins_to_tweets(sus_large_bins, bm_likes)

# did the bins like equally many tweets?
unique_value_in_column(bins_and_tweets['number of tweets liked'])
# m = 21 : True
# m = 20 = 13 : False -- 1 bin liked 2
# m = 12 : : False -- 2 bins liked 2
# m = 11 = 10 : False -- 3 bins liked 2, 1 bin liked 3
# bins_and_tweets.sort_values(by=['number of tweets liked'], ascending = False)


# How many likes did those tweets get, during live scrape and later checked?

# Check if bins each check a like single, and
# if they did, get the max like count of that tweet over the observation period:
if (bins_and_tweets['number of tweets liked'] == 1).all():
    bins_tweets_and_likes = bins_and_tweets
    for i in bins_tweets_and_likes.index:
        # Get max like count of unique tweet liked by bin:
        max = max_likes.loc[bins_tweets_and_likes.loc[i,'tweetsliked'][0]]
        # Get later like count of unique tweet liked by bin, if available:
        try:
            later = latercounts_df.loc[bins_tweets_and_likes.loc[i,'tweetsliked'][0], 'like_count']
        except:
            later = np.nan
        # Add them to DataFrame:
        bins_tweets_and_likes.loc[i,'max number of likes'] = max
        bins_tweets_and_likes.loc[i,'later number of likes'] = later
        # Add also difference:
        bins_tweets_and_likes.loc[i,'difference'] = max - later

bins_tweets_and_likes.sort_values(by=['difference'], ascending = False)[0:10]

bins_tweets_and_likes[0:10]['tweetsliked']

firefox https://twitter.com/anyuser/status/1579691428267331584
firefox https://twitter.com/anyuser/status/1584990096704802816
firefox https://twitter.com/anyuser/status/1580932642476036098
firefox https://twitter.com/anyuser/status/1586705278468325376
firefox https://twitter.com/anyuser/status/1585961696253747202
firefox https://twitter.com/anyuser/status/1587593616318414851
firefox https://twitter.com/anyuser/status/1584911909903556609
firefox https://twitter.com/anyuser/status/1587519445714583554
firefox https://twitter.com/anyuser/status/1587594137406406656
firefox https://twitter.com/anyuser/status/1587371339060596736


#######################
# Like/retweet count now vs. then
#######################

# 1. Look at the already scraped latercounts.pkl:

# take a look at the not found tweets
tweets_not_found = latercounts_df[~latercounts_df['error'].isnull()]
tweets_not_found.shape[0]
tweets_not_found[0:3]

# take a look the retweets
retweets = latercounts_df[~latercounts_df['referenced_tweet'].isnull()]
retweets[0:3]

# 2. Comparison of counts
# parse new tweetsdata and max data into dataframe,
# calculate diff between old maxlikes/maxretweets counts and newly observed:
    # TODO (nice): counts_diff warns "A value is trying to be set on a copy of a slice from a DataFrame. Try using .loc[row_indexer,col_indexer] = value instead"

counts = counts_diff(latercounts_df, max_likes, max_retweets)
counts[0:3]







# 4. Do stuff with counts :)

# look at tweets with high pos delta
counts_likes = counts.sort_values(by=['likes_diff'], ascending=False)  # not particularly high values, top delta drop of 45
counts_likes[0:3]

plot_counts(counts, var = 'retweets', topn = 100)  # var: likes or retweets, topn: number of top tweets with highest diff to plot
plot_counts(counts, var = 'likes', topn = 100)

# TODO: next step: compare whether the disappeared likers coincide with bins


#######################
# User existence
#######################

# 3. Parsed later user data.
laterusers[0:3]

# 4. Do stuff with laterusers :)

gone_users = laterusers[laterusers['error_title'] != 'none']
gone_users['error_title'].unique()  # wither user profile deleted or went private (that's what I assume "Forbidden" means)

deleted_users = laterusers[laterusers['error_title'] == 'Not Found Error']
deleted_users  # majority 183/204

private_users = laterusers[laterusers['error_title'] == 'Forbidden']
private_users  # minority 21/204

# relationship bins and deletions: Are deleted accounts among large bins of users?
# TODO: with all data: plot bins like in Web science conf paper (Fig. 2) and color the share of deletions per bar to visualize relationship


# 36% of deleted users are in bins of size m or larger
bins_deletions = sum(f in (deleted_users.index.values.tolist()) for f in sus_large_bins_together) / len((deleted_users.index.values.tolist()))
# 5% of deleted users are in n largest bins
# rename:
bins_deletions = sum(f in (deleted_users.index.values.tolist()) for f in sus_bins_together) / len((deleted_users.index.values.tolist()))





#######################
# Appendix: User exist test stuff
#######################

# user_list_foo = user_list_foo[0:150]
user_list_foo.sort()
user_list_foo = user_list_foo[0:190]
user_list_foo.append('CIBStestdummy1')
user_list_foo.insert(75, 'CIBStestdummy2')
user_list_foo.append('CIBStestdummy3')


# This is a list of dictionaries, each for 100 users:
user_data_foo1 = lookup_users(user_list_foo, client)
user_data_foo2 = lookup_users(user_list_foo, client)
user_data_foo3 = lookup_users(user_list_foo, client)
user_data_foo4 = lookup_users(user_list_foo, client)

# Look at first dictionary (first batch of 100 users), first user:
# user_data_foo[0].data[0].username
# user_data_foo[0].data[0].id
# user_data_foo[0].data[0].name
# user_data_foo[0].data[0].created_at
# user_data_foo[0].data[0].protected
# user_data_foo[0].data[0].verified
# user_data_foo[0].data[0].public_metrics
# user_data_foo[0].data[0].public_metrics['followers_count']

len(user_data_foo1[0].errors)
len(user_data_foo2[0].errors)
len(user_data_foo3[0].errors)
len(user_data_foo4[0].errors)
user_data_foo1 == user_data_foo2 == user_data_foo3 == user_data_foo4

laterusers = parse_users(user_list_foo, user_data_foo)
errors_foo = laterusers[laterusers['error_detail'].notnull()]
errors_foo
