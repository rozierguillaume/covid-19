#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Guillaume Rozier - 2020 - MIT License
# This script will automatically tweet new data and graphes on the account @covidtracker_fr

# importing the module 

import france_data_management as data
import math
from datetime import datetime
import locale
import tweepy
import pandas as pd
import secrets as s
from datetime import timedelta
PATH = "../../"

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

"""
Secrets :
    consumer_key ="xxxxxxxxxxxxxxxx"
    consumer_secret ="xxxxxxxxxxxxxxxx"
    access_token ="xxxxxxxxxxxxxxxx"
    access_token_secret ="xxxxxxxxxxxxxxxx"
"""

# authentication 
auth = tweepy.OAuthHandler(s.consumer_key, s.consumer_secret) 
auth.set_access_token(s.access_token, s.access_token_secret) 

api = tweepy.API(auth) 
    
def tweet_france_maps():
    _, _, dates, _, _, _, _, df_incid, _ = data.import_data()
    df_incid = df_incid[df_incid["cl_age90"] == 0]
    
    lastday_df_incid = datetime.strptime(df_incid['jour'].max(), '%Y-%m-%d')
    
    ## TWEET2
    df_incid_lastday = df_incid.loc[df_incid['jour']==df_incid['jour'].max(), :]
    nb_dep = len(df_incid_lastday.loc[df_incid_lastday['incidence_color']=='Alerte', :]) + len(df_incid_lastday.loc[df_incid_lastday['incidence_color']=='Alerte Renforcée', :]) + len(df_incid_lastday.loc[df_incid_lastday['incidence_color']=='Alerte Maximale', :])
    
    images_path2 =[PATH+"images/charts/france/dep-map-incid-cat/latest.jpeg"]
    media_ids2 = []
    
    for filename in images_path2:
        res = api.media_upload(filename)
        media_ids2.append(res.media_id)
        
    tweet2 = "🔴 {} départements devraient être classés rouge, car ils dépassent le niveau d'alerte de 50 cas pour 100 000 habitants en 7 jours (données du {})\n➡️ Plus d'infos : covidtracker.fr/covidtracker-france".format(nb_dep, lastday_df_incid.strftime('%d/%m'))
    api.update_status(status=tweet2, media_ids=media_ids2)
    #print(tweet2)
    
tweet_france_maps()

