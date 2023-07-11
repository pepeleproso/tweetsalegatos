import tweepy
from tweepy import StreamingClient, StreamRule
import os
import json
import time
import mysql.connector

bearer_token = "%3DovLAKy73kdxYsMJv4bEQzjzQHlh7JFTQflapSSIFUB6avhFBwk"

for i in range(0, 500):
    cnx = mysql.connector.connect(user='', password='',
                              host='',
                              database='tweets_cfk')

    print("------------inicio lote----------------------------")
    print('Lote :' + str(i))
    cursor = cnx.cursor()
    print('Realizando query'
    )
    query = ("select author_id "
                "FROM tweets_cfk.tweets_authors "
                "where verificado is null "
                "group by author_id "
                "order by author_id "
                "limit 0,100")

    cursor.execute(query)

    print('Procesando resultados query')
    userstosearch = []

    for author_id in cursor:
        userstosearch.append(author_id[0])

    cursor.close()

    update_username = (
    "UPDATE tweets_cfk.tweets_authors SET verificado = %s, fechacreacion= %s, imagenperfil=%s, CantidadTweets=%s, CantidadSeguidores=%s, CantidadSeguidos=%s, CantidadListas=%s "
    "WHERE author_id = %s")

    update_userborrado = (
    "UPDATE tweets_cfk.tweets_authors SET verificado = %s "
    "WHERE author_id = %s")


    client =  tweepy.Client(bearer_token=bearer_token)

    try:
        print('buscando usuarios en twitter')
        users = client.get_users(ids=userstosearch, user_fields=['created_at','profile_image_url','verified','public_metrics'])
        
        print('insertando usuarios encontrados')
        curB = cnx.cursor(buffered=True)

        if users[0]:
            for user in users[0]:
                try:
                    authorid = user.id
                    verified = user.verified
                    created_at = user.created_at
                    profile_image_url = user.profile_image_url

                    if user.public_metrics:
                        cantidadTweets = user.public_metrics['tweet_count']
                        cantidadSeguidores = user.public_metrics['followers_count']
                        cantidadSeguidos = user.public_metrics['following_count']
                        cantidadListas = user.public_metrics['listed_count']

                    # created_at
                    # verified
                    # profile_image_url
                    print(authorid, verified, created_at, profile_image_url)
                    curB.execute(update_username, (verified, created_at, profile_image_url, cantidadTweets, cantidadSeguidores, cantidadSeguidos, cantidadListas, authorid))
                except Exception as e:
                    print("error")
                    print(e)
                    break

            curB.close()
            cnx.commit()

        print('insertando usuarios con errores')
        curB = cnx.cursor(buffered=True)
        for user in users[2]:
            try:
                authorid = user['value']
                verified = 0
                print(authorid)
                curB.execute(update_userborrado, (verified, authorid))
            except Exception as e:
                print("error")
                print(e)
                break    
        cnx.commit() 
        cnx.close()

    except  Exception as e:
                print("error")
                print(e)
                break
    print("Fin lote-----------------------------------------------------------")
    time.sleep(5)

