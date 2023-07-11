from os import walk
import json
from types import SimpleNamespace as Namespace
from itertools import islice

# folder path
#dir_path = r'C:\\Users\\licen\\OneDrive\\Documentos\\git\\twitter-monitor\\output\\3107'
dir_path = r'C:\\Users\\licen\\OneDrive\\Documentos\\git\\twitter-monitor\\output'

import mysql.connector

update_tweet_quoted = ("UPDATE tweets_cfk.tweets_alegatos SET quoted_id = %s WHERE tweet_id = %s")
update_tweet_retweeted = ("UPDATE tweets_cfk.tweets_alegatos SET retweeted_id = %s WHERE tweet_id = %s")
update_tweet_replied_to = ("UPDATE tweets_cfk.tweets_alegatos SET replied_to_id = %s WHERE tweet_id = %s")


# list to store files name
res = []
for (dir_path, dir_names, file_names) in walk(dir_path):
    cnx = mysql.connector.connect(user='ana', password='Facebook#36',
                                    host='179.43.112.209',
                                    database='tweets_cfk')
    curB = cnx.cursor(buffered=True)
    for tweetfile in list(islice(file_names, 500)):
        f = open(dir_path + '\\' + tweetfile, "r")
        text = f.read()
        x = json.loads(text, object_hook=lambda d: Namespace(**d))
        #print(x.id)
        if hasattr(x, 'referenced_tweets'):
            print((x.id, x.referenced_tweets))
            for t in x.referenced_tweets:
                if t.type == "quoted":
                    curB.execute(update_tweet_quoted, (t.id, x.id))
                elif t.type == "retweeted":
                    curB.execute(update_tweet_retweeted, (t.id, x.id))
                elif t.type == "replied_to":
                    curB.execute(update_tweet_replied_to, (t.id, x.id))
            #if hasattr(x.referenced_tweets, ''):
            #curB.execute(update_tweet, (x.in_reply_to_user_id, x.id))
    curB.close()
    cnx.commit()
    cnx.close()
print(res)