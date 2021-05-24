#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.guillaumerozier.fr
Mail : guillaume.rozier@telecomnancy.net

README:s
This file contains script that generate France maps and GIFs. 
Single images are exported to folders in 'charts/image/france'. GIFs are exported to 'charts/image/france'.
I'm currently cleaning this file, please ask me is something is not clear enough!
Requirements: please see the imports below (use pip3 to install them).

"""


# In[2]:


from multiprocessing import Pool
import requests
import cv2
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
import plotly.figure_factory as ff
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
now = datetime.now()
PATH = "../../"


# In[11]:


df_metro = data.import_data_metropoles()
df_metro_65 = df_metro[df_metro["clage_65"] == 65]
df_metro_0 = df_metro[df_metro["clage_65"] == 0]
nb_last_days=40


# In[14]:


metropoles = df_metro_0[df_metro_0["semaine_glissante"]==df_metro_0["semaine_glissante"].max()].sort_values(by=["ti"], ascending=False)["Metropole"].values
metropoles_couvre_feu = ["Paris", "Saint Etienne", "Grenoble", "Montpellier", "Rouen", "Toulouse", "Lille", "Lyon", "Marseille"]
metropoles_couvre_feu_sorted = [m for m in metropoles if m in metropoles_couvre_feu]


# In[15]:



fig=go.Figure()

for i,metro in enumerate(metropoles_couvre_feu_sorted): #list(dict.fromkeys(list(df_metro['Metropole'].values))
    
    y=df_metro_0[df_metro_0["Metropole"]==metro]
    y=y[len(y)-nb_last_days:]
    
    fig.add_trace(go.Scatter(
            x = [d[-10:] for d in y["semaine_glissante"].values],
            y = y["ti"],
            name = str(i+1) + ".<b> " + metro + "</b>" + "<br> Incidence : " + str(math.trunc(y["ti"].values[-1])) + "",
            line_width=5,
            marker_size=10,
            mode="markers+lines",
            opacity=1))
    fig.update_yaxes(range=[0, df_metro_0["ti"].max()])
    
    fig.update_layout(
        
        title={
            'text': "<b>Taux d'incidence du Covid19 dans les métropoles [avec couvre-feu le 17/10]<br></b>{}, nombre de cas sur 7 j. pour 100k. hab.".format("covidtracker.fr"),
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
                size=20),
    )
    
    
name_fig = "line_metropole_avec_couvre_feu"
fig.write_image(PATH+"images/charts/france/{}.jpeg".format(name_fig), scale=2, width=800, height=800)

plotly.offline.plot(fig, filename = PATH+'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[16]:



fig=go.Figure()

metropoles = df_metro_0[df_metro_0["semaine_glissante"]==df_metro_0["semaine_glissante"].max()].sort_values(by=["ti"], ascending=False)["Metropole"].values

for i,metro in enumerate([m for m in metropoles if m not in metropoles_couvre_feu]): #list(dict.fromkeys(list(df_metro['Metropole'].values))
    
    y=df_metro_0[df_metro_0["Metropole"]==metro]
    #y=y[len(y)-nb_last_days:]
                 
    fig.add_trace(go.Scatter(
            x = [d[-10:] for d in y["semaine_glissante"].values],
            y = y["ti"],
            name = str(i+1) + ".<b> " + metro + "</b>" + "<br> Incidence : " + str(math.trunc(y["ti"].values[-1])) + "",
            line_width=5,
            marker_size=10,
            mode="markers+lines",
            opacity=1))
    
    fig.update_yaxes(range=[0, df_metro_0["ti"].max()])
    
    fig.update_layout(
        
        title={
            'text': "<b>Taux d'incidence du Covid19 dans les métropoles <b>[sans couvre-feu le 17/10]</b><br></b>{}, nombre de cas sur 7 j. pour 100k. hab.".format("covidtracker.fr"),
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
                size=20),
    )
    
    
name_fig = "line_metropoles_sans_couvre_feu"
fig.write_image(PATH+"images/charts/france/{}.jpeg".format(name_fig), scale=2, width=800, height=800)

plotly.offline.plot(fig, filename = PATH+'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[17]:


im1 = cv2.imread(PATH+'images/charts/france/line_metropole_avec_couvre_feu.jpeg')
im2 = cv2.imread(PATH+'images/charts/france/line_metropoles_sans_couvre_feu.jpeg')

im3 = cv2.hconcat([im1, im2])

cv2.imwrite(PATH+'images/charts/france/line_metropoles_comp_couvre_feu.jpeg', im3)


# In[18]:


nb_last_days=25
for (title, df_temp, name) in [("Tous âges", df_metro_0, "0"), ("> 65 ans", df_metro_65, "65")]:
    metros = list(dict.fromkeys(list(df_temp['Metropole'].values)))
    metros_ordered = df_temp[df_temp['semaine_glissante'] == df_temp['semaine_glissante'].max()].sort_values(by=["ti"], ascending=True)["Metropole"].values
    dates_heatmap = list(dict.fromkeys(list(df_temp['semaine_glissante'].values))) 
    
    array_incidence=[]
    
    for idx, metro in enumerate(metros_ordered): #deps_tests.drop("975", "976", "977", "978")
        values = df_temp[df_temp["Metropole"] == metro]['ti'].values.astype(int)
        values = values[len(values)-nb_last_days:]
        array_incidence += [values]
        #dates_heatmap=df_metro[df_metro["Metropole"] == metro]["semaine_glissante"].values.astype(str)
        
    fig = ff.create_annotated_heatmap(
        z=array_incidence, #df_tests_rolling[data].to_numpy()
        x=[("<b>" + a[-2:] + "/" + a[-5:-3] + "</b>") for a in dates_heatmap[-nb_last_days:]], #date[:10] for date in dates_heatmap
        y=[str(22-idx) + ". <b>" + metro[:9] +"</b>" for idx, metro in enumerate(metros_ordered)],
        showscale=True,
        font_colors=["white", "white"],
        coloraxis="coloraxis",
        #text=df_tests_rolling[data],
        #annotation_text = array_incidence
        )

    annot = []

    fig.update_xaxes(side="bottom", tickfont=dict(size=10))
    fig.update_yaxes(tickfont=dict(size=15))

    fig.update_layout(
        
        title={
            'text': "<b>Taux d'incidence du Covid19 dans les 22 métropoles<br>{}</b>, nombre de cas sur 7 j. pour 100k. hab.".format(title),
            'y':0.97,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
            size=20),
        coloraxis=dict(
            cmin=0, cmax=800,
            colorscale = [[0, "green"], [0.08, "#ffcc66"], [0.25, "#f50000"], [0.5, "#b30000"], [1, "#3d0000"]],
            #color_continuous_scale=["green", "red"],
            colorbar=dict(
                #title="{}<br>du Covid19<br> &#8205;".format(title),
                thicknessmode="pixels", thickness=12,
                lenmode="pixels", len=300,
                yanchor="middle", y=0.5,
                tickfont=dict(size=9),
                ticks="outside", ticksuffix="{}".format(" cas"),
                )
        ),
    margin=dict(
            l=0,
            r=0,
            b=70,
            t=70,
            pad=0
        ),
    )

    annotations = annot + [
                    dict(
                        x=0.5,
                        y=-0.08,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        opacity=0.6,
                        font=dict(color="black", size=12),
                        text='Lecture : une case correspond à l\'incidence pour chaque métropole (à lire à gauche) et à une date donnée (à lire en bas).<br>Du rouge correspond à une incidence élevée.  <i>Date : {} - Source : covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                        showarrow = False
                    ),
                ]

    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 10
        fig.layout.annotations[i].text = "<b>"+fig.layout.annotations[i].text+"</b>"

    for annot in annotations:
        fig.add_annotation(annot)

    name_fig = "heatmaps_metropoles_" + name
    fig.write_image(PATH+"images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1000, height=1000)
    fig.write_image(PATH+"images/charts/france/{}_SD.jpeg".format(name_fig), scale=0.5, width=900, height=900)
    #fig.show()
    plotly.offline.plot(fig, filename = PATH+'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

