#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
LICENSE MIT
2021
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


# In[83]:


import pandas as pd
import plotly.graph_objects as go
import france_data_management as data
import math
PATH = '../../'


# In[1]:


stations = {
    "07005": {"departement": "80"},
    "07015": {"departement": "59"},
    "07020": {"departement": "50"},
    "07027": {"departement": "14"},
    "07037": {"departement": "76"},
    "07072": {"departement": "51"},
    "07110": {"departement": "29"},
    "07117": {"departement": "22"},
    "07130": {"departement": "35"},
    "07139": {"departement": "61"},
    "07149": {"departement": "94"},
    "07168": {"departement": "10"},
    "07181": {"departement": "54"},
    "07190": {"departement": "67"},
    "07222": {"departement": "44"},
    "07240": {"departement": "37"},
    "07255": {"departement": "18"},
    "07280": {"departement": "21"},
    "07299": {"departement": "68"},
    "07335": {"departement": "86"},
    "07434": {"departement": "87"},
    "07460": {"departement": "63"},
    "07471": {"departement": "43"},
    "07481": {"departement": "69"},
    "07510": {"departement": "33"},
    "07535": {"departement": "46"},
    "07558": {"departement": "12"},
    "07577": {"departement": "26"},
    "07591": {"departement": "05"},
    "07607": {"departement": "40"},
    "07621": {"departement": "65"},
    "07627": {"departement": "09"},
    "07630": {"departement": "31"},
    "07643": {"departement": "34"},
    "07650": {"departement": "13"},
    "07661": {"departement": "33"},
    "07690": {"departement": "06"},
    "07747": {"departement": "66"},
    "07761": {"departement": "2A"},
    "07790": {"departement": "2B"},
}


# In[10]:


df_202101 = pd.read_csv(PATH+"data/france/meteo/synop.202101.csv", sep=";")
df_202101 = df_202101[df_202101.numer_sta.isin(stations)]


# In[69]:


def calculer_iptcc(t_list, rh_list):
    iptcc_list = []
    for i in range(len(t_list)):
        T, RH = t_list[i], rh_list[i]
        AH_num = 6.112 * math.exp(17.67 * T / (T+243.5)) * RH * 2.1674 
        AH_den = 273.15 + T
        AH = AH_num / AH_den

        contenu_exp = (T-7.5)**2/196 + (RH-75)**2/625 + (AH-6)**2/2.89
        IPTCC = 100 * math.exp(-0.5 * contenu_exp)
        iptcc_list += [IPTCC]

    return iptcc_list


# In[78]:


import numpy as np

df_202101["t_degre"] = df_202101["t"].replace("mq", np.nan).astype(float) - 273.15
df_202101["u_pourcent"] = df_202101["u"].replace("mq", np.nan).astype(float)
df_202101_groupby = df_202101.groupby("date").mean().reset_index()
df_202101_groupby["date"] = pd.to_datetime(df_202101_groupby["date"], format="%Y%m%d%H0000")
df_202101_groupby["iptcc"] = calculer_iptcc(df_202101_groupby["t_degre"].values, df_202101_groupby["u_pourcent"].values)


# In[87]:


df_vue_ensemble = data.import_data_vue_ensemble()


# In[91]:


fig=go.Figure()
fig.add_trace(go.Scatter(
    x=df_202101_groupby.date,
    y=df_202101_groupby.u_pourcent.rolling(window=7).mean(),
    name="humidite"
))
fig.add_trace(go.Scatter(
    x=df_202101_groupby.date,
    y=df_202101_groupby.t_degre.rolling(window=7).mean(),
    name="temp"
))
fig.add_trace(go.Scatter(
    x=df_202101_groupby.date,
    y=df_202101_groupby.iptcc.rolling(window=7).mean(),
    name="iptcc"
))
fig.add_trace(go.Scatter(
    x=df_vue_ensemble.date,
    y=df_vue_ensemble.total_cas_confirmes.diff().rolling(window=7).mean()/500,
    name="cas"
))

