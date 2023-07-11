import tweepy
from tweepy import StreamingClient, StreamRule
import os
import json

bearer_token = "ZJeHgPu793miiGO" 
class TweetPrinterV2(tweepy.StreamingClient):


    def on_tweet(self, tweet):
        self.saveTweet(tweet, tweet.data)
        print(f"{tweet.id} {tweet.created_at} ({tweet.author_id}): {tweet.text}")
        print("-"*50)

    def saveTweet(self, tweet, tweetjson):
            try:
                filename = "output/tweet_" + str(tweet.id) + ".json"
                with open(filename, 'a') as outfile:
                    json.dump(tweetjson, outfile)
            except BaseException as ex:
                raise Exception('Error saving tweet', ex)

printer = TweetPrinterV2(bearer_token)

#rules = printer.get_rules()
#for r in rules.data:
#     printer.delete_rules(r.id)
    
# add new rules
rule = StreamRule(value="Luciani")
rule = StreamRule(value="(Alegatos) OR (lawfare) OR (Obra pública) Or (Vialidad) OR (fiscalía)")
rule = StreamRule(value="(@CFKArgentina) OR (@alferdez)")
rule = StreamRule(value="Cristina place_country:AR")
rule = StreamRule(value="#TodosConCristina OR #CristinaPresa OR #CristinaCondenada OR #TodoslosCHORROSconCristina OR #CFKLadronaDeLaNacionArgentina OR #ElPoderJudicialApesta")
rule = StreamRule(value="#Lucianinotienepruebas OR #LucianiNosetoca")
printer.add_rules(rule)
printer.filter(expansions=["author_id", "referenced_tweets.id", "in_reply_to_user_id"],tweet_fields="created_at")