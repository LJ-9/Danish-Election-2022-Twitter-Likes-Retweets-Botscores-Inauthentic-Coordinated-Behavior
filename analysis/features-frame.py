import os
import pickle
import pandas as pd
import numpy as np
# if import * does not work, try os.getcwd() to see where we are at
try: #wrapped in try so that you can run it without error trigger. If preferred, I can comment out too
    os.chdir('/Users/qbj218/Documents/Git/fv22-wip/analysis')
except:
    pass
from resources.fv22 import *


# pulldir = '../Pull-All_June/'
pulldir = '../Pull-All_fv22/'
#pulldir = '../Pull-mini/'

with open(os.path.join(pulldir, 'bins_likers.pkl'), 'rb') as f:
    bins_lk = pickle.load(f)

with open(os.path.join(pulldir, 'bins_retweeters.pkl'), 'rb') as f:
    bins_rt = pickle.load(f)

likers = pd.read_pickle(os.path.join(pulldir,'binary-matrix-likers.pkl'))
retweeters = pd.read_pickle(os.path.join(pulldir,'binary-matrix-retweeters.pkl'))

#June
#botv4_lk = pd.read_pickle(os.path.join(pulldir, 'Botscores/botscores_likers_v4_june.pkl'))
#botlite_lk = pd.read_pickle(os.path.join(pulldir, 'Botscores/botscores_likers_lite_june.pkl'))
#botv4_rt = pd.read_pickle(os.path.join(pulldir, 'Botscores/botscores_june_retweeters_v4.pkl'))
#botlite_rt = pd.read_pickle(os.path.join(pulldir, 'Botscores/botscores_retweeters_lite.pkl'))
# election
botv4_lk = pd.read_pickle(os.path.join(pulldir, 'Botscores/botscores_likers_v4.pkl'))
botlite_lk = pd.read_pickle(os.path.join(pulldir, 'Botscores/botscores_likers_lite.pkl'))
botv4_rt = pd.read_pickle(os.path.join(pulldir, 'Botscores/botscores_retweeters_v4.pkl'))
botlite_rt = pd.read_pickle(os.path.join(pulldir, 'Botscores/botscores_retweeters_lite.pkl'))


# Links userid and screenname:
laterusers = pd.read_pickle(os.path.join(pulldir, 'laterusers.pkl'))
laterusers['screenname'] = laterusers.index

# look at likers or rewtweeters?
bins = bins_lk
#bins = bins_rt
bm = likers
#bm = retweeters

botv4 = botv4_lk
#botv4 = botv4_rt
botlite = botlite_lk
#botlite = botlite_rt
# Screennames to binsizes:
binsizes = pd.DataFrame([[name, len(l)] for l in bins for name in l],
                   columns=['screenname', 'binsize'])
binsizes.set_index('screenname', inplace = True)

# Features Frame 1 / 5  : Add screennames
ff = np.transpose(bm) # start ff with users from binary matrix
ff.drop(ff.iloc[:, 0:ff.shape[1]], inplace=True, axis=1) # drop all columns except for screenname
ff.index.name = 'screenname'; ff.rename_axis(None, axis='columns', inplace=True)
#ff[ff.index.duplicated(keep=False)]

# Features Frame 2 / 5  : Add bin sizes
ff = pd.concat([ff,binsizes], axis = 1)
#ff[ff.index.duplicated(keep=False)]

# Features Frame 3 / 5  : Add user-id to dataframe, either form v4 or from laterusers. we use laterusers here (bigger set)
# join such that we only ids to the usernames we have in ff2
ff = ff.join(laterusers, how='left')
ff.rename(columns={'id':'userid'}, inplace = True)

# Features Frame 4 / 5  : Botometer scores
    # Botometer v4:
botv4['user-id'] = botv4['user-id'].astype('int')
    # keep relevant columns only
botv4.set_index('user-id', inplace = True); botv4.index.name = 'userid'
botv4 = botv4[['screenname_from_list','raw_overall_uni',
               'raw_astroturf_uni','raw_fake_follower_uni','raw_financial_uni',
               'raw_self_declared_uni','raw_spammer_uni','raw_other_uni']]
    # Botometer Lite:
botlite.set_index('userid', inplace=True); botlite.drop(['tweetid'], axis=1, inplace=True)
botlite.rename(columns={"scores":"lite"}, inplace = True)
    # Both contain a few silly duplicates:
        #ff[ff.index.duplicated(keep=False)]
        #botlite[botlite.index.duplicated(keep=False)]
botv4 = botv4[~botv4.index.duplicated(keep='first')]
botlite = botlite[~botlite.index.duplicated(keep='first')]
    # merge them:
botscores = pd.concat([botv4,botlite], axis=1)
    # add missing screennames:
laterusers_id = laterusers.set_index('id')
for id in botscores[botscores['screenname_from_list'].isna()].index:
    try:
        botscores.at[id, 'screenname_from_list'] = laterusers_id.at[id, 'screenname']
    except:
        pass
# No duplicates:
# botscores[botscores.index.duplicated(keep=False)]
# Single missing screenname:
# botscores[botscores['screenname_from_list'].isna()]

botscores['screenname'] = botscores['screenname_from_list']
#botscores['userid_botscores'] = botscores.index.astype('int')
botscores.set_index('screenname_from_list', inplace = True)
botscores.index.name = 'screenname'

# 6 duplicates; THIS IS A BIT WEIRD:
# botscores[botscores.index.duplicated(keep=False)].shape
# Single missing screenname:
# botscores[botscores['screenname'].isna()].shape

# Features Frame 5 / 5  : Add Botometer scores to ff, keeping all users from ff
# Drop weird duplicates
botscores = botscores[~botscores.index.duplicated(keep='first')]
# concat:
ff = pd.concat([ff,botscores], axis = 1)
# done!
ff.head()
# save dataframe as pkl file
# CHANGE NAME
ff.to_pickle(os.path.join(pulldir, 'features-frame_likers.pkl'))
