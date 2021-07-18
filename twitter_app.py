# Kanika Parikh 216030215 and Kaumilkumar Patel 216008914
# Assignment 3 : Part A

"""
    This script connects to Twitter Streaming API, gets tweets with '#' and
    forwards them through a local connection in port 9009. That stream is
    meant to be read by a spark app for processing. Both apps are designed
    to be run in Docker containers.

    To execute this in a Docker container, do:
    
        docker run -it -v $PWD:/app --name twitter -p 9009:9009 python bash

    and inside the docker:

        pip install tweepy
        #pip install -U git+https://github.com/tweepy/tweepy.git
        python twitter_app.py

    (we don't do pip install tweepy because of a bug in the previous release)
    For more instructions on how to run, refer to final slides in tutorial 8

    Made for: EECS 4415 - Big Data Systems (York University EECS dept.)
    Author: Tilemachos Pechlivanoglou

"""
# Kanika Parikh and Kaumilkumar Patel
# Assignment 3 - Part A


# from __future__ import absolute_import, print_function

import socket
import sys
import json


from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream

# Replace the values below with yours
'''consumer_key="ZAPfZLcBhYEBCeRSAK5PqkTT7"
consumer_secret="M81KvgaicyJIaQegdgXcdKDeZrSsJz4AVrGv3yoFwuItQQPMay"
access_token="2591998746-Mx8ZHsXJHzIxAaD2IxYfmzYuL3pYNVnvWoHZgR5"
access_token_secret="LJDvEa0jL7QJXxql0NVrULTAniLobe2TAAlnBdXRfm1xF"
'''

class TweetListener(StreamListener):
    """ A listener that handles tweets received from the Twitter stream.

        This listener prints tweets and then forwards them to a local port
        for processing in the spark app.
    """

    def on_data(self, data):
        """When a tweet is received, forward it"""
        try:

            global conn

            # load the tweet JSON, get pure text
            full_tweet = json.loads(data)
            tweet_text = full_tweet['text']

            # print the tweet plus a separator
            print ("------------------------------------------")
            print(tweet_text + '\n')

            # send it to spark
            conn.send(str.encode(tweet_text + '\n'))
        except:

            # handle errors
            e = sys.exc_info()[0]
            print("Error: %s" % e)


        return True

    def on_error(self, status):
        print(status)

# ==== setup local connection ====

# IP and port of local machine or Docker
TCP_IP = socket.gethostbyname(socket.gethostname()) # returns local IP
TCP_PORT = 9009

# setup local connection, expose socket, listen for spark app
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")

# if the connection is accepted, proceed
conn, addr = s.accept()
print("Connected... Starting getting tweets.")


# ==== setup twitter connection ====
listener = TweetListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, listener)

# setup search terms --MODIFIED 
# political parties, companies, product brands, stocks, etc.
track = ['#apple', '#iphone', '#applewatch', '#ios','#airpods','#shotoniphone','#macbook','#macbookpro','#ipadpro','#ios','#amazon','#amazonprime','#amazondeals','#onlineshopping','#fashion', '#amazonseller', '#amazonfreebies','#ebook', '#amazonreviewer','#amazonfba','#crypto','#bitcoin','#cryptocurrency','#blockchain','#forex','#cryptotrading','#bitcoins','#investment','#bitcoincash','#bitcoinprice','#america', '#vote' ,'#donaldtrump', '#politicalmemes ','#freedom','#politics','#democrats', '#NDA','#obama','#democraticparty','#shoes','#fashion','#shoesaddict', '#adidas' ,'#fashionblogger','#nike', '#ootd',' #jordan','#footwear','#shoesforsale']

language = ['en']
#locations = [-130,-20,100,50]

# get filtered tweets, forward them to spark until interrupted
try:
    stream.filter(track=track, languages=language)
except KeyboardInterrupt:
    s.shutdown(socket.SHUT_RD)

