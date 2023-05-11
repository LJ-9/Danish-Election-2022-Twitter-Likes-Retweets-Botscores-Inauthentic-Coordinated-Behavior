import os
import tweepy
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bearertoken import *

# bearer_token = '<your bearer token here or in bearertoken.py>'
client = tweepy.Client(bearer_token, wait_on_rate_limit = True)


#################
# HANDY FUNCTIONS
#################

# Divides a list into a lists of sublists of length n:
def sublists(list, n):
    for i in range(0, len(list), n):
        yield list[i:i + n]

# Flatten list from [[1,2,3],[4,5,6]] to [1,2,3,4,5,6] (users in bins)
def flatten(l):
    return [item for sublist in l for item in sublist]

# Checks if all values in a coumn are equal to the first:
def unique_value_in_column(df_column):
    a = df_column.to_numpy()
    return (a[0] == a).all()


#################
# BINS OPERATIONS
#################

# Create dataframe with bins and the lists of tweets each bin has liked.
# Bonus: includes size of bin.
def bins_to_tweets(bins_list, binarymatrix):
    bins_list = sorted(bins_list, key=len, reverse = True)
    bins_df = pd.DataFrame()
    bins_df['bins'] = bins_list
    bins_df['bin size'] = [len(bins_list[bin]) for bin in range(len(bins_list))]
    bins_df['tweetsliked'] = [list(binarymatrix.loc[binarymatrix[bins_list[bin][0]] == 1].index.values) for bin in range(len(bins_list))]
    bins_df['number of tweets liked'] = [len(bins_df['tweetsliked'][bin]) for bin in range(len(bins_list))]
    return bins_df



############
# TWEETS
############

# For the post-live scrape of like counts, etc.:
def latercounts(pulldir):
    print('Loading binary matrices etc. from', pulldir)
    bm_likes = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-likers.pkl'))
    bm_retweets = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-retweeters.pkl'))
    tweets_list = tweetslist(bm_likes, bm_retweets)  # tweets_list contains list of tweets IDs from both binary matrices of likers and retweeters

    #####
    # THIS SCRAPES DATA
    # Look up the tweets in tweets_list, storing raw response
    #####

    print('Starting lookup...')
    tweets_data = lookup_tweets(tweets_list, client)
    # The response is a named tuple.
    # Each key in dict has the response for max 100 tweet lookups, as before the list did)
    # Speed diff probably negelgible, given rate limits with more data

    #print('Save raw response...') # This doesn't work, can't load again.
    #tweets_data_df = pd.DataFrame(tweets_data)
    #tweets_data_df.to_pickle(os.path.join(pulldir, 'latercounts-raw.pkl'))

    print('Create dataframe...')
    # store everything of response object in dataframe in a structured way
    tweets_df = process_lookup_tweets(tweets_data)

    print('Save dataframe...')
    tweets_df.to_pickle(os.path.join(pulldir, 'latercounts.pkl'))
    print('Done.')

# Look up a list of tweet IDs, 100 at a time,
# return a list of dictionaries with the content:
#
# Examples:
# foo = lookup_tweets([...])
# foo[0].data is data of dictionary of first 100 tweets
# original tweet: 1602266759670759424
# retweet: 1602642947543113728
# bar = lookup_tweets([1602266759670759424, 1602642947543113728])
# bar[0].data[0] # data of first tweet
# bar[0].data[1]['referenced_tweets'][0]['type'] # second tweet is retweet

# see tweepy documentation for info on get_tweets
    # https://docs.tweepy.org/en/stable/client.html
# see Twitter API2 docs for info on endpoint options:
    #https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets-id

def lookup_tweets(tweet_IDs, client):
    Sublists = sublists(tweet_IDs, 100)
#    print('Number of sublists:', len(Sublists))
    counter = 0
    list_of_full_tweet_dicts = {} # initiate dict
    for idx, sublist in enumerate(Sublists):
        counter = counter + 1
