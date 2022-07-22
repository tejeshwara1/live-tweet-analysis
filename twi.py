import streamlit as st
import warnings
warnings.filterwarnings("ignore")
# EDA Pkgs
import pandas as pd
import numpy as np
import tweepy
import json
from tweepy import OAuthHandler
import re
from textblob import TextBlob
from geopy import Nominatim
import pydeck as pdk
import plotly.express as px
from datetime import datetime, timedelta
#To Hide Warnings
st.set_option('deprecation.showfileUploaderEncoding', False)
st.set_option('deprecation.showPyplotGlobalUse', False)

# Viz Pkgs
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
#sns.set_style('darkgrid')


STYLE = """
<style>
img {
    max-width: 100%;
}
</style> """

def main():
    """ Common ML Dataset Explorer """

    html_temp = """
	<div style="background-color:#1DA1F2;"><p style="color:white;font-size:40px;padding:9px">Realtime Twitter Sentiment Analysis</p></div>
	"""
    st.markdown(html_temp, unsafe_allow_html=True)

    ################# Twitter API Connection #######################
    consumer_key = "twVdlTNpcT41vRXDxS6YQsGxJ"
    consumer_secret = "GcB0h7mHwvuQ0OUhabiKFvwbGtuFIdQ8AaS1BGUFZsDdBQJGGp"
    access_token = "1134044565353029633-VkwjeSNrvVpT2AlB8gPiJOaYLGJFHG"
    access_token_secret = "H7WLfoUxzQx4FbQkXv6RkiDxZl4S8ECQdHsZ3lror7v5c"

    # Use the above credentials to authenticate the API.

    auth = tweepy.OAuthHandler( consumer_key , consumer_secret )
    auth.set_access_token( access_token , access_token_secret )
    api = tweepy.API(auth)
    ################################################################

    df = pd.DataFrame(columns=["Date","Time","User","IsVerified","Tweet","User_location"])

    # Write a Function to extract tweets:
    def get_tweets(Topic,Count):
        i=0
        my_bar = st.progress(0) # To track progress of Extracted tweets
        for tweet in tweepy.Cursor(api.search_tweets, q=Topic+"-filter:retweets",count=c, lang="en").items():
            if i+1>Count:
                break
            else:
                pass
            try:
                my_bar.progress((i/Count)+1)
            except:
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

    def get_coord(df):
        lat=[]
        lon=[]
        for i in range(len(df["User_location"])):
            if df["User_location"][i]!=None:
                locator = Nominatim(user_agent="myGeocoder")
                location = locator.geocode(df["User_location"][i])
                if location==None:
                    lat.append(None)
                    lon.append(None)
                else:
                    lat.append(location.latitude)
                    lon.append(location.longitude)
            else:
                lat.append(None)
                lon.append(None)
        df["lat"]= lat
        df["lon"]= lon
        return df

    


    # Collect Input from user :
    c = st.number_input("Enter Tweet count",min_value=50)
    Topic = str(st.text_input("Enter the topic you are interested in (Press Enter once done)"))
    # Topic = "modi"


    if len(Topic) > 0 :

        # Call the function to extract the data. pass the topic and filename you want the data to be stored in.
        with st.spinner("Please wait, Tweets are being extracted"):
            get_tweets(Topic , Count=c)
        st.success('Tweets have been Extracted !!!!')


        # Call function to get Clean tweets
        df['clean_tweet'] = df['Tweet'].apply(lambda x : clean_tweet(x))

        # Call function to get the Sentiments
        df["Sentiment"] = df["Tweet"].apply(lambda x : analyze_sentiment(x))


        # See the Extracted Data :
        st.subheader("Extracted Data")
        st.write(df)


        # get the countPlot
        st.subheader("Count Plot for Different Sentiments")
        sns.countplot(df["Sentiment"])
        st.pyplot()

        # Piechart
        st.subheader("Pie Chart for Different Sentiments")
        a=len(df[df["Sentiment"]=="Positive"])
        b=len(df[df["Sentiment"]=="Negative"])
        c=len(df[df["Sentiment"]=="Neutral"])
        d=np.array([a,b,c])
        explode = (0.1, 0.0, 0.1)
        plt.pie(d,shadow=True,explode=explode,labels=["Positive","Negative","Neutral"],autopct='%1.2f%%')
        st.pyplot()


        # get the countPlot Based on Verified and unverified Users
        st.subheader("Count Plot for Different Sentiments for Verified and unverified Users")
        sns.countplot(df["Sentiment"],hue=df.IsVerified)
        st.pyplot()





        st.subheader("Distribution of users with respect to geographical locations")

        with st.spinner("Please wait, getting coordinates to plot"):
            df = get_coord(df)
        
        # df = pd.read_csv('test.csv')


        fig = px.scatter_geo(df,lat='lat',lon='lon', hover_name="clean_tweet",color="Sentiment")
        fig.update_layout(title = 'Tweets Sentiment about '+Topic, title_x=0.5)
        fig.show()










    st.sidebar.header("About App")
    st.sidebar.info("Realtime Twitter Sentiment analysis Project will scrap tweets of the topic selected by the user. The extracted tweets will then be used to determine the Sentiments of those tweets. \
                    The different Visualizations will help us get a feel of the overall mood of the people on Twitter regarding the topic we select.")
    st.sidebar.text("Built with Streamlit")






if __name__ == '__main__':
    main()

