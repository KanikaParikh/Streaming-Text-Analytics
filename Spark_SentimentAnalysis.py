# Kanika Parikh 216030215 and Kaumilkumar Patel 216008914
# Assignment 3 : Part B

"""
    This Spark app connects to a script running on another (Docker) machine
    on port 9009 that provides a stream of raw tweets text. That stream is
    meant to be read and processed here, where top trending hashtags are
    identified. Both apps are designed to be run in Docker containers.

    To execute this in a Docker container, do:
    
        docker run -it -v $PWD:/app --link twitter:twitter eecsyorku/eecs4415

    and inside the docker:

        spark-submit spark_app.py

    For more instructions on how to run, refer to final tutorial 8 slides.

    Made for: EECS 4415 - Big Data Systems (York University EECS dept.)
    Modified by: Tilemachos Pechlivanoglou
    Based on: https://www.toptal.com/apache/apache-spark-streaming-twitter
    Original author: Hanee' Medhat

"""
# Reference used- https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/


from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row,SQLContext
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import sys
import os

# create spark configuration
conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark context with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# create the Streaming Context from spark context, interval size 2 seconds
ssc = StreamingContext(sc, 2)
# setting a checkpoint for RDD recovery (necessary for updateStateByKey)
ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009
dataStream = ssc.socketTextStream("twitter",9009)

# ---------------------------------------------------------------
# MODIFIED---
# Dictionary to hold 10 hashtags for each topic where key: topic and vlaues: hashtags

tweets_dict = {
       'Politics': ['#america', '#vote' ,'#donaldtrump', '#politicalmemes ','#freedom','#politics','#democrats', '#NDA','#obama','#democraticparty'],
       'Amazon': ['#amazon','#amazonprime','#amazondeals','#onlineshopping','#fashion', '#amazonseller', '#amazonfreebies','#ebook','#amazonreviewer','#amazonfba'],
       'Apple': ['#apple', '#iphone', '#applewatch', '#ios','#airpods','#shotoniphone','#macbook','#macbookpro','#ipadpro','#ios'],
       'Shoes': ['#shoes','#fashion','#shoesaddict', '#adidas' ,'#fashionblogger','#nike', '#ootd',' #jordan','#footwear','#shoesforsale'],
       'CryptoCurrency': ['#crypto','#bitcoin','#cryptocurrency','#blockchain','#forex','#cryptotrading','#bitcoins','#investment','#bitcoincash','#bitcoinprice']
       }

# Returns boolean value (True: for values in dict otherwise False)
def Filtering_hashtags(line):

    res = False

    for w in line.split(" "):
        for t in tweets_dict.values():
            if w.lower() in t:
                res = True

    return(res)

# Filtering_hashtags function to filter tweets and returns new Data stream containing only the elements that are in dictionary.

hashtags = dataStream.filter(Filtering_hashtags)

# Grouping them based on a topic (dictionary key) 

def tweets_topic(line):
    res = ""

    for w in line.split(" "):
        # iterating over dictionary values to group them.
        for key in tweets_dict.keys():

            for value in tweets_dict[key]:
                if value == w.lower():
                    res = key
    return(res)

def tweets_sentiment(tweet):
    
    sia = SIA()
    polarity = sia.polarity_scores(tweet)

    if polarity['compound'] > 0.2:
        return('Positive')

    elif polarity['compound'] < -0.2:
        return('Negative')

    else:
        return('Neutral')

# -----------------------------------------------------------
# map each hashtag to be a pair of (hashtag,1)
hashtag_counts = hashtags.map(lambda x: (tweets_topic(x) + "-" + tweets_sentiment(x), 1))

# adding the count of each hashtag to its last count
def aggregate_tags_count(new_values, total_sum):
    return sum(new_values) + (total_sum or 0)

# do the aggregation, note that now this is a sequence of RDDs
hashtag_totals = hashtag_counts.updateStateByKey(aggregate_tags_count)

# MODIFIED:
# checks if values.txt file exists,then remove it before running
if os.path.exists('values.txt'):
    os.remove('values.txt')

# creates new files for graph data and output data
values = open('values.txt', 'a+') # keep apending to file
output = open('PARTB_OUTPUT.txt', 'a+')

# process a single time interval
def process_interval(time, rdd):
    # print a separator
    print("----------- %s -----------" % str(time))
    output.write("----------- %s -----------\n" % str(time))
    try:
        all_rdd = rdd.take(1000)
        for tag in all_rdd:
            # MODIFIED: write output to file
            values.write('{:<40} {}\n'.format(tag[0], tag[1])) 
            output.write('{:<40} {}\n'.format(tag[0], tag[1]))
            print('{:<40} {}'.format(tag[0], tag[1]))
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)

# Do this for every single interval
hashtag_totals.foreachRDD(process_interval)

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()

# MODIFIED: close files
values.close()
output.close()