#        print('Sublist', counter, 'of', len(Sublists))
        print('Sublist', counter, 'of circa', len(tweet_IDs) / 100)
        list_of_full_tweet_dicts[idx] = client.get_tweets(sublist, tweet_fields=['id','public_metrics','referenced_tweets'])
        # per 100 tweet IDs, we store the response in a dict. The response is of form named tuple.
        # dict: list_of_full_tweet_dicts.keys() works and returns 1,2,3,...length up to as many sublists as we have
        # named tupled: list_of_full_tweet_dicts[0]._fields works and returns the fields in the named tuple, length up to 100
    return list_of_full_tweet_dicts

        # tweets_data = lookup_tweets_2(tweets_list, client) # reworked this function
        # this returns now a dict of response object, not a list of tweets, a dict that is futher more a namedtuple,
        # that has its own syntax to access the data, see: https://docs.tweepy.org/en/stable/response.html#tweepy.Response

        # tweets_data[0] means tweets in first sublist, tweets_data[1] means tweets in second sublist
        # tweets_data[0]._fields # see what 'fields' (like keys) are in the response object for the first 100 tweets
        # tweets_data[0].data[1].id # how to access tweet id
        # tweets_data[0].data[1].public_metrics # how to access metrics
        # tweets_data[0].data[0].referenced_tweets[0]['type']# how to access referenced tweet, only works if there is one
        # tweets_data[2].errors # access if any tweets were not found, returns a list of errors, if empty, then all tweets were found


# stores EVERYTHING of response of lookup_tweets in a dataframe
# so that we can slice and dice the data accordingly for different analyses
def process_lookup_tweets(tweets_data):
    df_dict = {}
    for sub in list(range(0,len(tweets_data),1)):
        # for each sublist, init dataframe to store results in (to prevent overwriting)
        tweets_data_df = pd.DataFrame(columns=['id','like_count','retweet_count','reply_count','quote_count','referenced_tweet','referenced_tweet:_type', 'error'])
        for idx,tweet in enumerate(tweets_data[sub].data): # for each sublist, store data in dataframe
            tweets_data_df.loc[idx,'id'] = tweet.id
            tweets_data_df.loc[idx, 'like_count'] = tweet.public_metrics['like_count']
            tweets_data_df.loc[idx, 'retweet_count'] = tweet.public_metrics['retweet_count']
            tweets_data_df.loc[idx, 'reply_count'] = tweet.public_metrics['reply_count']
            tweets_data_df.loc[idx, 'quote_count'] = tweet.public_metrics['quote_count']
            try:
                tweets_data_df.loc[idx, 'referenced_tweet'] = tweet.referenced_tweets[0]['id']
                tweets_data_df.loc[idx, 'referenced_tweet:_type'] = tweet.referenced_tweets[0]['type'] # can be 'replied to' or 'quoted'. Is 'replied to' a retweet without text?
            except TypeError: # if there is no referenced tweet, then the referenced_tweets list is empty, and we get a TypeError
                pass # Nan filled into list
        try:
            for i in list(range(0,len(tweets_data[sub].errors),1)):
                tweets_data_df.loc[tweets_data_df.shape[0], 'id'] = tweets_data[sub].errors[i]['value'] #add tweet ID of errorred tweet to bottom of df after df done
                tweets_data_df.loc[tweets_data_df.shape[0]-1, 'error'] = tweets_data[sub].errors[i]['detail'] #add error message
        except: # if there is no errors
            pass # don't do anything

        df_dict[sub] = tweets_data_df # store each dataframe in the early on initiated dictionary, with the key being the sublist number
    tweets_df = pd.concat(df_dict.values(), ignore_index=True)
    tweets_df = tweets_df.set_index(['id'])

    return tweets_df



 # More dictionary examples:
 # list_of_tweet_dicts = lookup_tweets([...])
 # len(list_of_tweet_dicts) # these are dictionaries, with max 100 tweets in each
 # len(list_of_tweet_dicts[0]) # first dictionary: [0]: succesfully gotten, [1]: ?, [2]: errors, [3]: ?
 # len(list_of_tweet_dicts[0][0]) # first dictionary tweets
 # list_of_tweet_dicts[0].data    # first dictionary tweets
     # saved under each is 'id', 'public_metrics' and 'referenced_tweets', cf. def. of lookup_tweets.
     #list_of_tweet_dicts[0][0][0]['public_metrics']
     #list_of_tweet_dicts[0].data[0].public_metrics
     #list_of_tweet_dicts[0][0][1]['public_metrics']


# Take a list of tweet dictionaries and parse info about their tweet_type
# into a dataframe:
def tweet_type(list_of_full_tweet_dicts):
    parsed_tweets = pd.DataFrame()
    for dict in range(len(list_of_full_tweet_dicts)):
        for tweet in list_of_full_tweet_dicts[dict].data:
            if 'referenced_tweets' in tweet:
                parsed_tweets.at[tweet.id,'type'] = tweet.referenced_tweets[0].type
            else:
                parsed_tweets.at[tweet.id,'type'] = 'original'
    return parsed_tweets


