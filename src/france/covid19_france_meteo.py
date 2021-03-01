#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


import pandas as pd
import plotly.graph_objects as go
import france_data_management as data
import math
PATH = '../../'


# In[3]:


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


# In[44]:





# In[5]:


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


# In[56]:


import numpy as np
def import_data_mois_meteo(date):
    df_meteo = pd.read_csv(PATH+"data/france/meteo/synop.{}.csv".format(date), sep=";")
    df_meteo = df_meteo[df_meteo.numer_sta.isin(stations)]

    df_meteo["t_degre"] = df_meteo["t"].replace("mq", np.nan).astype(float) - 273.15
    df_meteo["u_pourcent"] = df_meteo["u"].replace("mq", np.nan).astype(float)
    df_meteo_groupby = df_meteo.groupby("date").mean().reset_index()
    df_meteo_groupby["date"] = pd.to_datetime(df_meteo_groupby["date"], format="%Y%m%d%H0000")
    #df_meteo_groupby["iptcc"] = calculer_iptcc(df_meteo_groupby["t_degre"].values, df_meteo_groupby["u_pourcent"].values)
    return df_meteo_groupby


# In[76]:


def merge_df_meteo(df1, df2):
    df_merge = df1.merge(df2, left_on="date", right_on="date", how="outer").fillna(0)

    df_final = pd.DataFrame()
    df_final["date"] = df_merge.date
    df_final["u_pourcent"] = df_merge["u_pourcent_x"] + df_merge["u_pourcent_y"]
    df_final["t_degre"] = df_merge["t_degre_x"] + df_merge["t_degre_y"]
    return df_final


# In[89]:


df1 = import_data_mois_meteo("202008")
df2 = import_data_mois_meteo("202009")

df1 = merge_df_meteo(df1, df2)
df2 = import_data_mois_meteo("202010")

df1 = merge_df_meteo(df1, df2)
df2 = import_data_mois_meteo("202011")

df1 = merge_df_meteo(df1, df2)
df2 = import_data_mois_meteo("202012")

df1 = merge_df_meteo(df1, df2)
df2 = import_data_mois_meteo("202101")

df1 = merge_df_meteo(df1, df2)
df2 = import_data_mois_meteo("202102")

df_meteo_groupby = merge_df_meteo(df1, df2)
df_meteo_groupby["iptcc"] = calculer_iptcc(df_meteo_groupby["t_degre"].values, df_meteo_groupby["u_pourcent"].values)


# In[23]:


df_vue_ensemble = data.import_data_vue_ensemble()
df_new = data.import_data_new()
df_new_france = df_new.groupby("jour").sum().reset_index()
df_new_france["r_incid_hosp"] = df_new_france["incid_hosp"]/df_new_france["incid_hosp"].shift(7)


# In[ ]:


##### fig=go.Figure()
fig.add_trace(go.Scatter(
    x=df_meteo_groupby.date,
    y=df_meteo_groupby.u_pourcent.rolling(window=14, center=True).mean(),
    name="humidite"
))
fig.add_trace(go.Scatter(
    x=df_meteo_groupby.date,
    y=df_meteo_groupby.t_degre.rolling(window=14, center=True).mean(),
    name="temp",
    yaxis="y2"
))
fig.add_trace(go.Scatter(
    x=df_meteo_groupby.date,
    y=df_meteo_groupby.iptcc.rolling(window=7, center=True).mean(),
    name="iptcc",
    yaxis="y3"
))
fig.add_trace(go.Scatter(
    x=df_new_france.jour,
    y=df_new_france.r_incid_hosp.rolling(window=7, center=True).mean().shift(12),
    name="R adm hosp (J+10)",
    yaxis="y4"
))

fig.update_layout(
    yaxis2=dict(
            title="yaxis2 title",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.15
        ),
    yaxis3=dict(
            title="yaxis2 title",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            #anchor="free",
            overlaying="y",
            side="right",
            position=1
        ),
    yaxis4=dict(
            title="yaxis2 title",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            #anchor="free",
            overlaying="y",
            side="right",
            position=0.95
        ),
)

