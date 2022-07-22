import time  # to simulate a real time data, time loop
import random as rd
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import streamlit as st
import warnings
warnings.filterwarnings("ignore")
# EDA Pkgs
import tweepy
import json
from tweepy import OAuthHandler
import re
from textblob import TextBlob
from datetime import datetime, timedelta
#To Hide Warnings
st.set_option('deprecation.showfileUploaderEncoding', False)
st.set_option('deprecation.showPyplotGlobalUse', False)

# Viz Pkgs
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import threading
################# Twitter API Connection #######################
consumer_key = "G8KeigbnwOkpIeBHEuccPUDAZ"
consumer_secret = "npim5gEYPt2D25nJFGGGcWINwfu6QjG6yN4xrUAkUdV2QF9Wal"
access_token = "1521784145906909184-uj28cZNTQZNPpddR1xy8KdqAhEOjP9"
access_token_secret = "mrfUhfMRROgMC1PE7sZrgyCie1QPkOabkD7vLy63oPWCi"

# Use the above credentials to authenticate the API.

auth = tweepy.OAuthHandler( consumer_key , consumer_secret )
auth.set_access_token( access_token , access_token_secret )
api = tweepy.API(auth)
################################################################
df = pd.DataFrame(columns=["Date","Time","User","IsVerified","Tweet","User_location"])


# Write a Function to extract tweets:
def get_tweets(Topic,Count):
    i=0
    for tweet in tweepy.Cursor(api.search_tweets, q=Topic+"-filter:retweets",count=Count, lang="en").items():
        if i+1>Count:
            break
        else:
            pass
        dt = tweet.created_at
        dt = dt+ timedelta(hours=5,minutes=30)
        df.loc[i,"Date"] = str(dt)[:11]
        df.loc[i,"Time"] = str(dt)[11:19]

        df.loc[i,"User"] = tweet.user.name
        df.loc[i,"IsVerified"] = tweet.user.verified
        df.loc[i,"Tweet"] = tweet.text
        df.loc[i,"User_location"] = tweet.user.location
        
        #df.to_csv("TweetDataset.csv",index=False)
        #df.to_excel('{}.xlsx'.format("TweetDataset"),index=False)   ## Save as Excel
        
        i+=1



# Function to Clean the Tweet.
def clean_tweet(tweet):
        return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|([RT])', ' ', tweet.lower()).split())


# Funciton to analyze Sentiment
def analyze_sentiment(tweet):
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity == 0:
        return 'Neutral'
    else:
        return 'Negative'


st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    layout="wide",
)
Topic = str(st.text_input("Enter the Topic"))
c = st.slider('Range of Number of Tweets',1, 500, (5, 10))

if len(Topic)>0:

    placeholder = st.empty()

    while True:


        tot = rd.randint(c[0], c[1])
        get_tweets(Topic ,tot)
        df['clean_tweet'] = df['Tweet'].apply(lambda x : clean_tweet(x))

        df["Sentiment"] = df["Tweet"].apply(lambda x : analyze_sentiment(x))



        sc = df.Sentiment.value_counts()


        with placeholder.container():
            st.write("Total tweets")
            st.write(tot)
            st.write(sc)

            fig1 = px.histogram(data_frame=df, x="Sentiment")
            st.write(fig1)
            time.sleep(1)