# This extends tweet_type, and can be extended to cover more, like tweet text:
# Take a list of tweet dictionaries and parse info about their type, like_count and retweet_count
# into a dataframe:
def parse_tweet(list_of_full_tweet_dicts):
    parsed_tweets = pd.DataFrame()
    for dict in range(len(list_of_full_tweet_dicts)):
        for tweet in list_of_full_tweet_dicts[dict].data:
            parsed_tweets.at[tweet.id,'like_count'] = tweet.public_metrics['like_count']
            parsed_tweets.at[tweet.id,'retweet_count'] = tweet.public_metrics['retweet_count']
            if 'referenced_tweets' in tweet:
                parsed_tweets.at[tweet.id,'type'] = tweet.referenced_tweets[0].type
            else:
                parsed_tweets.at[tweet.id,'type'] = 'original'
    parsed_tweets['like_count'] = parsed_tweets['like_count'].astype('Int64')
    parsed_tweets['retweet_count'] = parsed_tweets['retweet_count'].astype('Int64')
    return parsed_tweets


# parses new tweetsdata and max data into dataframe,
# calculating diff between old maxlikes/maxretweets counts and newly observed.
def counts_diff(tweets_df, maxlikes, maxretweets):
    # subset tweets_df with relevant columns 'like_count', 'retweet_count':
    counts =  tweets_df[['like_count','retweet_count']]
    # add 'max_likes' and 'max_retweets' to counts dataframe:
    for tweet in counts.index:
        if tweet in maxlikes:
            counts.at[tweet, 'max_likes'] = maxlikes[tweet]
        if tweet in maxretweets:
            counts.at[tweet, 'max_retweets'] = maxretweets[tweet]
    try:
        #counts['max_likes'] = counts['max_likes'].astype('Int64')
        #counts['max_retweets'] = counts['max_retweets'].astype('Int64')
        counts['likes_diff'] = counts['max_likes'] - counts['like_count']
        counts['retweets_diff'] = counts['max_retweets'] - counts['retweet_count']
    except:
        pass
    return counts

def plot_counts(counts, var, topn):
    column = f'{var}_diff'
    yval = counts.sort_values(by=[column], ascending = False)
    plt.plot(list(range(0,topn,1)),yval[column][0:topn])
    plt.xlabel(f'top {topn} tweets with greatest drop in {var}')
    plt.ylabel(f'absolute drop in {var}')
    plt.show()



########################
# USER LOOKUPS post livescrape
# Requires that binarymatrix.sh, binning.sh and timeseries.sh have been run on pulldir
########################

def laterusers(pulldir):
    print('Loading binary matrices etc. from', pulldir)
    bm_likes = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-likers.pkl'))
    bm_retweets = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-retweeters.pkl'))
    users_list = userlist(bm_likes, bm_retweets)

    #####
    # THIS SCRAPES DATA
    # Look up the users in users_list, storing raw response
    #####

    print('Starting lookup...')
    users_data = lookup_users_2(users_list, client)

    #print('Save raw response...') # This doesn't work, can't load again.
    #users_data_df = pd.DataFrame(users_data)
    #users_data_df.to_pickle(os.path.join(pulldir, 'laterusers-raw.pkl'))

    print('Create dataframe...')
    # store everything of response object in dataframe in a structured way
    parsed_users = parse_users(users_list, users_data)

    print('Save dataframe...')
    parsed_users.to_pickle(os.path.join(pulldir, 'laterusers.pkl'))
    print('Done.')

# userlist takes union of users from the two binary matrices, and removes any
# 'AwarenessRequired_Likers_of_Deleted_Tweet' and
# 'AwarenessRequired_Retweeters_of_Deleted_Tweet',
# which we added to keep track while scraping and now causes regex errors with the API.
def userlist(binarymatrixlikers,binarymatrixretweers):
    users_list = list(set(list(binarymatrixlikers.columns) + list(binarymatrixretweers.columns)))
    if 'AwarenessRequired_Retweeters_of_Deleted_Tweet' in users_list:
        users_list.remove('AwarenessRequired_Retweeters_of_Deleted_Tweet')
    if 'AwarenessRequired_Liking_Users_of_Deleted_Tweet' in users_list:
        users_list.remove('AwarenessRequired_Liking_Users_of_Deleted_Tweet')
    return users_list


# GET data about users from list_of_usernames
# same logic as lookup_tweets
def lookup_users(list_of_usernames, client):
    Sublists = sublists(list_of_usernames, 100)
#    print('Number of sublists:', len(Sublists))
    list_of_userdata_dicts = []
    counter = 0
    for sublist in Sublists:
        counter = counter + 1
