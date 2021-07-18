PART A:
1. Open one terminal for Twitter_app.py:
– docker run -it -v $PWD:/app --name twitter -w /app python bash
– pip install tweepy (pip install -U git+https://github.com/tweepy/tweepy.git)
– python twitter_app.py

2. Another terminal for spark_app.py
– docker run -it -v $PWD:/app --link twitter:twitter eecsyorku/eecs4415
– spark-submit spark_app.py


PART B: 
1. Open one terminal for Twitter_app.py:
– docker run -it -v $PWD:/app --name twitter -w /app python bash
– pip install tweepy (pip install -U git+https://github.com/tweepy/tweepy.git)
– python twitter_app.py

2. Another terminal for spark sentiment app
– docker run -it -v $PWD:/app --link twitter:twitter eecsyorku/eecs4415
– apt-get update
– apt-get install gcc
– apt-get install python-dev python3-dev
– apt-get install python-nltk
– python (go into python bash)
	- import nltk
	- nltk.download('vader_lexicon')
	- exit() or ctrl+D 
– spark-submit Spark_SentimentAnalysis.py

Run plot_graph.py:
- open new local terminal
- python plot_graph.py
