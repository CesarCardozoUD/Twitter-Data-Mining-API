# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 12:10:28 2019

@author: Cesar Cardozo
"""

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor 

from textblob import TextBlob
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import json

"""
import twitter_credentials
"""

ACCESS_TOKEN = "869673043-NV32kgdYZ8KhbUZEwj52nLYbhij0669DWnrEyR1q"
ACCESS_TOKEN_SECRET = "YBCV5Pfi5ZvsTtnlOllWNCzKhlSIrC85Xy7jYQOT6Jf6I"
CONSUMER_KEY = "MFEZvaki3Sa8fuYQq7gBW6wtl"
CONSUMER_SECRET = "Gq6XlgZDZyaUi3UM2W5NXUqhLowu2K4rrQVPi7CibV17msskUp"
BOGOTA_WOE_ID = 368148
COLOMBIA_WOE_ID = 23424787


class TwitterAuthenticator():
    
    def authenticate_twitter_app(self):         
        """
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        """   
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        return auth


class TwitterClient():
    def __init__(self, twitter_user=None):
        self.twitter_user = twitter_user 
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        
    def get_twitter_client_api(self):
        return self.twitter_client
    
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

class TwitterStreamer():
    
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    
    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)
        
        

class TwitterListener(StreamListener):
    
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
    
    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error en los datos %s" % str(e))
        return True
    
    def on_error(self, status):
        if status == 402:
            return False
        print(status)
        
class TweetAnalyzer():
    
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))        
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1
    
    def tweets_to_dataframe(self, tweets):
        df = pd.DataFrame(data = [tweet.id for tweet in tweets], columns=['ID'])
        df['Fecha'] = np.array([tweet.created_at for tweet in tweets])
        df['Num_Retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['Tweet'] = np.array([tweet.text for tweet in tweets])
        df['Fuente'] = np.array([tweet.source for tweet in tweets])
        return df
    
    def trends_to_dataframe(self, trends):
        trendy = json.loads(json.dumps(trends, indent=1))
        df = pd.DataFrame(data = [trend['name'] for trend in trendy[0]['trends']], columns=['HashTag'])
        df['Veces_Tweet'] = np.array([trend['tweet_volume'] for trend in trendy[0]['trends']])
        return df
        
        
if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()
    
    tweets = api.user_timeline(screen_name = "luzrello", count = 2000)
 
    bogota_trends = api.trends_place(COLOMBIA_WOE_ID)
    trends = json.loads(json.dumps(bogota_trends, indent=1))
    df = tweet_analyzer.tweets_to_dataframe(tweets)
    bdf = tweet_analyzer.trends_to_dataframe(bogota_trends)
    bdf = bdf.sort_values(by='Veces_Tweet', ascending=False)
    print(bdf.head(15))
    #time_serie = pd.Series(data=df['Likes'].values, index=df['Fecha'])
    #time_serie.plot(figsize=(16,4), color = 'r')
    
    #time_serie = pd.Series(data=df['Num_Retweets'].values, index=df['Fecha'])
    #time_serie.plot(figsize=(16,4), color = 'b')
    
    #plt.show()
    #df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['Tweet']])
    #df = df.sort_values(by='Num_Retweets', ascending=False)
    #print(df.head(10))