#        print('Sublist', counter, 'of', len(Sublists))
        print('Sublist', counter, 'of circa', len(list_of_usernames) / 100)
        list_of_userdata_dicts.append(
            client.get_users(usernames = sublist, user_fields = ['created_at','protected','verified','public_metrics'])
        )
    return list_of_userdata_dicts

def lookup_users_2(list_of_usernames, client):
    Sublists = sublists(list_of_usernames, 100)
    list_of_userdata_dicts = {} # initiate dict
    counter = 0
    for idx, sublist in enumerate(Sublists):
        counter = counter + 1
        print('Sublist', counter, 'of circa', len(list_of_usernames) / 100)
        list_of_userdata_dicts[idx] =client.get_users(usernames = sublist, user_fields = ['created_at','protected','verified','public_metrics'])
        # per 100 tweet IDs, we store the response in a dict. The response is of form named tuple.
        # dict: list_of_full_tweet_dicts.keys() works and returns 1,2,3,...length up to as many sublists as we have
        # named tupled: list_of_full_tweet_dicts[0]._fields works and returns the fields in the named tuple, length up to 100
    return list_of_userdata_dicts


# Parse userdata about list_of_usernames.
# Both are included as arguments because userdata may be incomplete, and we don't want to forget anyone.
def parse_users(list_of_usernames, userdata):
    parsed_users = pd.DataFrame(data = list_of_usernames) # take list as basic
    parsed_users.set_index(0, inplace=True) # assign usernames to index
    parsed_users.index.name = 'username'
    parsed_users['id'] = 'empty'
    parsed_users['error_title'] = 'none'
    parsed_users['error_detail'] = 'none'
    for dict in range(len(userdata)):
        for userindex in userdata[dict].data:
            if 'id' in userindex:
                parsed_users.at[userindex.username,'id'] = userindex.id
            if 'name' in userindex:
                parsed_users.at[userindex.username,'name'] = userindex.name
            if 'created_at' in userindex:
                parsed_users.at[userindex.username,'created_at'] = userindex.created_at
            if 'protected' in userindex:
                parsed_users.at[userindex.username,'protected'] = userindex.protected
            if 'verified' in userindex:
                parsed_users.at[userindex.username,'verified'] = userindex.verified
            if 'public_metrics' in userindex:
                parsed_users.at[userindex.username,'followers_count'] = userindex.public_metrics['followers_count']
                parsed_users.at[userindex.username,'following_count'] = userindex.public_metrics['following_count']
                parsed_users.at[userindex.username,'tweet_count'] = userindex.public_metrics['tweet_count']
                parsed_users.at[userindex.username,'listed_count'] = userindex.public_metrics['listed_count']
        for userindex in userdata[dict].errors:
            if 'title' in userindex:
                parsed_users.at[userindex['value'],'error_title'] = userindex['title']
            if 'detail' in userindex:
                parsed_users.at[userindex['value'],'error_detail'] = userindex['detail']
    return parsed_users



################
# USER EXISTS
################

def tweetslist(binarymatrixlikers,binarymatrixretweers):
    tweets_list = list(set(list(binarymatrixlikers.index.values) + list(binarymatrixretweers.index.values)))
    return tweets_list





################
# BOTOMETER
################

# BotometerLite: check users in bulk


def botlite(accounts, blt_twitter):
    # split accounts into sublists of 100
    #Sublists = sublists(accounts, 100)
    Sublists = [accounts[x:x+100] for x in range(0, len(accounts), 100)]

    blt_scores = [[] for _ in range(len(Sublists))] # triggers error

    #for idx, sublist in enumerate(Sublists):
    for i in list(range(len(Sublists))): #triggers error
        try:
            screen_name_list = Sublists[i]

            blt_scores[i] = blt_twitter.check_accounts_from_screen_names(screen_name_list)

        except Exception as ex:
            print(ex)
            # logger.info(print(ex)) # find out how to only print reduced messages like in print(ex) to log file
            pass
    return blt_scores

def process_blt_scores(blt_scores):
    list_of_dicts = flatten(blt_scores)
    scoresplot = pd.DataFrame.from_records(list_of_dicts)
    scoresplot.rename(columns = {'botscore':'scores', 'tweet_id':'tweetid', 'user_id':'userid'}, inplace = True)
    return scoresplot

