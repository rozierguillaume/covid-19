#!/usr/bin/env python
# coding: utf-8

# In[3]:


# Guillaume Rozier - 2020 - MIT License
# This script will automatically tweet new data and graphes on the account @covidtracker_fr

# importing the module 

import math
from datetime import datetime
import locale
import tweepy
import json
import pandas as pd
import secrets as s
from datetime import timedelta

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

PATH = "../../"

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

def tweet_world():
    # Import data
    df_confirmed_csse = pd.read_csv(PATH+'data/total_cases_csse.csv')
    df_deaths_csse = pd.read_csv(PATH+'data/total_deaths_csse.csv')
    
    df_confirmed = pd.read_csv(PATH+'data/data_confirmed.csv')
    df_deaths = pd.read_csv(PATH+'data/data_deaths.csv')
    
    # Compute diff to get daily data
    df_confirmed_diff = df_confirmed.copy()
    df_confirmed_diff.loc[:, df_confirmed.columns != 'date'] = df_confirmed.loc[:, df_confirmed.columns != 'date'] .diff()

    df_deaths_diff = df_deaths.copy()
    df_deaths_diff.loc[:, df_deaths.columns != 'date'] = df_deaths.loc[:, df_deaths.columns != 'date'] .diff()
    
    # Get only last day
    date = max(df_confirmed["date"])
    date_str = datetime.strptime(date, '%Y-%m-%d').strftime('%d %B')

    df_confirmed_lastd = df_confirmed[df_confirmed["date"] == date]
    df_confirmed_diff_lastd = df_confirmed_diff[df_confirmed_diff["date"] == date]

    df_deaths_lastd = df_deaths[df_deaths["date"] == date]
    df_deaths_diff_lastd = df_deaths_diff[df_deaths_diff["date"] == date]
    
    # Get results
    sum_cases = math.trunc(df_confirmed_lastd.sum(axis=1).values[0])
    new_cases = math.trunc(df_confirmed_diff_lastd.sum(axis=1).values[0])

    sum_deaths = math.trunc(df_deaths_lastd.sum(axis=1).values[0])
    new_deaths = math.trunc(df_deaths_diff_lastd.sum(axis=1).values[0])
    
    new_cases_string = f"{new_cases:,d}".replace(',', ' ')
    sum_cases_string = f"{sum_cases:,d}".replace(',', ' ')
    new_deaths_string = f"{new_deaths:,d}".replace(',', ' ')
    sum_deaths_string = f"{sum_deaths:,d}".replace(',', ' ')
    
    # Write and publish tweet
    tweet ="Données du #Covid19 dans le monde au {} :\n+ {} cas en 24h, soit {} au total\n+ {} décès en 24h, soit {} au total\n➡️ Plus d'infos : covidtracker.fr/covidtracker-world\n".format(date_str, new_cases_string, sum_cases_string, new_deaths_string, sum_deaths_string) # toDo 
    #image_path ="images/charts/cases_world.jpeg"
    
    images_path =[PATH+"images/charts/cases_world.jpeg", PATH+"images/charts/deaths_world.jpeg"]
    media_ids = []
    
    for filename in images_path:
        res = api.media_upload(filename)
        media_ids.append(res.media_id)

    # to attach the media file 
    api.update_status(status=tweet, media_ids=media_ids)
    #print(tweet)
    
    return date_str, new_cases_string, sum_cases_string, new_deaths_string, sum_deaths_string 
    
date_str, new_cases_string, sum_cases_string, new_deaths_string, sum_deaths_string  = tweet_world()


# In[4]:


PATH_stats = PATH+"data/stats/"

def traitement_val(valeur, plus_sign=False):
    if int(valeur)<0:
        valeur = "--"
        
    if len(valeur)>3:
        valeur = valeur[:len(valeur)-3] + " " + valeur[-3:]

    return valeur

data_json = {}
for val, name in [(new_cases_string, "new_cases"), (sum_cases_string, "sum_cases"), (new_deaths_string, "new_deaths"), (sum_deaths_string, "sum_deaths")]:
    
    dict_json = {}
    dict_json["date"] = date_str
    
    dict_json["valeur"] = val
    
    if (int(val.replace(" ", "")) > 0) & ("new" in name):
        dict_json["valeur"] = "+ " + dict_json["valeur"]
    
    data_json[name] = dict_json
    
    
with open(PATH_stats + 'stats.json', 'w') as outfile:
    json.dump(data_json, outfile)

