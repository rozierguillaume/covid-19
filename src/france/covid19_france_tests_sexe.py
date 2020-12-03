#!/usr/bin/env python
# coding: utf-8

# In[48]:


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


# In[49]:


from multiprocessing import Pool
import requests
import pandas as pd
import math
import plotly.graph_objects as go
import plotly.express as px
import plotly
from plotly.subplots import make_subplots
from datetime import datetime
from datetime import timedelta
from tqdm import tqdm
import imageio
import json
import locale
import france_data_management as data
import numpy as np
import cv2

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
colors = px.colors.qualitative.D3 + plotly.colors.DEFAULT_PLOTLY_COLORS + px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet
show_charts = False
PATH = "data/france/stats/"
now = datetime.now()


# In[50]:


data.download_data()


# In[56]:


df = data.import_data_tests_sexe()


# In[58]:


for (val, valname, title) in [('p', 'positifs', ' cas positifs '), ('t', 'tests', ' tests réalisés ')]:
    fig = go.Figure()
    df_hommes = df[val+"_h"].rolling(window=14).mean()
    df_femmes = df[val+"_f"].rolling(window=14).mean()

    fig.add_trace(go.Scatter(
        x=df['jour'] , y=df_femmes,
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[0]),
        stackgroup='one',
        fillcolor="rgba(227, 136, 225, 0.7)",
        groupnorm='percent', # sets the normalization for the sum of the stackgroup,
        name="Femmes<br>" + str(round(df_femmes.values[-1]/(df_femmes.values[-1]+df_hommes.values[-1])*100, 1)) + " %"
    ))
    fig.add_trace(go.Scatter(
        x=df['jour'] , y=df_hommes,
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[1]),
        fillcolor="rgba(66, 135, 245, 0.7)",
        stackgroup='one',
        name="Hommes<br>" + str(round(df_hommes.values[-1]/(df_femmes.values[-1]+df_hommes.values[-1])*100, 1)) + " %"
    ))

    fig.add_shape(
                type="line",
                x0=df["jour"].min(),
                y0=50,
                x1=df["jour"].max(),
                y1=50,
                opacity=1,
                fillcolor="black",
                line=dict(
                    dash="dot",
                    color="black",
                    width=1,
                )
            )


    fig.update_layout(
        annotations = [
                    dict(
                        x=0,
                        y=1.05,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(""), #datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')
                        showarrow = False
                    )],
        margin=dict(
                    l=20,
                    r=100,
                    b=20,
                    t=65,
                    pad=0
                ),
        showlegend=True,
         title={
                'text': "Répartition des{}en fonction du sexe".format(title),
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        xaxis=dict(
            tickformat='%d/%m',
            nticks=25),
        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%'))

    #fig.show()
    name_fig = "repartition_age_sexe{}".format(valname)
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

