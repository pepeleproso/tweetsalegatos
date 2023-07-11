from ssl import create_default_context
import tweepy
#from tweepy import StreamingClient, StreamRule
import os
import json
import time
import mysql.connector
from datetime import date, datetime

bearer_token = "4eByWDgKr7ghgSd7QnBXQlnJb06ZJeHgPu793miiGO" 

client =  tweepy.Client(bearer_token=bearer_token)

id= 138814032
starttime = datetime.fromisoformat('2022-07-27')
endtime = datetime.fromisoformat('2022-08-23')

users = client.get_users_tweets(id, 
                                end_time=endtime,
                                expansions=["author_id", "referenced_tweets.id", "in_reply_to_user_id"],
                                tweet_fields="created_at",
                                start_time=starttime)

cnx = mysql.connector.connect(user='', password='',
                              host='',
                              database='tweets_cfk')

insert_cfk_tweets = (
    "INSERT INTO tweets_cfk.tweets_alegatos "
    "(tweet_id, author_id, created_at, text,author_username) "
    "VALUES (%s, %s, %s, %s, 'cfkargentina ')")

print(users)

curB = cnx.cursor(buffered=True)

for t in users[0]:
    print(t.id)
    curB.execute(insert_cfk_tweets, (t.id, t.author_id, t.created_at, t.text))
    
curB.close()
cnx.commit()