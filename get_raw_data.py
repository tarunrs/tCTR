 # -*- coding: utf-8 -*-

import sys
import tweepy
import webbrowser
import pickle
import os
from time import time, strftime, localtime

CONSUMER_KEY = 'zXhZvsaUSLbnk1E2KjcNw'
CONSUMER_SECRET = 'dqinsFtcx7aO7TKJYzTr3s8JpgWjwCMjFMnVwm41plg'
ACCESS_TOKEN = '9175042-LgX3UMYB9qSauD7DvEjp0Nsle3vttognI0Fy0KHZ4M'
ACCESS_TOKEN_SECRET = 'iAMQCAwdZF2RuTI8jEaV6BxPDcLlQaiY2J7dFYj4wg'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def create_directories(directory):
  print "Creating directories"
  sub_dirs = ["raw_data", "ctr_data", "feature_data", "feature_files", "support_data"]
  if not os.path.exists(directory):
    print "\t" + directory
    os.makedirs(directory)
  for d in sub_dirs:
    temp_dir = directory + "/" + d
    if not os.path.exists(temp_dir):
      print "\t" + temp_dir
      os.makedirs(temp_dir)
  
def get_tweets(user_id):
  tweets = []
  print "Getting tweets for user", user_id
  i = 0
  for status in tweepy.Cursor(api.user_timeline, id=user_id).items():
    i += 1
    if i % 500 == 0:
      print i
    tweets.append(status)
  fname = user_id + "/raw_data/tweets.pkl"
  print "Dumping :", fname
  pickle.dump(tweets, open(fname, "w"))

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Enter a Username"
  else:
    user_id = sys.argv[1]
    print "Starting processing for ", user_id
    create_directories(user_id)   
    get_tweets(user_id)

