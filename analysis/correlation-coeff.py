import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
# if import * does not work, try os.getcwd() to see where we are at
try: #wrapped in try so that you can run it without error trigger. If preferred, I can comment out too
    os.chdir('/Users/qbj218/Documents/Git/fv22-wip/analysis')
except:
    pass
from resources.fv22 import *


#pulldir = '../Pull-All_June/'
pulldir = '../Pull-All_fv22/'
#pulldir = '../Pull-mini/'

with open(os.path.join(pulldir, 'features-frame_likers.pkl'), 'rb') as f:
    ff_lk = pickle.load(f)

with open(os.path.join(pulldir, 'features-frame_retweeters.pkl'), 'rb') as f:
    ff_lk = pickle.load(f)

ff_lk.head()
list(ff_lk.columns)

ff_lk.head().T
ff_lk.loc[:,'binsize'].max()

# filter to clusters > 50
ff_large = ff_lk.loc[(ff_lk['binsize'] >= 50)]# & (ff_lk['binsize'] <= 100)]
ff_small = ff_lk.loc[(ff_lk['binsize'] <= 10)]
ff_vp = ff_lk.loc[(ff_lk['binsize'] == 87)]


df1 = ff_large 
df2 = ff_small 

df = ff_lk
# Pearson correlation coefficient for all columns
df.corr(numeric_only=True)
plt.figure(figsize=(14,8))
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='Blues')
plt.show()
# print column error-title of ff_lk
print((list(ff_lk.loc[:,'error_title']!=('none' or 'NaN'))))
list(ff_lk.loc[:,'error_detail'])
ff_lk

plt.plot(df.loc[:,'raw_overall_uni'],df.loc[:,'binsize'], 'o', markersize=7, alpha = .1)
plt.show()
plt.plot(df.loc[:,'raw_astroturf_uni'], 'o', markersize=7, alpha = .1)

plt.hist(df1.loc[:,'raw_overall_uni'], alpha = .7, bins = 100, density = True)
plt.show()
plt.hist(ff_vp.loc[:,'raw_overall_uni'], alpha = .7, bins = 100)
plt.show()

plt.hist(df2.loc[:,'raw_overall_uni'], alpha = .7, bins = 100)
plt.show()

plt.hist(ff_lk.loc[:,'raw_overall_uni'], alpha = .7, bins = 100)
plt.show()
