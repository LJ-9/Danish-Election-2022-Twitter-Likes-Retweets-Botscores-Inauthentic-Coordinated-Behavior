import os
import pandas as pd
import numpy as np
import glob
import csv
import pickle
from ast import literal_eval

# Binning.
# This is "groupby_app" from https://stackoverflow.com/a/46629623/1654116
# only with transposition, and also lists bins with only 1 user.
#
# Given binarymatrix, returns list of tuples of identical likers/retweeters

def binning(df): # @jezrael's sol
    print('Binning, including singles (much slower)')
    print('Binary matrix shape: (tweets, users) =', df.shape)
    print('Transposing: Users to rows, tweets to columns...')
    df = df.T
    print('Grouping rows (users) by all columns (tweets)...')
    bins = df.groupby(df.columns.tolist()).apply(lambda x: tuple(x.index)).tolist()
    print('Number of bins:', len(bins))
    return bins


# Given binarymatrix, returns list of tuples of identical likers/retweeters,
# but first subsets to users with a duplicate, thus not producing bins of size 1.
def binning_no_singles(df): # @jezrael's sol
    print('Binning, excluding singles (much faster)')
    print('Binary matrix shape: (tweets, users) =', df.shape)
    print('Transposing: Users to rows, tweets to columns...')
    df = df.T
    print('Removing non-duplicates...')
    df = df[df.duplicated(keep=False)]
    print('Grouping rows (users) by all columns (tweets)...')
    bins = df.groupby(df.columns.tolist()).apply(lambda x: tuple(x.index)).tolist()
    print('Number of bins:', len(bins))
    return bins

# This is "group_duplicate_index_v2" from https://stackoverflow.com/a/46629623/1654116
# only with transposition and index naming added
#
# I don't trust it. Maybe v1 is better, but this did weird.
#
# def binning(binarymatrix):
#     print("Transposing...")
#     binarymatrix = binarymatrix.T
#     print("Index name...")
#     binarymatrix.index.name = 'userID'
#     print("Crazy magic...")
#     a = binarymatrix.values
#     s = (a.max()+1)**np.arange(binarymatrix.shape[1])
#     sidx = a.dot(s).argsort()
#     b = a[sidx]
#     print("Concatenation...")
#     m = np.concatenate(([False], (b[1:] == b[:-1]).all(1), [False] ))
#     print("Flattening...")
#     idx = np.flatnonzero(m[1:] != m[:-1])
#     print("Listing...")
#     I = binarymatrix.index[sidx].tolist()
#     print("Returning bins...")
#     bins = [I[i:j] for i,j in zip(idx[::2],idx[1::2]+1)]
#     return bins


def bin_likers(pulldir):
    filepath = os.path.join(pulldir,'binary-matrix-likers.pkl')
    print('Loading',filepath,'...')
    likers_binarymatrix = pd.read_pickle(filepath)

    print('Binning likers...')
    bins_likers = binning(likers_binarymatrix)

    savepath = os.path.join(pulldir,'bins_likers.pkl')
    print("Saving liker bins to",savepath)
    #bins_likers.to_pickle(savepath)
    with open(savepath, 'wb') as f:
        pickle.dump(bins_likers, f)
    # to load:
    # with open(savepath, 'rb') as f:
    #    bins_likers = pickle.load(f)


def bin_retweeters(pulldir):
    filepath = os.path.join(pulldir,'binary-matrix-retweeters.pkl')
    print('Loading',filepath,'...')
    retweeters_binarymatrix = pd.read_pickle(filepath)

    print('Binning retweeters...')
    bins_retweeters = binning(retweeters_binarymatrix)

    savepath = os.path.join(pulldir,'bins_retweeters.pkl')
    print("Saving retweeter bins to",savepath)
    #bins_retweeters.to_pickle(savepath)
    with open(savepath, 'wb') as f:
        pickle.dump(bins_retweeters, f)