# Creating histogram
def blt_hist(scoresplot):
    fig, ax = plt.subplots(figsize =(10, 7))

    ax.hist(scoresplot['scores'], bins = np.linspace(0,1,50), alpha=.7, weights=np.ones(len(scoresplot))/len(scoresplot)) #density = True)#[0, .05, .1, .15,.2, .25,.3, .35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.85, .9,.95,1])
    # later: implement hist of unsuspicious users and compare
    #ax.hist(scoresplotunsus['scores'], bins = np.linspace(0,1,50), alpha=.7, weights=np.ones(len(scoresplotunsus))/len(scoresplotunsus))# density = True)#[0, .05, .1, .15,.2, .25,.3, .35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.85, .9,.95,1])


    ax.set_ylabel('Frequency')
    ax.set_xlabel('Botscores')

    # Show plot
    plt.show()



# normal botometer, not able to check in bulk
def botometer_v4(accounts, bom):
    scores = pd.DataFrame(columns=[
                                'user-id',
                                'screenname_from_list',
                                'screenname',
                                'maj_lang',

                               'result_cap_e',
                               'result_cap_uni',

                               'astroturf_e',
                               'fake_follower_e',
                               'financial_e',
                               'other_e',
                               'overall_e',
                               'self_declared_e',
                               'spammer_e',

                               'astroturf_uni',
                               'fake_follower_uni',
                               'financial_uni',
                               'other_uni',
                               'overall_uni',
                               'self_declared_uni',
                               'spammer_uni',

                               'raw_astroturf_e',
                               'raw_fake_follower_e',
                               'raw_financial_e',
                               'raw_other_e',
                               'raw_overall_e',
                               'raw_self_declared_e',
                               'raw_spammer_e',

                               'raw_astroturf_uni',
                               'raw_fake_follower_uni',
                               'raw_financial_uni',
                               'raw_other_uni',
                               'raw_overall_uni',
                               'raw_self_declared_uni',
                               'raw_spammer_uni'])

    for screen_name in accounts:
        try:
                result = bom.check_account(screen_name)
                scores=scores.append(
                    {
                        'user-id': result['user']['user_data']['id_str'],
                        'screenname_from_list': screen_name,
                        'screenname': result['user']['user_data']['screen_name'],
                        'maj_lang': result['user']['majority_lang'],


                        'result_cap_e': result['cap']['english'],
                        'result_cap_uni': result['cap']['universal'],

                         # english
                        'astroturf_e': result['display_scores']['english']['astroturf'],
                        'fake_follower_e': result['display_scores']['english']['fake_follower'],
                        'financial_e': result['display_scores']['english']['financial'],
                        'other_e': result['display_scores']['english']['other'],
                        'overall_e': result['display_scores']['english']['overall'],
                        'self_declared_e': result['display_scores']['english']['self_declared'],
                        'spammer_e': result['display_scores']['english']['spammer'],

                         # universal
                        'astroturf_uni': result['display_scores']['universal']['astroturf'],
                        'fake_follower_uni': result['display_scores']['universal']['fake_follower'],
                        'financial_uni': result['display_scores']['universal']['financial'],
                        'other_uni': result['display_scores']['universal']['other'],
                        'overall_uni': result['display_scores']['universal']['overall'],
                        'self_declared_uni': result['display_scores']['universal']['self_declared'],
                        'spammer_uni': result['display_scores']['universal']['spammer'],

                              # english
                        'raw_astroturf_e': result['raw_scores']['english']['astroturf'],
                        'raw_fake_follower_e': result['raw_scores']['english']['fake_follower'],
                        'raw_financial_e': result['raw_scores']['english']['financial'],
                        'raw_other_e': result['raw_scores']['english']['other'],
                        'raw_overall_e': result['raw_scores']['english']['overall'],
                        'raw_self_declared_e': result['raw_scores']['english']['self_declared'],
                        'raw_spammer_e': result['raw_scores']['english']['spammer'],

                         # universal
                        'raw_astroturf_uni': result['raw_scores']['universal']['astroturf'],
                        'raw_fake_follower_uni': result['raw_scores']['universal']['fake_follower'],
                        'raw_financial_uni': result['raw_scores']['universal']['financial'],
                        'raw_other_uni': result['raw_scores']['universal']['other'],
                        'raw_overall_uni': result['raw_scores']['universal']['overall'],
                        'raw_self_declared_uni': result['raw_scores']['universal']['self_declared'],
                        'raw_spammer_uni': result['raw_scores']['universal']['spammer'],


                    }, ignore_index=True )



        except Exception as ex:
            print(ex)
            # logger.info(print(ex)) # find out how to only print reduced messages like in print(ex) to log file
            pass
    return scores
