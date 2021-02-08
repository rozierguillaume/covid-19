#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.covidtracker.fr
Mail : guillaume.rozier@telecomnancy.net

README:
This file contains scripts that download data from data.gouv.fr and then process it to build many graphes.
I'm currently cleaning the code, please ask me if something is not clear enough.

The charts are exported to 'charts/images/france'.
Data is download to/imported from 'data/france'.
Requirements: please see the imports below (use pip3 to install them).

"""


# In[4]:


import pandas as pd
import plotly.graph_objects as go
import france_data_management as data
from datetime import datetime
from datetime import timedelta
from plotly.subplots import make_subplots
import plotly
import math
import os
import json
PATH = "../../"
PATH_STATS = "../../data/france/stats/"

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


# In[8]:


def import_df_age():
    df = pd.read_csv(PATH+"data/france/vaccin/vacsi-a-fra.csv", sep=";")
    return df


# In[66]:


df = import_df_age()
df["n_dose1"] = df["n_dose1"].replace({",": ""}, regex=True).astype("int")
df = df.groupby(["clage_vacsi"]).sum()/100
df = df[1:]
df["n_dose1_pourcent"] = round(df.n_dose1/df.n_dose1.sum()*100, 1)

clage_vacsi = [24, 29, 39, 49, 59, 64, 69, 74, 79, 80]
nb_pop = [5236809, 3593713, 8034961, 8316050, 8494520, 3979481, 3801413, 3404034, 2165960, 4081928]
df_age = pd.DataFrame()
df_age["clage_vacsi"]=clage_vacsi
df_age["nb_pop"]=nb_pop

df = df.merge(df_age, left_on="clage_vacsi", right_on="clage_vacsi")
df["pop_vac"] = df["n_dose1"]/df["nb_pop"]*100
df


# In[73]:


fig = go.Figure()
fig.add_trace(go.Bar(
    x=[str(age) + " ans" for age in df.clage_vacsi[:-1]]+["+ 80 ans"],
    y=df.pop_vac,
    text=[str(round(prct, 2)) + " %" for prct in df.pop_vac],
    textposition='auto',))
fig.update_layout(
    title={
                    'text': "% de population ayant reçu au moins 1 dose de vaccin",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
    annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime("2021-01-27", '%Y-%m-%d').strftime('%d %b')),                    
                        showarrow = False
                    ),
                    ]
)
fig.update_yaxes(range=[0, 100])
fig.show()


# In[63]:


fig = go.Figure()
fig.add_trace(go.Pie(
    labels=[str(age) + " ans" for age in df.index[:-1]]+["+ 80 ans"],
    values=df.n_dose1_pourcent,
    text=[str(prct) + "" for prct in df.n_dose1],
    textposition='auto',))
fig.update_layout(
    title={
                    'text': "Nombre de vaccinés par tranche d'âge",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
    annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime("2021-01-27", '%Y-%m-%d').strftime('%d %b')),                    
                        showarrow = False
                    ),
                    ]
)
fig.show()

