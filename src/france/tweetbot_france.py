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
    
def tweet_france():
    data.download_data()
    
    df_incid_fra_clage = data.import_data_tests_sexe()
    df_incid_france = df_incid_fra_clage[df_incid_fra_clage["cl_age90"]==0]
    
    df_new = data.import_data_new()
    df_new_france = df_new.groupby("jour").sum().reset_index()
    
    df = data.import_data_df()
    dates = sorted(list(dict.fromkeys(list(df['jour'].values))))
    ###
    
    lastday_df_new = datetime.strptime(df_new_france['jour'].max(), '%Y-%m-%d')
    
    hosp = df_new_france[df_new_france['jour']==lastday_df_new.strftime('%Y-%m-%d')]['incid_hosp'].values[-1]
    date_j7 = (lastday_df_new - timedelta(days=7)).strftime("%Y-%m-%d")
    hosp_j7 = df_new_france[df_new_france['jour'] == date_j7]['incid_hosp'].values[-1]
    
    
    deaths = df_new_france[df_new_france['jour']==lastday_df_new.strftime('%Y-%m-%d')]['incid_dc'].values[-1]
    deaths_j7 = df_new_france[df_new_france['jour'] == date_j7]['incid_dc'].values[-1]
    
    lastday_df_incid = datetime.strptime(df_incid_france['jour'].max(), '%Y-%m-%d')
    tests = df_incid_france[df_incid_france['jour']==lastday_df_incid.strftime('%Y-%m-%d')]['P'].values[-1]
    depistage = df_incid_france[df_incid_france['jour']==lastday_df_incid.strftime('%Y-%m-%d')]['T'].values[-1]
    
    date_j7_incid = (lastday_df_incid - timedelta(days=7)).strftime("%Y-%m-%d")
    tests_j7 = df_incid_france[df_incid_france['jour'] == date_j7_incid]['P'].values[-1]
    
    depistage_j7 = df_incid_france[df_incid_france['jour'] == date_j7_incid]['T'].values[-1]
    
    date = datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B')
    
    hosp_tendance, hosp_sign = "en hausse", "+"
    if hosp_j7>hosp:
        hosp_tendance, hosp_sign = "en baisse", ""
    if hosp_j7==hosp:
        hosp_tendance, hosp_sign = "stable", "+"
        
    deaths_tendance, deaths_sign = "en hausse", "+"
    if deaths_j7>deaths:
        deaths_tendance, deaths_sign = "en baisse", ""
    if deaths_j7==deaths:
        deaths_tendance, deaths_sign = "stable", "+"
        
    tests_tendance, tests_sign = "en hausse", "+"
    if tests_j7>tests:
        tests_tendance, tests_sign = "en baisse", ""
    if tests_j7==tests:
        tests_tendance, tests_sign = "stable", "+"
        
    date_incid = datetime.strptime(sorted(list(dict.fromkeys(list(df_incid_france['jour'].values))))[-1], '%Y-%m-%d').strftime('%d %B')
    tweet ="Chiffres #Covid19 :\n• {} personnes décédées en milieu hosp. ({}), {} sur 7 j. ({}{})\n• {} admissions à l'hôpital ({}), {} sur 7 j. ({}{})\n• {} cas positifs ({}), {} sur 7 j. ({}{})\n➡️ + d'infos : covidtracker.fr".format(deaths, lastday_df_new.strftime('%d/%m'), deaths_tendance, deaths_sign, deaths-deaths_j7, hosp, lastday_df_new.strftime('%d/%m'), hosp_tendance, hosp_sign, hosp-hosp_j7, tests, lastday_df_incid.strftime('%d/%m'), tests_tendance, tests_sign, tests-tests_j7) # toDo 
    
    images_path =[PATH+"images/charts/france/dashboard_jour.jpeg", PATH+"images/charts/france/heatmap_incidence.jpeg"]
    media_ids = []
    
    for filename in images_path:
        res = api.media_upload(filename)
        media_ids.append(res.media_id)

    # to attach the media file 
    api.update_status(status=tweet, media_ids=media_ids)
    print(tweet)
    print(tests)
    print(depistage_j7)
    
tweet_france()

