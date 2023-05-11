# Danish National Election 2022 Twitter Data on Likes, Retweets, and Botscores for the purpose of exploring Coordinated Inauthenthic Behavior


This repository contains code related to the dataset on the Danish National Election 2022, available at [Harvard Dataverse](https://doi.org/10.7910/DVN/RWPZUN). See the directory *Data from Danish Twitter on National Election 2022*.

We cluster users in to bins of users that showed exactly the same liking/retweeting behavior over the period. To investigate whether any of these bins exhibited *coordinated inauthenthic behavior*, we were interested in whether bin size correlated with
- user account deletion/suspension (we bought some likes at some point, and saw that the user accounts disappered rather quickly)
- high bot scores from Botometer / Botometer Lite.
We didn't find any correlations. Also not between Botometer and Botometer Lite scores.

*Dates for Data Collection:*
- 1. Nov. 2022 was the election date.
- Oct. 7, 2022 and 30 days forward we scraped with the query *#dkpol -is:retweet OR  #fv22 -is:retweet OR #fv2022 -is:retweet*. See `Pull-All_fv22/parameters.py`.
- Late January to Mid February we looked up user account information and botscores.

Botometer guidelines suggest that we should have looked up botscores runningly as they are somewhat time sensitive, but honestly, checking for correlation with botscores came as an afterthought to the general data collection.

*Code on Dataset:* To use the code in thes repo on the dataset, clone the repo and download the dataset, extract `Data from ... Election 2022/Raw Data/Pull-All_fv22.zip` and place the `Pull-All_fv22` directory in the repo root.

*Much more Information:* For much more information on the research motivation for creating this dataset and undertaking the analysis, please see the introduction to the PhD thesis TODO [Curbing Amplification Online: Towards Improving the Quality of Information Spread on Social Media Using Agent-Based Models and Twitter Data](URL) by Laura Jahn, University of Copenhagen, 2023.

# Dataset components
The dataset contains the following:

## 1. /Raw Data/Pull-All_fv22.zip

### Tweet IDs, Liking Users and Retweeting Users live scraped DATE to DATE

Runningly, we collected the user identities of liking and retweeting users, with the algorithm described in [this paper](URL) using the code from [this repo](https://github.com/humanplayer2/get-twitter-likers-data).

The dataset contains the collected data, time stamped. I.e., for every ~5 minutes in the scrap period, there is a file of the last 48 hours' tweet IDs, and lists of liking and retweeting users. See the linked-to repo for information on the directory and file structure.

This repo contains code to process these rather raw files. In addition to this readme, you can also go through the file `analysis/Pull-fv22-treatment.py` for a bit of practical code.

*Note:* The dataset does not contain e.g. tweet text, as this cannot to shared in batch without violating Twitter's terms and conditions.

See *Data from Danish Twitter on National Election 2022/Raw Data*

## 2. /Preprocessed Data
*Note:* We have uploaded the processed data as it can take quite some RAM to conclude the processing. We ran out of memory on 128 GB RAM Linux machine, so we supplemented it with an additional 2 TB NVMe disk, allocated to swap space. One treatment ended up using ~590 GB of that.

### 2.0 /Preprocessed Data:
Preprocessed using code from this repo, see below.

The `binarymatrices.zip` file contains two Tweet IDs x User IDs matrices (one for likes, one for retweets), with a `1` in `(i,j)` if user `j` liked/retweeted tweet `i`, else `0`.
 - Processed using `binarymatrices.sh`


### 2.1 /Preprocessed Data/Botscores
Contains for every liking user / retweeting user observed during the live scrape,
their botscores according to [Botometer v4](LINK) and [Botometer Lite](LINK).

Collected using `botscores_v4.sh` and `botscores_lite.sh`.

### 2.2 /Preprocessed Data/Clusters
Contains analyses of the binary matricies, where users have been grouped if they share the exact same liking / retweeting behavior. As described in [this other paper](link).

The clustering/binning was done using `/analysis/binning.sh`.

### 2.3 /Preprocessed Data/Later Users and Tweets Lookups
- `latercounts.pkl`: look up of all tweets to get their like and retweet counts,
- `laterusers.pkl`: look up of all user profiles e.g. whether it still exists, has been suspended, error codes, etc.

### 2.4 /Preprocessed Data/Likers Retweeters Pagination
To improve the live scraped data, we have since used Twitter's updated API allowing for pagination to re-collect the liking and retweeting users.

This data should, if no users were deleted or unliked, contain the same information as the live scraped data.

See the section *Disclaimer for Article II* in the PhD thesis [Curbing Amplification Online](URL) for more information.

This paginated data was collected using the [twarc2 package](https://twarc-project.readthedocs.io/en/latest/twarc2_en_us/), using the scripts `analysis/twarc-lookup-liking-users.sh` and `analysis/twarc-lookup-retweeting-users.sh`. As we had multiple bearer tokens available, we split the user lists using `twarc-split-user-list.py` into sublists so we could collect data in parallel.

# Testing for Correlations: Conclusions

Again, we were mostly interested in whether the correlation in liking/retweeting behavior among users correlated with
- user account deletion/suspension, creation date
- high bot scores from Botometer / Botometer lite.

We didn't find any correlations: The size of a user's cluster of identitically liking/retweeting users did not correlate with the user's botscore or botlike score, and the size of a cluster did not correlate with how many of its users had disappered. Also, Botometer and Botometer Lite scores did not correlate with one another.

## To replicate:

1. Run `analysis/features-frame.py`: Collects tweet and user information, including botscores, user cluster sizes, deletions, etc.

In a bit more detail, the feature frames we created to check for correlated features included the following:
- binsize: size of bin/cluster the user is grouped into
- user-ID
- error_title: result from user look-ups, e.g. error if user not found due to deletions and suspensions
- error_detail
- name
- created_at: creation date of user account
- protected: whether user account is private
- verified: whether user account is verified
- followers_count: number of followers of user
- following_count: number of accounts the user follows
- tweet_count: number of posted tweets by user
- listed_count: number of public lists that user is a member of
- screenname
- Botscores
  - All 8 raw, universal Botometer v4 botscores, such as *overall*, *fake follower*, *astroturf*
  - Botometer lite score

2. Run `analysis/correlation-coeff.py`: Loads the feature frame and inspects data, e.g.:
- slices dataframe to filter for users in large bins
- computes the Pearson correlation coefficient across all columns
- plots histogramms comparing users' different features, e.g. bin size and bot scores


# Various Notes:

## `botometer.sh`:

You must add access tokes to `analysis/bearertoken.py`.

pip install botometer tweepy=3.10.0 requests pandas numpy matplotlib

Botometer 1.6.1 that we used is only compatible with Tweepy 3, not Tweepy 4 (used in `analysis/resources/fv22.py`). To run the Botometer tests in `botometer.py`, we suggest setting up a virtual Python enviroment for Botometer, e.g. using Python venv or conda. This does not affect the tweepy version outside the new envionment.
 1. download and install conda: https://conda.io/projects/conda/en/latest/user-guide/install/index.html
 2. create a virtual environment for your python version: `conda create --name botometer python=3.10.8`
 3. swithch to work in the new environment `conda activate botometer`
 4. install botometer and compatible tweepy version in it: `pip install botometer tweepy==3.10.0`
 5. to check which packages are installed in environment: when active, use `conda list`, when inactive use `conda list -n botometer`
 6. deactivate environment with `conda deactivate` or `conda activate base` when changing to other scripts that rely on latest tweepy version.


## Nice todos:
- in tweetlookup.py, both functions `tweet_type` and `parse_tweet` can unfold reason for why tweet type is not found, through "[2]: errors"; see "More dictionary examples" in tweetlookup.py. It would be nice to override more 'borked' values with this, to have a clearer picture of what the status of tweets are, like is now done for users in `parse_users`
- Prep Pull-mini to the degree that it can be shared as just a test folder: replace usernames and tweetIDs with just numbers or so, and remove columns using csv-clean.py from get-twitter-likers-data repo.
