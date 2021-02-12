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
PATH = '../../'
from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


# In[3]:


data.download_data()
data.download_data_hosp_fra_clage()


# In[4]:


df_a_vacsi_a_france = data.import_data_vacsi_a_fra()
df_hosp_fra_clage = data.import_data_hosp_fra_clage()


# In[ ]:


df_hosp_fra_clage


# In[ ]:


df_a_vacsi_a_france


# In[ ]:


df_a_vacsi_a_france_80 = df_a_vacsi_a_france[df_a_vacsi_a_france.clage_vacsi==80]
df_hosp_fra_clage_80 = df_hosp_fra_clage[df_hosp_fra_clage.cl_age90 >= 89].groupby(["jour"]).sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_hosp_fra_clage_80.jour,
    y=df_hosp_fra_clage_80.dc.diff().rolling(window=7).mean(),
    showlegend=False,
    line=dict(color="red", width=4)
))

fig.add_trace(go.Scatter(
    x=df_a_vacsi_a_france_80.jour,
    y=df_a_vacsi_a_france_80.n_cum_dose1/4156974*100,
    line=dict(width=4, color="#1f77b4"),
    showlegend=False,
    yaxis="y2"
))

fig.update_layout(
    title=dict(
        y=0.90, x=0.5,
        font = dict(
                size=20, color="black"),
        text="<b>[Plus de 80 ans] <span style='color:red;'>décès hospitaliers</span> et <span style='color:#1f77b4;'>vaccinations</span></b>"),
    
    yaxis=dict(
        title="<b>Décès hospitaliers</b>",
        titlefont=dict(
            color="red"
        ),
        tickfont=dict(
            color="red"
        )
    ),
    yaxis2=dict(
            range=[0, 100],
            title="<b>% vaccinés</b> (au moins 1 dose)",
            titlefont=dict(
                color="#1f77b4"
            ),
            ticksuffix=" %",
            tickfont=dict(
                color="#1f77b4"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=1
        ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    font=dict(color="black"),
                    text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier covidtracker.fr.'.format(datetime.strptime(max(df_hosp_fra_clage_80.jour), '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)


# In[ ]:


df_a_vacsi_a_france_80 = df_a_vacsi_a_france[df_a_vacsi_a_france.clage_vacsi!=80].groupby(["jour"]).sum().reset_index()
df_hosp_fra_clage_80 = df_hosp_fra_clage[df_hosp_fra_clage.cl_age90 < 89].groupby(["jour"]).sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_hosp_fra_clage_80.jour,
    y=df_hosp_fra_clage_80.dc.diff().rolling(window=7).mean(),
    showlegend=False,
    line=dict(color="red", width=4)
))

fig.add_trace(go.Scatter(
    x=df_a_vacsi_a_france_80.jour,
    y=df_a_vacsi_a_france_80.n_cum_dose1/(66990000-4156974)*100,
    line=dict(width=4, color="#1f77b4"),
    showlegend=False,
    yaxis="y2"
))

fig.update_layout(
    title=dict(
        y=0.90, x=0.5,
        font = dict(
                size=20, color="black"),
        text="<b>[0 - 79 ans] <span style='color:red;'>décès hospitaliers</span> et <span style='color:#1f77b4;'>vaccinations</span></b>"),
    
    yaxis=dict(
        title="<b>Décès hospitaliers</b>",
        titlefont=dict(
            color="red"
        ),
        tickfont=dict(
            color="red"
        )
    ),
    yaxis2=dict(
            range=[0, 100],
            title="<b>% vaccinés</b> (au moins 1 dose)",
            titlefont=dict(
                color="#1f77b4"
            ),
            ticksuffix=" %",
            tickfont=dict(
                color="#1f77b4"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=1
        ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    font=dict(color="black"),
                    text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier covidtracker.fr.'.format(datetime.strptime(max(df_hosp_fra_clage_80.jour), '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)


# In[ ]:


df_a_vacsi_a_france.clage_vacsi.unique()

