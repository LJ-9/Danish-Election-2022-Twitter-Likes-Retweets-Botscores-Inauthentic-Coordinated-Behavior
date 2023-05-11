import os
import pickle
import pandas as pd
import numpy as np
from resources.fv22 import *

#pulldir = '../Pull-All/'
#pulldir = '../Pull-mini/'
pulldir = '../Pull-June/'

bm_likes = pd.read_csv(os.path.join(pulldir, 'binary-matrix-likers.csv'))
bm_likes.set_index('Unnamed: 0', inplace=True)
bm_likes.index.name = 'tweet'
bm_likes = bm_likes.fillna(0)
bm_likes.to_pickle(os.path.join(pulldir, 'binary-matrix-likers.pkl'))
bm_likes = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-likers.pkl'))

bm_retweets = pd.read_csv(os.path.join(pulldir, 'binary-matrix-retweeters.csv'))
bm_retweets.set_index('Unnamed: 0', inplace=True)
bm_retweets.index.name = 'tweet'
bm_retweets = bm_retweets.fillna(0)
bm_retweets.to_pickle(os.path.join(pulldir, 'binary-matrix-retweeters.pkl'))
bm_retweets = pd.read_pickle(os.path.join(pulldir, 'binary-matrix-retweeters.pkl'))
