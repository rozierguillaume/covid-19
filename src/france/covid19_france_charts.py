#!/usr/bin/env python
# coding: utf-8

# # COVID-19 French Charts
# Guillaume Rozier, 2020

# In[1]:


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


# In[2]:


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
PATH_STATS = "../../data/france/stats/"
PATH = "../../"
now = datetime.now()


# In[3]:


try:
    #import subprocess
    #subprocess.run(["pip3", "install", "scikit-learn"])
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import make_pipeline

except:
    pass


# # Data download and import

# In[4]:


import time

success=False
tries = 0

while not success:
    try:
        data.download_data()
        success=True
    except Exception as e:
        print(e)
        time.sleep(20)
        print('retrying in 20s')
        tries += 1
        
        if tries >= 200:
            success=True
        continue


# ## Data transformations

# In[5]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[6]:


df_new_france = df_new.groupby(["jour"]).sum().reset_index()

df_clage = data.import_data_hosp_clage()
df_clage_france = df_clage.groupby(["jour", "cl_age90"]).sum().reset_index()

df_incid = df_incid[df_incid["cl_age90"] == 0]

df_incid_france = df_incid.groupby("jour").sum().reset_index()
dates_clage = list(dict.fromkeys(list(df_clage_france['jour'].values))) 

df_sursaud_france = df_sursaud.groupby(['date_de_passage']).sum().reset_index()
df_sursaud_france["taux_covid"] = df_sursaud_france["nbre_pass_corona"] / df_sursaud_france["nbre_pass_tot"]
df_sursaud_france["taux_covid_acte"] = df_sursaud_france["nbre_acte_corona"] / df_sursaud_france["nbre_acte_tot"]
dates_sursaud = list(dict.fromkeys(list(df_sursaud['date_de_passage'].values))) 

dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 
date_plus_1 = (datetime.strptime(dates_incid[-1], '%Y-%m-%d') + timedelta(days=2)).strftime('%Y-%m-%d')

departements = list(dict.fromkeys(list(df_incid['dep'].values))) 

last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")
last_day_plot_dashboard = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=14)).strftime("%Y-%m-%d")

df_region = df.groupby(['regionName', 'jour', 'regionPopulation']).sum().reset_index()
df_region["hosp_regpop"] = df_region["hosp"] / df_region["regionPopulation"]*1000000 
df_region["rea_regpop"] = df_region["rea"] / df_region["regionPopulation"]*1000000 

df_tests_tot = df_tests.groupby(['jour']).sum().reset_index()

df_new_region = df_new.groupby(['regionName', 'jour']).sum().reset_index()
df_france = df.groupby('jour').sum().reset_index()

regions = list(dict.fromkeys(list(df['regionName'].values))) 
departements_noms = list(dict.fromkeys(list(df['departmentName'].values))) 


# In[7]:


#Calcul sorties de réa
# Dataframe intermédiaire (décalée d'une ligne pour le calcul)
df_new_tot = df_new.groupby(["jour"]).sum().reset_index()
last_row = df_new_tot.iloc[-1]
df_new_tot = df_new_tot.shift()
df_new_tot = df_new_tot.append(last_row, ignore_index=True)

# Nouvelle dataframe contenant le résultat
df_new_tot["incid_dep_rea"] = df_france["rea"] - df_france["rea"].shift() - df_new_tot["incid_rea"]
df_new_tot["incid_dep_hosp_nonrea"] = df_france["hosp_nonrea"] - df_france["hosp_nonrea"].shift() - df_new_tot["incid_hosp_nonrea"].iloc[-1]
# On ne garde que les 19 derniers jours (rien d'intéressant avant)
df_new_tot_last15 = df_new_tot[ df_new_tot["jour"].isin(dates[:]) ]
df_france_last15 = df_france[ df_france["jour"].isin(dates[-19:]) ]
df_tests_tot_last15 = df_tests_tot[ df_tests_tot["jour"].isin(dates[-19:]) ]


# In[8]:


def traitement_val(valeur, plus_sign=False):
    if (int(valeur) > 0) & plus_sign:
        valeur = "+ " + str(abs(int(valeur)))
        
    if ("+" not in valeur):
        if(int(valeur)<0):
            valeur = "- " + str(abs(int(valeur)))
        
    if len(valeur)>3:
        valeur = valeur[:len(valeur)-3] + " " + valeur[-3:]

    return valeur
            
df_france = df.groupby(["jour"]).sum().reset_index()

data_json = {}

#rea et hosp
for val in ["rea", "hosp", "incid_dc", "rea_new", "hosp_new"]:
    if "incid" in val:
        data_temp = df_new_france
    else:
        data_temp = df_france
        
    rea_json = {}
    date = data_temp["jour"].max()
    rea_json["date"] = date[-2:] + "/" + date[-5:-3]
    
    valeur = str(data_temp[val].values[-1].astype(int))
    valeur = traitement_val(valeur, plus_sign=(("new" in val) or ("incid" in val)))
        
        
    rea_json["valeur"] = valeur
    data_json[val] = rea_json
    
    
#####
    
df_tests_viros_france = df_tests_viros[df_tests_viros["cl_age90"]==0].groupby(["jour"]).sum().reset_index()
tests_last7 = traitement_val(str(df_tests_viros_france["P"].values[-7:].sum()), True)

dict_json = {}
date = df_tests_viros_france["jour"].dropna().max()
dict_json["date"] = date[-2:] + "/" + date[-5:-3]
dict_json["valeur"] = str(tests_last7)
data_json["tests_last7"] = dict_json


    
with open(PATH_STATS + 'stats.json', 'w') as outfile:
    json.dump(data_json, outfile)


# In[9]:


def objectif_deconfinement():
    dict_json = {}
    
    struct = {"dates": [], "values": []}
    n = 40
    dict_json["rea"] = struct
    dict_json["rea"]["values"] = [int(x) for x in df_france["rea"].values[-n:]]
    dict_json["rea"]["dates"] = list(df_france["jour"].values[-n:])
    
    struct = {"date": "", "values": []}
    dict_json["cas"] = struct
    cas_rolling = df_incid_france["P"].rolling(window=7, center=False).mean().dropna()
    
    dict_json["cas"]["values"] = [int(x) for x in cas_rolling.values[-n:]]
    dict_json["cas"]["dates"] = list(df_incid_france.loc[cas_rolling.index.values[-n:], "jour"])

    with open(PATH_STATS + 'objectif_deconfinement.json', 'w') as outfile:
        json.dump(dict_json, outfile)
        
objectif_deconfinement()


# In[10]:


def stats_dep_vague(nb_first_values):
    
    departements_noms = list(dict.fromkeys(list(df['departmentName'].values))) 
    
    df_temp = df[["jour", "hosp", "departmentName", "dep"]]

    dict_json = {"date": dates[nb_first_values][-2:]+"/"+dates[nb_first_values][-5:-3], "numeros_departements": {}, "avant_premiere_vague": [], "apres_premiere_vague": [], "data": {}}

    premiere_vague, deuxieme_vague, deps = [], [], []

    for dep in departements_noms:    
        df_dep = df_temp[df_temp["departmentName"] == dep].reset_index()
        df_dep = df_dep[ df_dep["jour"] <= dates[nb_first_values]]
        
        premiere_vague += [df_dep[ df_dep["jour"] < "2020-06"]["hosp"].max()]
        deuxieme_vague += [df_dep[ df_dep["jour"] > "2020-08"]["hosp"].max()]
        deps += [dep]

        dict_json["data"][dep] = {"hosp_max_premiere_vague": str(premiere_vague[-1]), "hosp_actuellement": str(deuxieme_vague[-1])}
        dict_json["numeros_departements"][dep] = df_dep["dep"].values[-1]
        diff_nette = [max(0, hosp - premiere_vague[-1]) for hosp in df_dep["hosp"].values]
        dict_json["data"][dep]["jour_depassement"] = "-/-"

        for idx, val in enumerate(diff_nette):
            if (val > 0) & (idx > 50):
                jour = df_dep["jour"].values[idx]
                dict_json["data"][dep]["jour_depassement"] = jour[-2:]+"/"+jour[-5:-3]
                break

    argsort = np.argsort(deuxieme_vague)
    premiere_vague_sorted = np.array(premiere_vague)[argsort]
    deuxieme_vague_sorted = np.array(deuxieme_vague)[argsort]
    deps_sorted = np.array(deps)[argsort]
    nb_jours_depassement = 0

    for idx, dep in enumerate(deps_sorted):
        if premiere_vague_sorted[idx] > deuxieme_vague_sorted[idx]:
            dict_json["avant_premiere_vague"] += [dep]
        else:
            dict_json["apres_premiere_vague"] += [dep]


    with open(PATH_STATS + 'risk_rates.json', 'w') as outfile:
        json.dump(dict_json, outfile)
        
stats_dep_vague(len(dates)-1)


# In[11]:


def incidence_deps_data():
    departements_noms = list(dict.fromkeys(list(df['departmentName'].values))) 
    dict_json = {"liste_departements": [], "donnees_departements": {}, "donnees_france": {}, "date_donnees": dates_incid[-1][-2:]+"/"+dates_incid[-1][-5:-3], "date_update": dates[-1][-2:]+"/"+dates[-1][-5:-3]}
    
    
    df_temp = df_new[["jour", "incid_dc", "incid_hosp", "incid_rea", "departmentName", "dep", "departmentPopulation"]][ df_new["jour"] >= dates[-7]]
    df_tests_viros_departements = df_tests_viros[(df_tests_viros["jour"] >= dates_incid[-7]) & (df_tests_viros["cl_age90"]==0)].merge(df_temp[["dep", "departmentName"]], left_on="dep", right_on="dep")
    df_tests_viros_departements = df_tests_viros_departements.groupby(["dep", "jour"]).first().reset_index()
    
    for dep in departements_noms:
        data_json = {"incidence_cas": 0, "incidence_hosp": 0, "incidence_dc": 0, "population": 0}
        
        df_dep = df_temp[df_temp["departmentName"] == dep].reset_index()
        df_dep_tests = df_tests_viros_departements[df_tests_viros_departements["departmentName"] == dep].reset_index()
        
        data_json["incidence_cas"] = int(np.round(df_dep_tests["P"].sum()/df_dep_tests["pop"].values[0]*100000))
        data_json["incidence_dc"] = df_dep["incid_dc"].sum()/df_dep["departmentPopulation"].values[0]*100000
        data_json["incidence_hosp"] = df_dep["incid_hosp"].sum()/df_dep["departmentPopulation"].values[0]*100000
        data_json["incidence_rea"] = df_dep["incid_rea"].sum()/df_dep["departmentPopulation"].values[0]*100000
        data_json["population"] = int(df_dep["departmentPopulation"].values[0])
        
        dict_json["donnees_departements"][dep] = data_json
        
    dict_json["liste_departements"] = departements_noms
    
    # France
    df_temp = df_tests_viros_france[df_tests_viros_france["jour"] >= dates_incid[-7]]
    data_json["incidence_cas"] = (df_temp["P"].sum()/df_temp["pop"].values[0]*100000)
    
    df_temp = df_new_france[["jour", "incid_dc", "incid_hosp", "incid_rea", "departmentPopulation"]][ df_new_france["jour"] >= dates[-7]]
    data_json["incidence_dc"] = df_temp["incid_dc"].sum()/df_temp["departmentPopulation"].values[0]*100000
    data_json["incidence_hosp"] = df_temp["incid_hosp"].sum()/df_temp["departmentPopulation"].values[0]*100000
    data_json["incidence_rea"] = df_temp["incid_rea"].sum()/df_temp["departmentPopulation"].values[0]*100000
    dict_json["donnees_france"] = data_json
        
    with open(PATH_STATS + 'incidence_departements.json', 'w') as outfile:
        json.dump(dict_json, outfile)
        
incidence_deps_data()


# In[12]:


"""values = []
dates_temp = []

for i in range(1, 2):
    stats_dep_vague(len(dates)-i)
     
    with open(PATH_STATS + 'risk_rates.json', 'r') as file:
        old_dict = json.loads(file.read())
        values +=  [len(old_dict["apres_premiere_vague"])]
        dates_temp += [old_dict["date"]]
        print(values)
dates_temp
values"""


# In[13]:


"""fig = go.Figure()

fig.add_trace(go.Scatter(
    x = df_incid[df_incid["jour"]==df_incid["jour"].max()]["pop"],
    y = df_incid[df_incid["jour"]==df_incid["jour"].max()]["P"]/df_incid[df_incid["jour"]==df_incid["jour"].max()]["pop"],
    mode="markers+text",
    text=df_incid[df_incid["jour"]==df_incid["jour"].max()]["departmentName"],
    marker_color='black',
    opacity=0.6
))

fig.show()"""


# # Graphes: bar charts

# ## Variation journée

# In[14]:


fig = go.Figure()

fig.add_trace(go.Bar(
    x = df_france_last15["jour"],
    y = df_france_last15["dc_new"],
    name = "Nouveaux décès hosp.",
    marker_color='black',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_france_last15["jour"],
    y = df_france_last15["rea_new"],
    name = "<b>Variation</b> des réanimations",
    marker_color='red',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_france_last15["jour"],
    y = df_france_last15["hosp_nonrea_new"],
    name = "<b>Variation</b> des hosp. (hors réa.)",
    marker_color='grey',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_france_last15["jour"],
    y = df_france_last15["rad_new"],
    name = "Nouv. retours à domicile",
    marker_color='green',
    opacity=0.6
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(

    barmode='group',
    title={
                'text': "<b>COVID-19 : variation quotidienne en France</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis=dict(
        title='',
        tickformat='%d/%m',
        nticks=100),
    yaxis_title="Nb. de personnes",
    
    annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "var_journ"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1400, height=800)

fig.update_layout(

    legend_orientation="h",
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Var jour lines

# In[15]:



for (range_x, name_fig) in [(["2020-03-22", last_day_plot], "var_journ_lines")]: #(["2020-06-10", last_day_plot], "var_journ_lines_recent")
    #fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    dc_new_rolling = df_france["dc_new"].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=4,
        opacity=0.8
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [dc_new_rolling.values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    #
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["dc_new"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.3,
        showlegend=False
    ))

    ###
    rea_new_rolling = df_france["rea_new"].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = rea_new_rolling,
        name = "<b>Variation</b> des réanimations",
        marker_color='red',
        line_width=4,
        opacity=0.8
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [rea_new_rolling.values[-1]],
        name = "<b>Variation</b> des réanimations",
        marker_color='red',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))
    #

    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["rea_new"],
        name = "<b>Variation</b> des réanimations",
        mode="markers",
        marker_color='red',
        line_width=3,
        opacity=0.3,
        showlegend=False
    ))

    ##
    hosp_non_rea_rolling = df_france["hosp_nonrea_new"].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = hosp_non_rea_rolling,
        name = "<b>Variation</b> des hosp. (hors réa.)",
        marker_color='grey',
        fillcolor='rgba(219, 219, 219, 0.5)',
        line_width=4,
        opacity=0.8,
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [hosp_non_rea_rolling.values[-1]],
        name = "<b>Variation</b> des ",
        marker_color='grey',
        fillcolor='rgba(219, 219, 219, 0.5)',
        marker_size=15,
        mode="markers",
        opacity=1,
        showlegend=False
    ))


    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["hosp_nonrea_new"],
        name = "<b>Variation</b> des tests positifs",
        mode="markers",
        marker_color='grey',
        opacity=0.3,
        showlegend=False
    ))
    
    ###
    incid_rolling = df_incid_france['P'].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_incid_france["jour"],
        y = incid_rolling,
        name = "<b>Variation</b> des tests positifs",
        marker_color='blue',
        line_width=4,
        opacity=0.8
    ), secondary_y=True)
    
    fig.add_trace(go.Scatter(
        x = [df_incid_france['jour'].max()],
        y = [incid_rolling.values[-1]],
        name = "<b>Variation</b> des tests positifs",
        marker_color='blue',
        fillcolor='rgba(219, 219, 219, 0.5)',
        marker_size=15,
        mode="markers",
        opacity=1,
        showlegend=False
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x = df_incid_france['jour'],
        y = df_incid_france['P'],
        name = "<b>Variation</b> des tests positifs",
        mode="markers",
        marker_color='blue',
        opacity=0.3,
        showlegend=False
    ), secondary_y=True)

    ###
    rad_new_rolling=df_france["rad_new"].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = rad_new_rolling,
        name = "Nouv. retours à domicile",
        marker_color='green',
        fillcolor='rgba(114, 171, 108, 0.3)',
        line_width=4,
        opacity=0.8,
    ))

    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [rad_new_rolling.values[-1]],
        name = "Nouv. retours à domicile",
        marker_color='green',
        fillcolor='rgba(114, 171, 108, 0.3)',
        marker_size=15,
        mode="markers",
        opacity=1,
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["rad_new"],
        name = "Nouv. retours à domicile",
        mode="markers",
        marker_color='green',
        line_width=2,
        opacity=0.3,
        showlegend=False
    ))

    fig.update_yaxes(zeroline=True, range=[df_france["hosp_nonrea_new"].min(), df_france['rad_new'].max()], zerolinewidth=2, zerolinecolor='Grey', secondary_y=False)
    fig.update_yaxes(zeroline=True, range=[df_france["hosp_nonrea_new"].min(), df_incid_france['P'].max()], zerolinewidth=2, zerolinecolor='Grey', secondary_y=True)
    fig.update_xaxes(range=range_x, nticks=30, ticks='inside', tickangle=0)

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=20,
                r=190,
                b=100,
                t=100,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': "<b>COVID-19 : variation quotidienne en France</b>, moyenne mobile centrée de 7 jours",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
            title='',
            tickformat='%d/%m'),
        yaxis_title="Nb. de personnes",

        annotations = [
                    dict(
                        x=0,
                        y=1.05,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )
    for (data_temp, type_ppl, col, ys, ay, date, yref) in [(dc_new_rolling, "décès", "black", 3, -10, dates[-1], 'y1'), (incid_rolling, "tests positifs", "blue", 8, -25, df_incid_france['jour'].max(), 'y2'), (rea_new_rolling, "réanimations", "red", -3, 10, dates[-1], 'y1'), (hosp_non_rea_rolling, "hospitalisations<br> &#8205; (hors réa.)", "grey", -10, 30, dates[-1], 'y1'), (rad_new_rolling, "retours à<br> &#8205; domicile", "green", 10, -30, dates[-1], 'y1')]:
        fig['layout']['annotations'] += (dict(
                x=date, y = data_temp.values[-1], # annotation point
                xref='x1', 
                yref=yref,
                text=" <b>{}</b> {}".format('%+d' % math.trunc(round(data_temp.values[-1], 2)), type_ppl),
                xshift=15,
                yshift=ys,
                xanchor="left",
                align='left',
                font=dict(
                    color=col,
                    size=15
                    ),
                opacity=0.8,
                ax=30,
                ay=ay,
            arrowcolor=col,
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=4,
                showarrow=True
            ),)

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1300, height=850)

    fig.update_layout(

        legend_orientation="h"
                     )
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[16]:


range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "dc_journ", [0, df_new_france["incid_dc"].max()]
title = "<b>Décès hospitaliers quotidiens</b> du Covid19"

for i in ("", "log"):
    dc_new_rolling = df_new_france["incid_dc"].rolling(window=7).mean()
    
    if i=="log":
        title += " [log.]"
        range_y=[0, math.log(df_france["dc_new"].max())/2]
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(
        x = df_new_france["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(0,0,0,0.3)",
        showlegend=False
    ))
    
    fig.add_shape(type="line",
    x0="2020-03-17", y0=0, x1="2020-03-17", y1=300000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-05-11", y0=0, x1="2020-05-11", y1=300000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-10-30", y0=0, x1="2020-10-30", y1=300000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-11-28", y0=0, x1="2020-11-28", y1=300000,
    line=dict(color="Orange",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-12-15", y0=0, x1="2020-12-15", y1=300000,
    line=dict(color="Green",width=0.5, dash="dot")
    )

    try:
        model = make_pipeline(PolynomialFeatures(4), Ridge())
        model.fit(df_new_france["jour"][-40:].index.values.reshape(-1, 1), dc_new_rolling[-40:].fillna(method="bfill"))

        index_max = df_new_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max, index_max+8)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_incid_france["jour"]), '%Y-%m-%d') - timedelta(days=0))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(3, len(x_pred)+3)]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(0,0,0,0.2)',
            line_width=5,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ))

    except:
        pass

    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [dc_new_rolling.values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgba(255, 255, 255, 0.6)',
        marker_size=18,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [dc_new_rolling.values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        marker_size=13,
        opacity=1,
        showlegend=False
    ))

    #
    fig.add_trace(go.Scatter(
        x = df_new_france["jour"],
        y = df_new_france["incid_dc"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ))

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), type="log")
    else:
        fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
        
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-17", last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=30),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0.5,
                        y=0.95,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>", #'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    
                        showarrow = False
                    ),
                    ]
                   )
    try:
        croissance = math.trunc((dc_new_rolling.values[-1]-dc_new_rolling.values[-7-1]) * 100 / dc_new_rolling.values[-1-7])
    except:
        croissance=0
    if croissance >= 0:
        croissance="+"+str(abs(croissance))

        
    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = dc_new_rolling.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % math.trunc(round(dc_new_rolling.values[-1], 2)), "décès quotidiens</b><br>en moyenne<br>du {} au {}.<br>{} % en 7 jours".format(datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=20
                ),
            opacity=0.8,
            ax=-300,
            ay=-60,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
            dict(
            x = "2020-03-17", y = 605, # annotation point
            xref='x1', 
            yref='y1',
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="red",
                size=8
                ),
            showarrow=False
        ),
           dict(
            x = "2020-05-11", y = 605, # annotation point
            xref='x1', 
            yref='y1',
            text="Déconfinement",
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="green",
                size=8
                ),
            showarrow=False
        ),
            dict(
            x = "2020-10-30", y = 605, # annotation point
            xref='x1', 
            yref='y1',
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="red",
                size=8
                ),
            showarrow=False
        ),
            dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[17]:


range_x, name_fig, range_y = ["2020-03-10", last_day_plot], "dc_journ_croissance", [-100, 150]
title = "<b>Croissance des décès hospitaliers</b> du Covid19"

fig = go.Figure()

dc_new_rolling = df_new_france["incid_dc"].rolling(window=7).mean()
dc_new_rolling = ((dc_new_rolling - dc_new_rolling.shift(7)) / dc_new_rolling.shift(7) * 100)

fig.add_trace(go.Bar(
    x = df_new_france["jour"],
    y = dc_new_rolling,
    name = "",
    marker_color='black',
    #line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(0,0,0,0.3)",
    showlegend=False
))

###

fig.update_yaxes(zerolinecolor='Grey', range=[-50, 300], tickfont=dict(size=18))
fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    bargap=0,
    margin=dict(
            l=50,
            r=0,
            b=50,
            t=70,
            pad=0
        ),
    legend_orientation="h",
    barmode='group',
    title={
                'text': title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=30),
    xaxis=dict(
            title='',
            tickformat='%d/%m'),

    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),
                ]
                 )

fig['layout']['annotations'] += (dict(
        x = dates[-1], y = dc_new_rolling.values[-1], # annotation point
        xref='x1', 
        yref='y1',
            text=" <b>{}% {}".format('%d' % math.trunc(round(dc_new_rolling.values[-1], 2)), "de croissance<br>hebdomadaire</b><br>".format(datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'))),
        xshift=-2,
        yshift=10,
        xanchor="center",
        align='center',
        font=dict(
            color="black",
            size=20
            ),
        opacity=0.8,
        ax=-100,
        ay=-90,
        arrowcolor="black",
        arrowsize=1.5,
        arrowwidth=1,
        arrowhead=0,
        showarrow=True
    ),)

fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[18]:


df_world_confirmed, df_world_deaths = pd.read_csv(PATH+'data/data_confirmed.csv'), pd.read_csv(PATH+'data/data_deaths.csv')


# In[19]:


range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "cas_est_journ", [0, df_world_deaths["France"].diff().max()/0.002*0.7]
title = "<b>Estimations des cas</b> du Covid19 à partir des décès<br>"
sub = "Hypothèses : taux de mortalité de 0,5 % ; décalage de 21 j. entre cas et décès"

fig = go.Figure()

#dc_new_rolling = df_france["dc_new"].rolling(window=7).mean().shift(-21).dropna()/0.005
n=7

estimated_rolling_bas = df_world_deaths["France"].diff().rolling(window=n).mean().shift(-21).dropna()/0.007
estimated_rolling_moy = df_world_deaths["France"].diff().rolling(window=n).mean().shift(-21).dropna()/0.005
estimated_rolling_haut = df_world_deaths["France"].diff().rolling(window=n).mean().shift(-21).dropna()/0.002
confirmed_rolling = df_world_confirmed["France"].diff().rolling(window=n, center=True).mean()

fig.add_trace(go.Scatter(
    x = df_world_deaths["date"],
    y = estimated_rolling_haut,
    name = "Est.",
    marker_color='black',
    line_width=0,
    opacity=0.6,
    #fill='tozeroy',
    fillcolor="rgba(0,0,0,0.3)",
    showlegend=False
))

fig.add_trace(go.Scatter(
    x = df_world_deaths["date"],
    y = estimated_rolling_bas,
    name = "Est.",
    marker_color='black',
    line_width=0,
    opacity=1,
    fill='tonexty',
    fillcolor="rgba(0,0,0,0.3)",
    showlegend=False
))

fig.add_trace(go.Scatter(
    x = df_world_deaths["date"],
    y = estimated_rolling_moy,
    name = "Est.",
    marker_color='black',
    line_width=2,
    opacity=1,
    #fill='tozeroy',
    fillcolor="rgba(0,0,0,0.3)",
    showlegend=False
))

fig.add_trace(go.Scatter(
    x = df_world_confirmed["date"],
    y = confirmed_rolling,
    name = "Conf",
    marker_color='red',
    line_width=3,
    opacity=0.8,
    #fill='tozeroy',
    fillcolor="rgba(201, 4, 4,0.3)",
    showlegend=False
))

fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

cas_est = round((df_world_deaths["France"].diff()/0.005).sum()/1000000, 2)
cas_detect = round(df_world_confirmed["France"].diff().sum().astype(int)/1000000, 2)

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    margin=dict(
            l=50,
            r=0,
            b=50,
            t=70,
            pad=0
        ),
    legend_orientation="h",
    barmode='group',
    title={
                'text': title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=30),
    xaxis=dict(
            title='',
            tickformat='%d/%m'),
    
    
    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    text=sub,
                    font=dict(size=15),
                    showarrow = False
                ),
            dict(
                    x=0.5,
                    y=0.93,
                    xref='paper',
                    yref='paper',
                    text="Total cas estimés : {} millions ({} % pop.)".format(cas_est, round(cas_est/67*100, 1)),
                    font=dict(size=15, color="black"),
                    showarrow = False
                ),
            dict(
                    x=0.5,
                    y=0.89,
                    xref='paper',
                    yref='paper',
                    text="Total cas détectés : {} millions".format(cas_detect),
                    font=dict(size=15, color="red"),
                    showarrow = False
                ),
                ]
                 )

fig['layout']['annotations'] += (dict(
        x = df_world_deaths["date"].values[-21], y = estimated_rolling_moy.values[-1], # annotation point
        xref='x1', 
        yref='y1',
        text=" <b>{} {}".format('%d' % math.trunc(round(estimated_rolling_moy.values[-1], 2)), "cas estimés</b><br>le {}/{}".format(df_world_deaths["date"].values[-21][-2:], df_world_deaths["date"].values[-21][-5:-3])),
        xshift=-5,
        yshift=5,
        xanchor="center",
        align='center',
        font=dict(
            color="black",
            size=20
            ),
        opacity=0.8,
        ax=-30,
        ay=-130,
        arrowcolor="black",
        arrowsize=1.5,
        arrowwidth=1,
        arrowhead=0,
        showarrow=True
    ),
    dict(
        x = df_world_deaths["date"].values[-21], y = confirmed_rolling.dropna().values[-21+5], # annotation point
        xref='x1', 
        yref='y1',
        text=" <b>{} {}".format('%d' % math.trunc(round(confirmed_rolling.dropna().values[-21+5], 2)), "cas<br>détéctés</b>"),
        xshift=-5,
        yshift=5,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=20
            ),
        opacity=0.8,
        ax=-120,
        ay=-60,
        arrowcolor="red",
        arrowsize=1.5,
        arrowwidth=1,
        arrowhead=0,
        showarrow=True
    ))

fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[20]:



range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "rea_journ", [0, df_france["rea"].max()*1.2]
title = "<b>Personnes en réanimation</b> pour Covid19"

for i in ("", "log"):
    if i=="log":
        title += " [log.]"
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_france["rea"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(201, 4, 4)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(201, 4, 4,0.3)",
        showlegend=False
    ))
    
    fig.add_trace(go.Bar(
        x = df_new_france["jour"],
        y = df_new_france["incid_rea"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(201, 4, 4)',
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_shape(type="line",
    x0="2020-03-17", y0=0, x1="2020-03-17", y1=15000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-05-11", y0=0, x1="2020-05-11", y1=15000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-10-30", y0=0, x1="2020-10-30", y1=15000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-11-28", y0=0, x1="2020-11-28", y1=15000,
    line=dict(color="Orange",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-01-20", y0=0, x1="2020-01-20", y1=15000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2019-10-30", y0=3000, x1="2021-10-30", y1=3000,
    line=dict(color="green",width=2, dash="dot"), xref='x1', yref='y1'
    )

    try:
        model = make_pipeline(PolynomialFeatures(2), Ridge())
        model.fit(df_france["jour"][-10:].index.values.reshape(-1, 1), df_france["rea"][-10:].fillna(method="bfill"))

        index_max = df_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max-0, index_max+14)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_france["jour"]), '%Y-%m-%d') - timedelta(days=0))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(x_pred))]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(201, 4, 4, 0.2)',
            line_width=5,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ))

    except Exception as e:
        print(e)
        print("error")
        pass
    
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["rea"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgba(255, 255, 255, 0.6)',
        marker_size=18,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["rea"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(201, 4, 4)',
        marker_size=13,
        opacity=1,
        showlegend=False
    ))

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), type="log", range=[0, 4])
    else:
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=range_y)
        
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-17", last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=30),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0.5,
                        y=0.95,
                        font=dict(size=14),
                        xref='paper',
                        yref='paper',
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    
                    ]
                     )

    croissance = math.trunc((df_france["rea"].values[-1] - df_france["rea"].values[-8]) * 100 / df_france["rea"].values[-8])
    if croissance >= 0:
        croissance="+"+str(abs(croissance))
        
    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_france["rea"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_france["rea"].values[-1], "personnes<br>en réanimation</b><br>le {}.<br>{} % en 7 jours".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=20
                ),
            opacity=0.8,
            ax=-250,
            ay=-70,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),dict(
            x = df_new_france["jour"].values[-1], y = (df_new_france["incid_rea"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_france["incid_rea"].values[-1], "<br>admissions"),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color='rgb(201, 4, 4)',
                size=10
                ),
            opacity=0.8,
            ax=-20,
            ay=-40,
            arrowcolor='rgb(201, 4, 4)',
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
         dict(
            x = dates[-1], y = 3000, # annotation point
            xref='x1', 
            yref='y1',
            text="Objectif",
            xshift=0,
            yshift=0,
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="green",
                size=10
                ),
            opacity=1,
            ax=0,
            ay=0,
            showarrow=False
        ),
            dict(
            x = "2020-03-17", y = 8100, # annotation point
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="red",
                size=8
                )
        ),
            dict(
            x = "2020-10-30", y = 8100, # annotation point
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="red",
                size=8
                )
        ),
            dict(
            x = "2020-05-11", y = 8100, # annotation point
            text="Déconfinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="green",
                size=8
                )
        ),
        dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[21]:


range_x, name_fig = ["2020-03-10", last_day_plot], "rea_journ_croissance"
title = "<b>Croissance des réanimations</b> pour Covid19"

fig = go.Figure()

croissance = (df_france["rea"]-df_france["rea"].shift(7))/df_france["rea"].shift(7)*100
fig.add_trace(go.Bar(
    x = dates,
    y = croissance,
    name = "",
    marker_color='rgb(201, 4, 4)',
    #line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(201, 4, 4,0.3)",
    showlegend=False
))

###

fig.update_yaxes(zerolinecolor='Grey', range=[-50, 300], tickfont=dict(size=18))
fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    bargap=0,
    margin=dict(
            l=50,
            r=0,
            b=50,
            t=70,
            pad=0
        ),
    legend_orientation="h",
    barmode='group',
    title={
                'text': title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=30),
    xaxis=dict(
            title='',
            tickformat='%d/%m'),

    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),
                ]
                 )


fig['layout']['annotations'] += (dict(
        x = dates[-1], y = croissance.values[-1], # annotation point
        xref='x1', 
        yref='y1',
        text=" <b>{}% {}".format('%d' % croissance.values[-1], "de croissance<br>hebdomadaire"),
        xshift=-2,
        yshift=10,
        xanchor="center",
        align='center',
        font=dict(
            color="rgb(201, 4, 4)",
            size=20
            ),
        opacity=0.8,
        ax=-100,
        ay=-90,
        arrowcolor="rgb(201, 4, 4)",
        arrowsize=1.5,
        arrowwidth=1,
        arrowhead=0,
        showarrow=True
    ),)

fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[22]:


range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "hosp_journ", [0, df_france["hosp"].max()*1.2]
title = "<b>Personnes hospitalisées</b> pour Covid19"

for i in ("", "log"):
    if i=="log":
        title+= " [log.]"
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_france["hosp"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(209, 102, 21)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    fig.add_shape(type="line",
    x0="2020-03-17", y0=0, x1="2020-03-17", y1=300000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-05-11", y0=0, x1="2020-05-11", y1=300000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-10-30", y0=0, x1="2020-10-30", y1=300000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-11-28", y0=0, x1="2020-11-28", y1=300000,
    line=dict(color="Orange",width=0.5, dash="dot")
    )
    
    
    
    """fig.add_shape(type="rect",
                    x0="2020-03-17", x1="2020-05-11", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.05,
                    layer="below"
        )
    """
    """fig.add_shape(type="rect",
                    x0="2020-03-17", x1="2020-03-17", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=0.5,
                    ),
                    layer="below"
        )
    """
    """fig.add_shape(type="rect",
                    x0="2020-10-30", x1=last_day_plot_dashboard, 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.05,
                      layer="below"

        )"""
    
    """fig.add_shape(type="rect",
                    x0="2020-10-30", x1="2020-10-30", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=0.5,
                    ),
                    layer="below"
        )"""
    
    fig.add_trace(go.Bar(
        x = df_new_france["jour"],
        y = df_new_france["incid_hosp"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(209, 102, 21)',
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))

    try:
        model = make_pipeline(PolynomialFeatures(3), Ridge())
        model.fit(df_france["jour"][-20:].index.values.reshape(-1, 1), df_france["hosp"][-20:].fillna(method="bfill"))

        index_max = df_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max-4, index_max+5)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_france["jour"]), '%Y-%m-%d') - timedelta(days=4))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(x_pred))]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(209, 102, 21, 0.4)',
            line_width=5,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ))

    except Exception as e:
        print(e)
        print("error")
        pass

    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["hosp"].values[-1]],
        name = "",
        mode="markers",
        marker_color='rgba(255, 255, 255, 0.6)',
        marker_size=18,
        opacity=1,
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["hosp"].values[-1]],
        name = "",
        mode="markers",
        marker_color='rgb(209, 102, 21)',
        marker_size=13,
        opacity=1,
        showlegend=False
    ))

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), type="log", range=[0, 5]) #range=[0, max(max(y_plot), df_france["hosp"].max())*1.1]
    else:
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=range_y) #range=[0, max(max(y_plot), df_france["hosp"].max())*1.1] 
        
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-17", last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=30),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0.5,
                        y=0.95,
                        font=dict(size=14),
                        xref='paper',
                        yref='paper',
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>", #'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    
                        showarrow = False
                    ),
 
                    ]
                )

    croissance = math.trunc(((df_france["hosp"].values[-1]-df_france["hosp"].values[-1-7]) / df_france["hosp"].values[-1-7]) * 100)
    if croissance >= 0:
        croissance="+"+str(abs(croissance))
        
    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = (df_france["hosp"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_france["hosp"].values[-1], "personnes<br>hospitalisées</b><br>le {}.<br>{} % en 7 jours".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-300,
            ay=0,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ), dict(
            x = df_new_france["jour"].values[-1], y = (df_new_france["incid_hosp"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_france["incid_hosp"].values[-1], "<br>admissions"),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=10
                ),
            opacity=0.8,
            ax=-20,
            ay=-40,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
          dict(
            x = "2020-03-17", y = 40000, # annotation point
            xref='x1', 
            yref='y1',
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="red",
                size=8
                ),
            showarrow=False
        ),
            dict(
            x = "2020-10-30", y = 40000, # annotation point
            xref='x1', 
            yref='y1',
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="red",
                size=8
                ),
            showarrow=False
        ),
          dict(
            x = "2020-05-11", y = 40000, # annotation point
            xref='x1', 
            yref='y1',
            text="Déconfinement",
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="green",
                size=8
                ),
            showarrow=False
        ),
           dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[23]:


range_x, name_fig = ["2020-03-10", last_day_plot], "hosp_journ_croissance"
title = "<b>Croissance des hospitalisations</b> pour Covid19"

fig = go.Figure()

croissance = (df_france["hosp"]-df_france["hosp"].shift(7))/df_france["hosp"].shift(7)*100
fig.add_trace(go.Bar(
    x = dates,
    y = croissance,
    name = "Croissance hosp",
    marker_color='rgb(209, 102, 21)',
    #line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(209, 102, 21,0.3)",
    showlegend=False
))

###

fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=[-50, 300],)
fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    bargap=0,
    margin=dict(
            l=50,
            r=0,
            b=50,
            t=70,
            pad=0
        ),
    legend_orientation="h",
    barmode='group',
    title={
                'text': title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=25),
    xaxis=dict(
            title='',
            tickformat='%d/%m'),

    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),
                ]
                 )

fig['layout']['annotations'] += (dict(
        x = dates[-1], y = croissance.values[-1], # annotation point
        xref='x1', 
        yref='y1',
        text=" <b>{}% {}".format('%d' % croissance.values[-1], "de croissance<br>hebdomadaire"),
        xshift=-2,
        yshift=10,
        xanchor="center",
        align='center',
        font=dict(
            color="rgb(209, 102, 21)",
            size=20
            ),
        opacity=0.8,
        ax=-100,
        ay=-90,
        arrowcolor="rgb(209, 102, 21)",
        arrowsize=1.5,
        arrowwidth=1,
        arrowhead=0,
        showarrow=True
    ),)

fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[24]:



range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "cas_journ", [0, df_incid_france["P"].max()]
title = "<b>Cas positifs</b> au Covid19"

#fig = go.Figure()
for i in ("", "log"):
    if i=="log":
        title += " [log.]"
        range_y=[0, math.log(df_incid_france["P"].max())/2]
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[""], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}]])

    df_incid_france_cas_rolling = df_incid[df_incid["dep"] != "973"].groupby(["jour"]).sum().reset_index()["P"].rolling(window=7, center=True).mean()#df_incid_france["P"].rolling(window=7, center=True).mean()
    df_incid_france_tests_rolling = df_incid_france["T"].rolling(window=7, center=True).mean()

    fig.add_trace(go.Scatter(
        x = df_incid_france["jour"],
        y = df_incid_france_cas_rolling,
        name = "Cas positifs (moyenne 7 j.)",
        marker_color='rgb(8, 115, 191)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.3)",
        showlegend=True
    ), secondary_y=True)
    
    fig.add_trace(go.Bar(
        x = df_incid_france["jour"],
        y = df_incid_france_tests_rolling,
        name = "Tests réalisés",
        marker_color='rgba(0, 0, 0, 0.2)',
        opacity=0.8,
        showlegend=True,
        
    ), secondary_y=False)
    
    fig.add_shape(type="line",
    x0="2020-03-17", y0=0, x1="2020-03-17", y1=300000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-05-11", y0=0, x1="2020-05-11", y1=300000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-10-30", y0=0, x1="2020-10-30", y1=300000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-12-15", y0=0, x1="2020-12-15", y1=300000,
    line=dict(color="Orange",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2019-10-30", y0=5000, x1="2021-10-30", y1=5000,
    line=dict(color="green",width=2, dash="dot"), xref='x1', yref='y2'
    )

    try:

        model = make_pipeline(PolynomialFeatures(2), Ridge())
        model.fit(df_incid_france["jour"][-10:-4].index.values.reshape(-1, 1), df_incid_france_cas_rolling[-10:-4].fillna(method="bfill"))

        index_max = df_incid_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max-4, index_max+3)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_incid_france["jour"]), '%Y-%m-%d') - timedelta(days=4))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(x_pred))]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(8, 115, 191, 0.2)',
            line_width=5,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ), secondary_y=True)

    except:
        pass
    
    fig.add_trace(go.Scatter(
        x = [dates_incid[-4]],
        y = [df_incid_france_cas_rolling.values[-4]],
        name = "",
        mode="markers",
        marker_color='rgba(255, 255, 255, 0.6)',
        marker_size=16,
        opacity=1,
        showlegend=False
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x = [dates_incid[-4]],
        y = [df_incid_france_cas_rolling.values[-4]],
        name = "",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        marker_size=11,
        opacity=1,
        showlegend=False
    ), secondary_y=True)
    
    

    """fig.add_trace(go.Scatter(
        x = df_incid_france["jour"],
        y = df_incid_france["P"],
        name = "Cas positifs",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        line_width=3,
        opacity=0.4,
        showlegend=True
    ), secondary_y=True)"""

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), type="log", secondary_y=True)
        fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), type="log", secondary_y=False)
    else:
        fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), secondary_y=True)
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-18", last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        bargap=0,
        margin=dict(
                l=50,
                r=10,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=30),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0.5,
                        y=0.99,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                        showarrow=False
                    ),
                    ]
                     )

    croissance = math.trunc(((df_incid_france_cas_rolling.values[-4]-df_incid_france_cas_rolling.values[-4-7]) / df_incid_france_cas_rolling.values[-4-7])*100)
    if croissance >= 0:
        croissance="+"+str(abs(croissance))
        
    if i=="log":
        y=math.log(df_incid_france_cas_rolling.values[-4])
    else:
        y=df_incid_france_cas_rolling.values[-4]
        
    fig['layout']['annotations'] += (dict(
            x = dates_incid[-4], y = y, # annotation point
            xref='x1', 
            yref='y2',
            text=" <b>{} {}".format('%d' % df_incid_france_cas_rolling.values[-4], "cas quotidiens<br></b>en moyenne du {} au {}.<br> {} % en 7 jours".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=20
                ),
            opacity=1,
            ax=-400,
            ay=-100,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
          dict(
            x = dates_incid[-1], y = 5000, # annotation point
            xref='x1', 
            yref='y2',
            text="Objectif",
            xshift=0,
            yshift=0,
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="green",
                size=10
                ),
            opacity=1,
            ax=0,
            ay=0,
            showarrow=False
        ),
            dict(
            x = "2020-10-30", y = 65000, # annotation point
            xref='x1', 
            yref='y2',
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            font=dict(
                color="red",
                size=8
                ),
            showarrow=False
        ),
         dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[ ]:





# In[25]:



    

range_x, name_fig, range_y = ["2020-03-10", last_day_plot], "cas_journ_croissance", [-50, 150]
title = "<b>Croissance des cas positifs</b> au Covid19"

fig = go.Figure()

df_incid_france_cas_rolling = df_incid_france["P"].rolling(window=7, center=True).mean()
df_incid_france_cas_rolling = (df_incid_france_cas_rolling-df_incid_france_cas_rolling.shift(7))/df_incid_france_cas_rolling.shift(7)*100

fig.add_trace(go.Bar(
    x = df_incid_france["jour"],
    y = df_incid_france_cas_rolling,
    name = "",
    marker_color='rgb(8, 115, 191)',
    #line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    showlegend=False
))

###

fig.update_yaxes(zerolinecolor='Grey', range=[-50, 300], tickfont=dict(size=18))
fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    bargap=0,
    margin=dict(
            l=50,
            r=0,
            b=50,
            t=70,
            pad=0
        ),
    legend_orientation="h",
    barmode='group',
    title={
                'text': title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=30),
    xaxis=dict(
            title='',
            tickformat='%d/%m'),

    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),
                ]
                 )

croissance = math.trunc(((df_incid_france_cas_rolling.values[-4]-df_incid_france_cas_rolling.values[-4-7]) / df_incid_france_cas_rolling.values[-4-7])*100)

fig['layout']['annotations'] += (dict(
        x = dates_incid[-4], y = df_incid_france_cas_rolling.values[-4], # annotation point
        xref='x1', 
        yref='y1',
        text=" <b>{}% {}".format('%d' % df_incid_france_cas_rolling.values[-4], "de croissance<br>hebdomadaire"),
        xshift=-2,
        yshift=10,
        xanchor="center",
        align='center',
        font=dict(
            color="rgb(8, 115, 191)",
            size=20
            ),
        opacity=1,
        ax=-130,
        ay=-10,
        arrowcolor="rgb(8, 115, 191)",
        arrowsize=1.5,
        arrowwidth=1,
        arrowhead=0,
        showarrow=True
    ),)

fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[26]:


"""range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "cas_rea_hosp_dc_journ", [0, df_incid_france["P"].max()]
title = "<b>Cas positifs, hospitalisations, réanimations et décès</b> du Covid19"

fig = go.Figure()

dc_new_rolling = df_france["dc_new"].rolling(window=7).mean()

fig.add_trace(go.Scatter(
    x = df_france["jour"],
    y = dc_new_rolling,
    name = "Décès",
    marker_color='black',
    line_width=8,
    opacity=0.8,
    fill='tozeroy',
    fillcolor="rgba(0,0,0,0.3)",
    showlegend=True
))

df_incid_france_cas_rolling = df_incid_france["P"].rolling(window=7, center=True).mean()

fig.add_trace(go.Scatter(
    x = dates,
    y = df_france["rea"].shift(-10).diff(),
    name = "Réanimations. * 10 (décalage 10 jours)",
    marker_color='rgb(201, 4, 4)',
    line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(201, 4, 4,0.3)",
    showlegend=True
))

fig.add_trace(go.Scatter(
    x = dates,
    y = df_france["hosp"].shift(-6).diff(),
    name = "Hospitalisations * 2 (décalage 6 jours)",
    marker_color='rgb(209, 102, 21)',
    line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(209, 102, 21,0.3)",
    showlegend=True
))

fig.add_trace(go.Scatter(
    x = df_incid_france["jour"],
    y = df_incid_france_cas_rolling,
    name = "Nouveaux décès hosp.",
    marker_color='rgb(8, 115, 191)',
    line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    showlegend=False
))


###

fig.update_yaxes(zerolinecolor='Grey', range=[0, 30000], tickfont=dict(size=18))
fig.update_xaxes(nticks=10, ticks='inside', range=[dates_incid[0], last_day_plot], tickangle=0, tickfont=dict(size=18))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    margin=dict(
            l=50,
            r=0,
            b=50,
            t=70,
            pad=0
        ),
    legend_orientation="h",
    barmode='group',
    title={
                'text': title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=25),
    xaxis=dict(
            title='',
            tickformat='%d/%m'),

    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),
                ]
                 )

croissance = math.trunc(((df_incid_france_cas_rolling.values[-4]-df_incid_france_cas_rolling.values[-4-7]) / df_incid_france_cas_rolling.values[-4-7])*100)

fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()"""


# In[27]:



for croiss in ["", "_croissance", "log"]:
    im1 = cv2.imread(PATH + 'images/charts/france/cas_journ{}.jpeg'.format(croiss))
    im2 = cv2.imread(PATH + 'images/charts/france/hosp_journ{}.jpeg'.format(croiss))
    im3 = cv2.imread(PATH + 'images/charts/france/rea_journ{}.jpeg'.format(croiss))
    im4 = cv2.imread(PATH + 'images/charts/france/dc_journ{}.jpeg'.format(croiss))

    im_haut = cv2.hconcat([im1, im2])
    #cv2.imwrite('images/charts/france/tests_combinaison.jpeg', im_h)
    im_bas = cv2.hconcat([im3, im4])

    im_totale = cv2.vconcat([im_haut, im_bas])
    cv2.imwrite(PATH + 'images/charts/france/dashboard_jour{}.jpeg'.format(croiss), im_totale)


# In[28]:


# Comparaison vague

for (range_x, name_fig, title, x_title) in [(["2020-03-12", "2020-05-12"], "rea_journ_v1","<b>Printemps</b> 2020", 0.8), (["2020-10-25", "2020-12-25"], "rea_journ_v2", "<b>Automne 2020</b>", 0.2)]:

    fig = go.Figure()
    
    fig.add_shape(type="rect",
                    x0="2020-10-30", x1="2020-10-30", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.7,
                      layer="below"

        )
    
    fig.add_shape(type="rect",
                    x0="2020-03-17", x1="2020-03-17", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.7,
                      layer="below"

        )


    fig.add_trace(go.Scatter(
        x = dates,
        y = df_france["rea"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(201, 4, 4)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(201, 4, 4,0.3)",
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["rea"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(201, 4, 4)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))
    
    try:
        model = make_pipeline(PolynomialFeatures(4), Ridge())
        model.fit(df_france["jour"][-40:].index.values.reshape(-1, 1), df_france["rea"][-40:].fillna(method="bfill"))

        index_max = df_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max, index_max+15)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_france["jour"]), '%Y-%m-%d') - timedelta(days=0))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(x_pred))]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(201, 4, 4, 0.2)',
            line_width=5,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ))

    except Exception as e:
        print(e)
        print("error")
        pass


    ###

    fig.update_yaxes(zerolinecolor='Grey', range=[0, 7000], tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, range=range_x, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':x_title,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=30),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [dict(
                        x=0.1,
                        y=0.8,
                        xshift=-10,
                        xref='paper',
                        yref='paper',
                        xanchor="left",
                        yanchor="middle",
                        ax=30,
                        ay=0,
                        text='Confinement',  
                        font=dict(color="red"),
                        arrowcolor="red",
                        arrowhead=1,
                        opacity=0.7,
                        showarrow = True
                    ),
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    croissance = math.trunc((df_france["rea"].values[-1] - df_france["rea"].values[-8]) * 100 / df_france["rea"].values[-8])

    """fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_france["rea"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_france["rea"].values[-1], "personnes<br>en réanimation</b><br>le {}.<br>+ {} % en 7 jours".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B'), croissance)),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=20
                ),
            opacity=0.8,
            ax=50,
            ay=-90,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)"""

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
    print("> " + name_fig)


# In[29]:


for (range_x, name_fig, title, x_title) in [(["2020-03-12", "2020-05-12"], "hosp_journ_v1", "<b>Printemps</b> 2020", 0.8), (["2020-10-25", "2020-12-25"], "hosp_journ_v2", "<b>Automne</b> 2020", 0.2)]:

    fig = go.Figure()
    
    
    fig.add_shape(type="rect",
                    x0="2020-10-30", x1="2020-10-30", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.7,
                      layer="below"

        )
    
    fig.add_shape(type="rect",
                    x0="2020-03-17", x1="2020-03-17", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.7,
                      layer="below"

        )

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_france["hosp"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(209, 102, 21)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))

    try:
        model = make_pipeline(PolynomialFeatures(4), Ridge())
        model.fit(df_france["jour"][-40:].index.values.reshape(-1, 1), df_france["hosp"][-40:].fillna(method="bfill"))

        index_max = df_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max-4, index_max+15)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_france["jour"]), '%Y-%m-%d') - timedelta(days=4))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(x_pred))]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(209, 102, 21, 0.4)',
            line_width=5,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ))

    except Exception as e:
        print(e)
        print("error")
        pass


    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["hosp"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(209, 102, 21)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=[0, 35000], tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':x_title,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=30),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                dict(
                        x=0.1,
                        y=0.8,
                        xshift=-10,
                        xref='paper',
                        yref='paper',
                        xanchor="left",
                        yanchor="middle",
                        ax=30,
                        ay=0,
                        text='Confinement',  
                        font=dict(color="red"),
                        arrowcolor="red",
                        arrowhead=1,
                        opacity=0.7,
                        showarrow = True
                    ),
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    croissance = math.trunc(((df_france["hosp"].values[-1]-df_france["hosp"].values[-1-7]) / df_france["hosp"].values[-1-7]) * 100)
    """fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_france["hosp"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_france["hosp"].values[-1], "personnes<br>hospitalisées</b><br>le {}.<br>+ {} % en 7 jours".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B'), croissance)),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=20
                ),
            opacity=0.8,
            ax=50,
            ay=-90,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)"""

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[30]:


for (range_x, name_fig, title, x_title) in [(["2020-03-12", "2020-05-12"], "dc_journ_v1", "<b>Printemps</b> 2020", 0.8), (["2020-10-25", "2020-12-25"], "dc_journ_v2", "<b>Automne</b> 2020", 0.2)]:

    fig = go.Figure()
    
    fig.add_shape(type="rect",
                    x0="2020-10-30", x1="2020-10-30", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.7,
                      layer="below"

        )
    
    fig.add_shape(type="rect",
                    x0="2020-03-17", x1="2020-03-17", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.7,
                      layer="below"

        )


    dc_new_rolling = df_france["dc_new"].rolling(window=7).mean()

    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(0,0,0,0.3)",
        showlegend=False
    ))

    try:
        model = make_pipeline(PolynomialFeatures(4), Ridge())
        model.fit(df_france["jour"][-40:].index.values.reshape(-1, 1), dc_new_rolling[-40:].fillna(method="bfill"))

        index_max = df_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max, index_max+11)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_incid_france["jour"]), '%Y-%m-%d') - timedelta(days=0))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(3, len(x_pred)+3)]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(0,0,0,0.2)',
            line_width=5,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ))

    except:
        pass


    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [dc_new_rolling.values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    #
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["dc_new"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=[0, 550], tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':x_title,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=30),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0.1,
                        y=0.8,
                        xshift=-10,
                        xref='paper',
                        yref='paper',
                        xanchor="left",
                        yanchor="middle",
                        ax=30,
                        ay=0,
                        text='Confinement',  
                        font=dict(color="red"),
                        arrowcolor="red",
                        arrowhead=1,
                        opacity=0.7,
                        showarrow = True
                    ),
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : covidtracker.fr'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )
    """croissance = math.trunc((dc_new_rolling.values[-1]-dc_new_rolling.values[-1-7]) * 100 / dc_new_rolling.values[-1])
    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = dc_new_rolling.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % math.trunc(round(dc_new_rolling.values[-1], 2)), "décès quotidiens</b><br>en moyenne<br>du {} au {}.<br>+ {} % en 7 jours".format(datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=20
                ),
            opacity=0.8,
            ax=50,
            ay=-90,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)"""

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# ## Evolution jorunée

# In[31]:


#EVOL JOURN
fig = make_subplots(specs=[[{"secondary_y": True}]])
#fig = go.Figure()

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_dc"],
    name = "Nouveaux décès hosp.",
    marker_color='black',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_rea"],
    name = "<b>Admissions</b> réanimations",
    marker_color='red',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_hosp_nonrea"],
    name = "<b>Admissions</b> autres hospit.",
    marker_color='grey',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_rad"],
    name = "Nouv. retours à domicile",
    marker_color='green',
    opacity=0.6
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    legend_orientation="h",
    margin=dict(
            l=0,
            r=0,
            b=0,
            t=80,
            pad=0
        ),
    #paper_bgcolor='#fffbed',#fcf8ed #faf9ed
    #plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
    barmode='group',
    title={
                'text': "<b>COVID-19 : évolution quotidienne en France</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis=dict(
        title='',
        tickformat='%d/%m',
        nticks=100),
    yaxis_title="Nb. de personnes",
    
    annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "evol_journ"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=1.5, width=900, height=800)

fig.update_layout(
    legend_orientation="h",
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Tests Covid

# In[32]:


# TESTS

fig = make_subplots(specs=[[{"secondary_y": True}]])
#fig = go.Figure()

fig.add_trace(go.Bar(
    x = df_tests_tot["jour"],
    y = df_tests_tot["nb_pos"].rolling(window=4, center=True).mean(),
    name = "Tests positifs",
    marker_color='red',
    opacity=0.6
), secondary_y=False)

fig.add_trace(go.Bar(
    x = df_tests_tot["jour"],
    y = df_tests_tot["nb_test"].rolling(window=4, center=True).mean(),
    name = "Tests négatifs",
    marker_color='green',
    opacity=0.6
), secondary_y=False)


# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    barmode='stack',
    #paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
    #plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
    title={
                'text': "<b>COVID-19 : tests en laboratoire de ville</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis=dict(
        title='',
        tickformat='%d/%m',
        nticks=100),
    yaxis_title="Nb. de personnes testées",
    
    annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "tests_journ"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1400, height=800)

fig.update_layout(
    legend_orientation="h",
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Entrées/Sortires hosp et réa

# In[33]:


"""fig = go.Figure()
#fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_rea"],
    name = "Admissions réanimation",
    marker_color='red',
    opacity=0.8
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_hosp_nonrea"],
    name = "Admissions hospitalisation (hors réa.)",
    marker_color='red',
    opacity=0.5
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_dep_rea"],
    name = "Sorties réanimation",
    marker_color='green',
    opacity=0.8
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_dep_hosp_nonrea"],
    name = "Sorties hospitalisation (hors réa.)",
    marker_color='green',
    opacity=0.5
))

fig.add_trace(go.Scatter(
    x = df_france["jour"],
    y = df_france["rea_new"],
    name = "Solde quotidien réanimation",
    marker_color='black',
    mode="lines+markers",
    opacity=0.8
))

fig.add_trace(go.Scatter(
    x = df_france["jour"],
    y = df_france["hosp_nonrea_new"],
    name = "Solde quotidien hosp. (hors réa.)",
    marker_color='black',
    mode="lines+markers",
    opacity=0.4
))


# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    legend_orientation="v",
    barmode='relative',
    title={
                'text': "<b>COVID-19 : entrées et sorties en hospitalisation</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'middle'},
                titlefont = dict(
                size=20),
        
    xaxis=dict(
        range=["2020-03-20", (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")  ], # Adding one day
        title='',
        tickformat='%d/%m'),
    yaxis_title="Nb. de personnes",
    
    annotations = [
                dict(
                    x=0.6,
                    y=1.08,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='',
                    font=dict(size=17),
                    showarrow = False),
            
                dict(
                    x=0,
                    y=1.04,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),           
                    showarrow = False)
                ]
                )

name_fig = "entrees_sorties_hosp_rea"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1200, height=800)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()"""


# ## Entrées/Sorties hosp et réa - rolling mean (7 days)
# La moyenne glissante sur 4 jours permet de lisser les effets liés aux week-ends (moins de saisies de données, donc il y a un trou) et d'évaluer la tendance.

# In[34]:


"""try:
    for (rge_x, rge_y, suffix) in [(["2020-03-21", last_day_plot], [-2500, 3700], ""), (["2020-06-10", last_day_plot], [-1000, 1000], "_recent")]:
        fig = go.Figure()
        #fig = make_subplots(specs=[[{"secondary_y": True}]])
        incid_rea = df_new_tot_last15["incid_rea"].rolling(window=7, center=True).mean()
        fig.add_trace(go.Bar(
            x = df_new_tot_last15["jour"],
            y = incid_rea,
            name = "Admissions réanimation",
            marker_color='red',
            opacity=0.8
        ))
        incid_hosp_nonrea = df_new_tot_last15["incid_hosp_nonrea"].rolling(window=7, center=True).mean()
        fig.add_trace(go.Bar(
            x = df_new_tot_last15["jour"],
            y = incid_hosp_nonrea,
            name = "Admissions hospitalisation (hors réa.)",
            marker_color='red',
            opacity=0.5
        ))

        incid_dep_rea = -df_new_tot_last15["incid_dep_rea"].rolling(window=7, center=True).mean().abs()
        fig.add_trace(go.Bar(
            x = df_new_tot_last15["jour"],
            y = incid_dep_rea,
            name = "Sorties réanimation",
            marker_color='green',
            opacity=0.8
        ))

        incid_dep_hosp_nonrea = -df_new_tot_last15["incid_dep_hosp_nonrea"].rolling(window=7, center=True).mean().abs()
        fig.add_trace(go.Bar(
            x = df_new_tot_last15["jour"],
            y = incid_dep_hosp_nonrea,
            name = "Sorties hospitalisation (hors réa.)",
            marker_color='green',
            opacity=0.5
        ))

        fig.add_trace(go.Scatter(
            x = df_france["jour"],
            y = df_france["rea_new"].rolling(window=7, center=True).mean(),
            name = "Solde réanimation",
            marker_color='black',
            mode="lines+markers",
            opacity=0.8
        ))

        fig.add_trace(go.Scatter(
            x = df_france["jour"],
            y = df_france["hosp_nonrea_new"].rolling(window=7, center=True).mean(),
            name = "Solde hosp. (hors réa.)",
            marker_color='black',
            mode="lines+markers",
            opacity=0.4
        ))

        fig.update_layout(
            legend_orientation="h",
            margin=dict(
                    l=20,
                    r=200,
                    b=100,
                    t=100,
                    pad=0
                ),
            barmode='relative',
            title={
                        'text': "<b>COVID-19 : entrées et sorties en hospitalisation</b>",
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'middle'},
                        titlefont = dict(
                        size=20),

            xaxis=dict(
                range=rge_x, # Adding one day
                title='',
                tickformat='%d/%m'),
            yaxis=dict(title="Nb. de personnes",
                       range=rge_y
                      ),

            annotations = [
                        dict(
                            x=0.6,
                            y=1.08,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            text='moyenne mobile centrée sur 7 jours',
                            font=dict(size=17),
                            showarrow = False),

                        dict(
                            x=0,
                            y=1.04,
                            xref='paper',
                            yref='paper',
                            text='Date : {}. Source : Santé publique France et CSSE. Auteur : GRZ - covidtracker.fr'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),           
                            showarrow = False)
                        ]
                        )

        fig['layout']['annotations'] += (dict(
                    x=dates[-4], y = incid_rea.values[-4], # annotation point
                    xref='x1', 
                    yref='y1',
                    text=" <b> {}</b> {}".format(math.trunc(round(incid_rea.values[-4], 1)), "admissions en<br> &#8205;  réanimation"),
                    xshift=10,
                    xanchor="left",
                    align='left',
                    font=dict(
                        color="rgba(255,0,0,1)",
                        size=14
                        ),
                    opacity=1,
                    ax=70,
                    ay=-20,
                    arrowcolor="rgba(255,0,0,1)",
                    arrowsize=1.5,
                    arrowwidth=1,
                    arrowhead=4,
                    showarrow=True
                ),)
        fig['layout']['annotations'] += (dict(
                    x=dates[-4], y = incid_hosp_nonrea.values[-4], # annotation point
                    xref='x1', 
                    yref='y1',
                    text=" <b> {}</b> {}".format(math.trunc(round(incid_hosp_nonrea.values[-4], 1)), "admissions en<br> &#8205; autre hospitalisation"),
                    xshift=10,
                    xanchor="left",
                    align='left',
                    font=dict(
                        color="rgba(255,0,0,0.6)",
                        size=14
                        ),
                    ax=70,
                    ay=-50,
                    arrowcolor="rgba(255,0,0,0.6)",
                    arrowsize=1.5,
                    arrowwidth=1,
                    arrowhead=4,
                    showarrow=True
                ),)
        fig['layout']['annotations'] += (dict(
                    x=dates[-4], y = incid_dep_rea.values[-4], # annotation point
                    xref='x1', 
                    yref='y1',
                    text=" <b>{}</b> {}".format(math.trunc(round(incid_dep_rea.dropna().values[-1], 1)), "sorties en<br> &#8205;  réanimation"),
                    xshift=10,
                    xanchor="left",
                    align='left',
                    font=dict(
                        color="green",
                        size=14
                        ),
                    opacity=1,
                    ax=70,
                    ay=20,
                    arrowcolor="green",
                    arrowsize=1.5,
                    arrowwidth=1,
                    arrowhead=4,
                    showarrow=True
                ),)
        fig['layout']['annotations'] += (dict(
                    x=dates[-4], y = incid_dep_hosp_nonrea.values[-4], # annotation point
                    xref='x1', 
                    yref='y1',
                    text=" <b>{}</b> {}".format(math.trunc(round(incid_dep_hosp_nonrea.dropna().values[-1], 1)), "sorties en<br> &#8205; autre hospitalisation"),
                    xshift=10,
                    xanchor="left",
                    align='left',
                    font=dict(
                        color="rgba(0,128,0,0.6)",
                        size=14
                        ),
                    ax=70,
                    ay=50,
                    arrowcolor="rgba(0,128,0,0.6)",
                    arrowsize=1.5,
                    arrowwidth=1,
                    arrowhead=4,
                    showarrow=True
                ),)

        name_fig = "entrees_sorties_hosp_rea_ROLLING{}".format(suffix)
        fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1200, height=800)

        fig.update_layout(
            annotations = [
                        dict(
                            x=0.5,
                            y=1.05,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                            showarrow = False
                        )]
                         )
        plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        print("> " + name_fig)
        if show_charts:
            fig.show()
            
except Exception as e:
    import traceback
    traceback.print_exc()"""


# ## Hospitalisations (bar chart)

# In[35]:


"""fig = go.Figure()

fig = px.bar(df_france, x='jour', y='hosp',
             color='hosp_new',
             labels={'hosp_new':'Solde hospitalisations'}, color_continuous_scale=["green", "#ffc832", "#cf0000"], range_color=(-2500, 2500))



# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    barmode='group',
    bargap=0,
    yaxis=dict(
        range=[0, 45000]),
    title={
                'text': "COVID19 : <b>nombre de personnes hospitalisées</b>",
                'y':0.97,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                    family="Roboto",
                    size=30),
    xaxis=dict(
        range=["2020-03-15", "2020-04-25"],
        title='',
        tickformat='%d/%m',
        nticks=50
    ),
    yaxis_title="Nb. de personnes",
    
    annotations = [
                dict(
                    x=0.01,
                    y=0.99,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "hosp_bar"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1400, height=800)

fig.update_layout(
    legend_orientation="h",
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)

if show_charts:
    fig.show()"""


# In[36]:


date_plus_6 = (datetime.strptime(dates_incid[-1], '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')

df_tests_viros_france = df_tests_viros.groupby(['jour', 'cl_age90']).sum().reset_index()

#Hosp clage
df_clage_france_individuels = df_clage_france[df_clage_france["cl_age90"] > 1]

for (data_type, data_type_title, marker_color, fillcolor, descr) in [("hosp", "Nombre de personnes hospitalisées pour", "rgb(209, 102, 21)", "rgba(209, 102, 21,0.3)", ""), 
                                     ("rea", "Nombre de personnes en réanimation pour", 'rgb(201, 4, 4)', 'rgba(201, 4, 4, 0.3)', ""), 
                                     ("dc", "Nombre de décès quotidiens pour", "black", "rgba(0,0,0,0.3)", ""),
                                     ("P", "Nombre de cas positifs quotidiens pour", "rgb(8, 115, 191)", "rgba(8, 115, 191, 0.3)", ""),
                                     ("tP", "Taux de positivité du", "rgb(8, 115, 191)", "rgba(8, 115, 191, 0.3)", "% de tests positifs"),
                                     ("tauxDepistage", "Taux de dépistage du", "rgb(8, 115, 191)", "rgba(8, 115, 191, 0.3)", "nb de tests sur 7j/100k hab.")]:
    clages = [9, 19, 29, 39, 49, 59, 69, 79, 89, 90]
    
    fig = make_subplots(rows=2, cols=5, shared_yaxes=False, specs=[[{"secondary_y": True}]*5]*2, subplot_titles=[str(clage-9) + " - " + str(clage) + " ans" for clage in clages[:-1]] + ["> 90 ans"], vertical_spacing = 0.15, horizontal_spacing = 0.05)

    i, j = 1, 1
    for clage in clages:
        
        
        
        if (data_type == "P"):
            data_temp = df_tests_viros_france[df_tests_viros_france["cl_age90"]==clage]
            
            if (data_type == "tP"):
                y = (data_temp["P"]/data_temp["T"]).rolling(window=7).mean()*100
                
            else:
                y = data_temp[data_type].rolling(window=7).mean()

            legend=False
            if clage == clages[0]:
                legend=True
            
            fig.add_trace(go.Scatter(x = data_temp["jour"], y = y, line_width=3, name = "Cas positifs", 
                                     showlegend=legend, 
                                     marker_color=marker_color, 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=True)
            
            last_date = data_temp["jour"].values[-1]
            last_val = y.values[-1]
            fig.add_trace(go.Scatter(x = [last_day], y = [last_val], line_width=3, name = "Cas positifs", 
                                     showlegend=False, 
                                     marker_color="rgba(255, 255, 255, 0.6)", 
                                     marker_size=12,
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=True)
            
            fig.add_trace(go.Scatter(x = [data_temp["jour"].values[-1]], y = [y.values[-1]], line_width=3, name = "Cas positifs", 
                                     showlegend=False, 
                                     marker_size=8,
                                     marker_color=marker_color, 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=True)
            
            fig.add_trace(go.Bar(x = data_temp["jour"], y = data_temp["T"].rolling(window=7).mean(),
                                 name = "Tests réalisés", 
                                 showlegend=legend, 
                                 marker_color='grey'), row=i, col=j, secondary_y=False )
            
        elif (data_type == "tP"):
            data_temp = df_tests_viros_france[df_tests_viros_france["cl_age90"]==clage]
            
            y = (data_temp["P"]/data_temp["T"]).rolling(window=7).mean()*100

            legend=False
            
            fig.add_trace(go.Scatter(x = data_temp["jour"], y = y, line_width=3, name = "Cas positifs", 
                                     showlegend=legend, 
                                     marker_color=marker_color, 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=False)
            
            last_date = data_temp["jour"].values[-1]
            last_val = y.values[-1]
            fig.add_trace(go.Scatter(x = [last_day], y = [last_val], line_width=3, name = "Taux de positivité", 
                                     showlegend=False, 
                                     marker_color="rgba(255, 255, 255, 0.6)", 
                                     marker_size=12,
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=False)
            
            fig.add_trace(go.Scatter(x = [data_temp["jour"].values[-1]], y = [y.values[-1]], line_width=3, name = "Cas positifs", 
                                     showlegend=False, 
                                     marker_size=8,
                                     marker_color=marker_color, 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=False)
            fig.update_yaxes(ticksuffix="%")
            
            """fig.add_trace(go.Bar(x = data_temp["jour"], y = data_temp["P"].rolling(window=7).mean(),
                                 name = "Tests positifs", 
                                 showlegend=legend, 
                                 marker_color='blue'), row=i, col=j, secondary_y=False )
            
            fig.add_trace(go.Bar(x = data_temp["jour"], y = data_temp["T"].rolling(window=7).mean(),
                                 name = "Tests réalisés", 
                                 showlegend=legend, 
                                 marker_color='grey'), row=i, col=j, secondary_y=False )
                        fig.update_layout(barmode="stack", bargap=0)"""
            
            

        elif (data_type == "tauxDepistage"):
            data_temp = df_tests_viros_france[df_tests_viros_france["cl_age90"]==clage]
            
            y = (data_temp["T"]/data_temp["pop"]).rolling(window=7).sum()*100000

            legend=False
            
            fig.add_trace(go.Scatter(x = data_temp["jour"], y = y, line_width=3, name = "Cas positifs", 
                                     showlegend=legend, 
                                     marker_color=marker_color, 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=False)
            
            last_date = data_temp["jour"].values[-1]
            last_val = y.values[-1]
            fig.add_trace(go.Scatter(x = [last_day], y = [last_val], line_width=3, name = "Taux de positivité", 
                                     showlegend=False, 
                                     marker_color="rgba(255, 255, 255, 0.6)", 
                                     marker_size=12,
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=False)
            
            fig.add_trace(go.Scatter(x = [data_temp["jour"].values[-1]], y = [y.values[-1]], line_width=3, name = "Cas positifs", 
                                     showlegend=False, 
                                     marker_size=8,
                                     marker_color=marker_color, 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j, secondary_y=False)
            fig.update_yaxes(ticksuffix="")
            
        else:
            data_temp = df_clage_france[df_clage_france["cl_age90"]==clage]
            y = data_temp[data_type]
            
            last_day = df_tests_viros_france["jour"].values[-1]
            last_val = y.values[-1]
        
        
            if data_type == "dc":
                y = y.diff().rolling(window=7).mean()

            fig.add_trace(go.Scatter(x = data_temp["jour"], y = y, line_width=5, name = "", 
                                     showlegend=False, 
                                     marker_color=marker_color, 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j)
            
            fig.add_trace(go.Scatter(x = [data_temp["jour"].values[-1]], y = [y.values[-1]], line_width=5, name = "", 
                                     showlegend=False, 
                                     mode="markers",
                                     marker_size=12,
                                     marker_color="rgba(255, 255, 255, 0.6)", 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j)
            
            fig.add_trace(go.Scatter(x = [data_temp["jour"].values[-1]], y = [y.values[-1]], line_width=5, name = "", 
                                     showlegend=False, 
                                     mode="markers",
                                     marker_size=8,
                                     marker_color=marker_color, 
                                     fillcolor=fillcolor,
                                     fill='tozeroy'),
                      i, j)

        fig.update_xaxes(tickformat='%d/%m', nticks=5, range=["2020-07-01", date_plus_6])
        #fig.update_yaxes(range=[0, df_clage_france_individuels[data_type].max()])
        
        """fig['layout']['annotations'] += (dict(
            x = last_day, y = last_val, # annotation point
            xref='x1', 
            yref='y6',
            text=str(last_val),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=20
                ),
            opacity=1,
            ax=-150,
            ay=-75,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)"""

        j += 1
        if j == 6:
            i, j = 2, 1

    fig.add_annotation(
                dict(
                    x=0.5,
                    y=1.24,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='{} Covid19'.format(data_type_title),
                    font=dict(size=30),
                    showarrow = False
                ))
    fig.add_annotation(
                    dict(
                        x=0.5,
                        y=1.1,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text='{} - @guillaumerozier - covidtracker.fr - {}'.format(descr, datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ))
    
    fig.update_layout(
        legend_orientation='h',
        margin=dict(
        l=50,
        r=0,
        b=10,
        t=115,
        pad=0
    )
                 )
    
   

    name_fig = "hosp_clage_" + data_type
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1400, height=600)
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
    print("> " + name_fig)


# ## Hospitalisations et réanimations (bar charts subplot)

# In[37]:


fig = make_subplots(rows=2, cols=1, shared_yaxes=True, subplot_titles=["Nombre de personnes<b> hospitalisées</b>", "Nombre de personnes en <b>réanimation</b>"], vertical_spacing = 0.15, horizontal_spacing = 0.1)

fig1 = px.bar(x=df_france['jour'], y=df_france['hosp'],
             color=df_france['hosp_new'], color_continuous_scale=["green", "#ffc832", "#cf0000"], range_color=(df_france['hosp_new'].min(), df_france['hosp_new'].max())
            )
fig2 = px.bar(x=df_france['jour'], y=df_france['rea'],
             color=df_france['rea_new'], color_continuous_scale=["green", "#ffc832", "#cf0000"], range_color=(-2500, 2500)
            )
trace1 = fig1['data'][0]
trace2 = fig2['data'][0]

"""fig.add_trace(trace1, row=1, col=1)
fig.add_trace(trace2, row=2, col=1)"""

fig.add_trace(go.Bar(x=df_france['jour'], y=df_france['hosp'],
                    marker=dict(color =df_france['hosp_new'], coloraxis="coloraxis1"), ),
              1, 1)
fig.add_trace(go.Bar(x=df_france['jour'], y=df_france['rea'],
                    marker=dict(color =df_france['rea_new'], coloraxis="coloraxis2"), ),
              2, 1)

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=1, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=1, col=1)

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=2, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=2, col=1)


for i in fig['layout']['annotations']:
    i['font'] = dict(size=25)

fig.update_layout(
    margin=dict(
        l=0,
        r=150,
        b=0,
        t=90,
        pad=0
    ),
    bargap=0,
    coloraxis1=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['hosp_new'].max(), cmax=df_france['hosp_new'].max(),
                   colorbar=dict(
                        title="Solde quotidien de<br>pers. hospitalisées<br> &#8205; ",
                        thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="middle", y=0.79, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15))),
    coloraxis2=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['rea_new'].max(), cmax=df_france['rea_new'].max(),
                   colorbar=dict(
                        title="Solde quotidien de<br>pers. en réanimation<br> &#8205; ",
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="middle", y=0.22, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15))), 


                showlegend=False,

)

fig["layout"]["annotations"] += ( dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text='covidtracker.fr - {}'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

name_fig = "hosp_rea_bar"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=1200)

fig["layout"]["annotations"] += (
                dict(
                    x=0.5,
                    y=1,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                    ),
                    )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)


#fig.show()


# ## Indicateur 1 - France

# In[38]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

df_sursaud_france['taux_covid_rolling'] = df_sursaud_france['taux_covid'].rolling(window=7, center=True).mean()
df_sursaud_france['taux_covid_acte_rolling'] = df_sursaud_france['taux_covid_acte'].rolling(window=7, center=True).mean()

fig = make_subplots(rows=2, cols=1, shared_yaxes=True, subplot_titles=["Circulation du Coronavirus<br><sub><b>Taux d'admission aux urgences pour Covid19</b></sub>", "<sub><b>Taux d'actes SOS Médecin pour Covid19</b></sub>"], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}], [{"secondary_y": True}]])

fig.add_trace(go.Bar(x = df_sursaud_france['date_de_passage'], y = df_sursaud_france['nbre_pass_corona'], opacity=0.2, marker_color='red', name = "nombre d'admissions aux urgences • d'actes SOS Médecin <b>pour Covid</b>"),
              1, 1, secondary_y=True)

fig.add_trace(go.Bar(x = df_sursaud_france['date_de_passage'], y = df_sursaud_france['nbre_pass_tot']-df_sursaud_france['nbre_pass_corona'], opacity=0.3, marker_color='grey', name = "<b>nombre total</b> d'admissions aux urgences • d'actes SOS Médecin "),
              1, 1, secondary_y=True)

fig.add_trace(go.Scatter(x = df_sursaud_france['date_de_passage'], y = 100*df_sursaud_france['taux_covid_rolling'], marker_color='red', line_width=5, name = "<b>taux</b> d'admissions aux urgences • d'actes SOS Médecin <b>pour Covid</b>"),
              1, 1)
fig.add_trace(go.Scatter(x = df_sursaud_france['date_de_passage'], y = 100*df_sursaud_france['taux_covid'], mode="markers", marker_color='red', marker_size=4, line_width=5, showlegend=False),
              1, 1)
fig.add_trace(go.Scatter(x = [dates_sursaud[-4]], y = 100*df_sursaud_france.loc[df_sursaud_france["date_de_passage"] == dates_sursaud[-4], 'taux_covid_rolling'], marker_color='red', name = "taux d'actes SOS Médecin pour Covid", mode="markers", marker_size=20,showlegend=False),
              1, 1)

##
fig.add_trace(go.Bar(x = df_sursaud_france['date_de_passage'], y = df_sursaud_france['nbre_acte_corona'], opacity=0.2, marker_color='red', name = "", showlegend=False),
              2, 1, secondary_y=True)

fig.add_trace(go.Bar(x = df_sursaud_france['date_de_passage'], y = df_sursaud_france['nbre_acte_tot']-df_sursaud_france['nbre_acte_corona'], opacity=0.3, marker_color='grey', name = "", showlegend=False),
              2, 1, secondary_y=True)

fig.add_trace(go.Scatter(x = df_sursaud_france['date_de_passage'], y = 100*df_sursaud_france['taux_covid_acte_rolling'], marker_color='red', line_width=5, name = "taux d'actes SOS Médecin pour Covid", showlegend=False),
              2, 1)
fig.add_trace(go.Scatter(x = df_sursaud_france['date_de_passage'], y = 100*df_sursaud_france['taux_covid_acte'], mode="markers", marker_color='red', marker_size=4, line_width=5, showlegend=False),
              2, 1)
fig.add_trace(go.Scatter(x = [dates_sursaud[-4]], y = 100*df_sursaud_france.loc[df_sursaud_france["date_de_passage"] == dates_sursaud[-4], 'taux_covid_acte_rolling'], marker_color='red', name = "taux d'actes SOS Médecin pour Covid", mode="markers", marker_size=20,showlegend=False),
              2, 1)

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=1, col=1)
fig.update_yaxes(title_text="", gridcolor='white', range=[0, 28], linewidth=1, linecolor='white', row=1, col=1, secondary_y=False)
fig.update_yaxes(range=[0, 6], row=1, col=1, secondary_y=True, type="log")

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=2, col=1)
fig.update_yaxes(title_text="", gridcolor='white', range=[0, 30], linewidth=1, linecolor='white', row=2, col=1, secondary_y=False)
fig.update_yaxes(range=[0, 5], row=2, col=1, secondary_y=True, type="log")

for i in fig['layout']['annotations']:
    i['font'] = dict(size=30)
    
y_val = 100*df_sursaud_france.loc[df_sursaud_france['date_de_passage']=='2020-03-28','taux_covid_rolling'].values[0]
fig['layout']['annotations'] += (dict(
        x='2020-03-28', y = y_val, # annotation point
        xref='x1', 
        yref='y1',
        text="   {} % des admissions au urgences<br>   ont concerné le Covid19 le 28 mars".format(round(y_val, 1)),
        xshift=5,
        yshift=5,
        xanchor="left",
        align='left',
        font=dict(
            color="red",
            size=14,
            ),
        ax=0,
        ay=-60,
        arrowcolor="red",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

y_val = 100*df_sursaud_france.loc[df_sursaud_france['date_de_passage']==dates_sursaud[-4],'taux_covid_rolling'].values[0]
fig['layout']['annotations'] += (dict(
        x=dates_sursaud[-4], y = y_val, # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{}</b> %".format(round(y_val, 1)),
        xshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=16,
            ),
        ax=0,
        ay=-25,
        arrowcolor="red",
        opacity=0.8,
        arrowsize=0.3,
        arrowwidth=0.1,
        arrowhead=0
    ),)

y_val = df_sursaud_france.loc[df_sursaud_france['date_de_passage']=='2020-03-28','nbre_pass_tot'].values[0]
fig['layout']['annotations'] += (dict(
        x='2020-03-28', y = math.log10(y_val), # annotation point
        xref='x1', 
        yref='y2',
        text="   Il y a eu {} admissions aux urgences<br>   le {} ".format('{:n}'.format(math.trunc(round(y_val, 1))).replace(',', ' '), '28 mars'),
        xshift=0,
        xanchor="left",
        align='left',
        font=dict(
            color="grey",
            size=14
            ),
        ax=250,
        ay=-30,
        arrowcolor="grey",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

###
y_val = 100*df_sursaud_france.loc[df_sursaud_france['date_de_passage']=='2020-03-28','taux_covid_acte_rolling'].values[0]
fig['layout']['annotations'] += (dict(
        x='2020-03-28', y = y_val, # annotation point
        xref='x2', 
        yref='y3',
        text="   {} % des actes SOS Médecin<br>   ont concerné le Covid19 le 28 mars".format(round(y_val, 1)),
        xshift=10,
        yshift=10,
        align='left',
        xanchor="left",
        font=dict(
            color="red",
            size=14
            ),
        ax=80,
        ay=-50,
        arrowcolor="red",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

y_val = 100*df_sursaud_france.loc[df_sursaud_france['date_de_passage']==dates_sursaud[-4],'taux_covid_acte_rolling'].values[0]
fig['layout']['annotations'] += (dict(
        x=dates_sursaud[-4], y = (y_val), # annotation point
        xref='x2', 
        yref='y3',
        text="<b>{}</b> %".format(round(y_val, 1)),
        xshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=16
            ),
        opacity=0.8,
        ax=0,
        ay=-25,
        arrowcolor="red",
        arrowsize=0.3,
        arrowwidth=0.1,
        arrowhead=0
    ),)

y_val = df_sursaud_france.loc[df_sursaud_france['date_de_passage']=='2020-03-28','nbre_acte_tot'].values[0]
fig['layout']['annotations'] += (dict(
        x='2020-03-28', y = math.log10(y_val), # annotation point
        xref='x2', 
        yref='y4',
        text="   Il y a eu {} actes SOS Médecin <br>   le {} ".format('{:n}'.format(math.trunc(round(y_val, 1))).replace(',', ' '), '28 mars'),
        xshift=0,
        align='left',
        xanchor="left",
        font=dict(
            color="grey",
            size=14
            ),
        ax = 100,
        ay = -10,
        arrowcolor="grey",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

fig.update_layout(
    barmode='stack',
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=90,
        pad=0
    ),
    bargap=0,
    legend_orientation="h",
    showlegend=True,

)
commentaire = "Les points rouges représentent les données brutes quotidiennes. Les lignes rouges sont obtenues en effectuant la moyenne mobile<br>centrée, sur 7 jours. Source : Santé publique France. Auteur : GRZ - <i>covidtracker.fr - {}</i>".format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y'))
fig["layout"]["annotations"] += ( dict(
                        x=0.5,
                        y=-0.05,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text="",
                        #text='guillaumerozier.fr - {}'.format(datetime.strptime(max(dates_sursaud), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),
                    dict(
                        x=0.01,
                        y=-0.05,
                        xref='paper',
                        yref='paper',
                        xanchor='left',
                        yanchor='top',
                        align="left",
                        text=commentaire,
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

fig.add_layout_image(
        dict(
            source="data/covidtracker_logo.jpeg",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=20, sizey=20,
            xanchor="right", yanchor="bottom"
            )
)

name_fig = "indic1_france"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=1400)

fig["layout"]["annotations"] += (
                dict(
                    x=0.5,
                    y=1,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                    ),
                    )


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)

#locale.setlocale(locale.LC_ALL, '')
#fig.show()


# In[39]:


"""
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

incid_rolling = (df_incid_france['p']).rolling(window=7, center=True).mean()
tests_tot_rolling = (df_incid_france['t']).rolling(window=7, center=True).mean()

#fig = go.Figure()
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(x = df_incid_france['jour'], y = incid_rolling, marker_color='red', line_width=5, name = "Nombre de tests positifs", showlegend=True), secondary_y=True
             )

fig.add_trace(go.Scatter(x = df_incid_france['jour'], y = df_incid_france['p'], mode="markers", marker_color='red', marker_size=4, line_width=5, showlegend=False), secondary_y=True
              )
fig.add_trace(go.Scatter(x = [dates_incid[-4]], y = [incid_rolling.values[-4]], marker_color='red', name = "", mode="markers", marker_size=20, showlegend=False), secondary_y=True
             )
fig.add_trace(go.Scatter(x = df_incid_france['jour'], y = tests_tot_rolling, name = "Nombre de tests réalisés", showlegend=True, marker_opacity=0, marker_color='grey', fill='tonexty', fillcolor='rgba(186, 186, 186, 0.4)'), secondary_y=False
             )

fig.update_xaxes(title_text="", gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white')
fig.update_yaxes(title_text="Nombre de tests positifs", range = [0, 1000], gridcolor='white', linewidth=1, linecolor='white', secondary_y=True)
fig.update_yaxes(title_text="Nombre de tests réalisés", range = [0, 40000], linewidth=0, showgrid=False, secondary_y=False)


for i in fig['layout']['annotations']:
    i['font'] = dict(size=30)

fig['layout']['annotations'] += (dict(
        x=dates_incid[-4], y = incid_rolling.values[-4], # annotation point
        xref='x1', 
        yref='y2',
        text="<b>{} personnes sont positives</b> chaque jour<br>en moyenne du {} au {}".format(math.trunc(round(incid_rolling.values[-4], 0)), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=20,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=16,
            ),
        ax=0,
        ay=-50,
        arrowcolor="red",
        opacity=0.7,
        arrowsize=2,
        arrowwidth=1,
        arrowhead=4
    ),
        dict(
        x=dates_incid[-4], y = tests_tot_rolling.values[-4], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{} tests</b> sont réalisés chaque jour<br>en moyenne du {} au {}".format(math.trunc(round(tests_tot_rolling.values[-4], 0)), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="black",
            size=16,
            ),
        ax=0,
        ay=-50,
        arrowcolor="black",
        opacity=0.7,
        arrowsize=2,
        arrowwidth=1,
        arrowhead=6
    ))


fig.update_layout(
    title={
                'text': "Covid-19 : <b>nombre de tests positifs au Covid19</b></b><br><sub>par jour ; tests virologiques uniquement ; moyenne mobile sur 7 j. ; données Santé publique France</sub>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    
    
    margin=dict(
        l=0,
        r=40,
        b=150,
        t=90,
        pad=0
    ),
    bargap=0,
    legend_orientation="h",
    showlegend=True,

)
commentaire = "Les points rouges représentent les données brutes quotidiennes. Les lignes rouges sont obtenues en effectuant la moyenne mobile<br>centrée, sur 7 jours. <i>Guillaume Rozier pour covidtracker.fr - {}</i>".format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y'))
fig["layout"]["annotations"] += (
                    dict(
                        x=0,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='left',
                        yanchor='top',
                        align="left",
                        text=commentaire,
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

fig.add_layout_image(
        dict(
            source="data/covidtracker_logo.jpeg",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=20, sizey=20,
            xanchor="right", yanchor="bottom"
            )
) 

name_fig = "incidence_france"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=900)

fig["layout"]["annotations"] += (
                dict(
                    x=0.5,
                    y=1,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                    ),
                    )


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)

locale.setlocale(locale.LC_ALL, '')
#fig.show()"""


# ## Tests France

# In[40]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

incid_rolling = (df_incid_france['P']).rolling(window=7, center=False).mean()
tests_tot_rolling = (df_incid_france['T']).rolling(window=7, center=False).mean()
taux = (df_incid_france['P']/df_incid_france['T']*100).rolling(window=7, center=False).mean()

if taux.dropna().values[-1] > 5:
    clr = "red"
elif taux.dropna().values[-1] > 1:
    clr = "darkorange"
else:
    clr = "green"

#fig = go.Figure()
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Bar(x = df_incid_france["jour"], y = incid_rolling, marker_color='rgba(252, 19, 3, 0.5)', showlegend = False),
                  secondary_y=False)
fig.add_trace(go.Bar(x = df_incid_france['jour'], y = tests_tot_rolling-incid_rolling, name = "Nombre de tests réalisés", showlegend = False, marker_color ='rgba(186, 186, 186, 0.5)'),
              secondary_y=False)
fig.add_trace(go.Scatter(x = df_incid_france['jour'], y = taux, name = "Taux de tests positifs", showlegend = False, marker_opacity=0, line_width = 10, marker_color=clr),
              secondary_y=True)
fig.add_trace(go.Scatter(x = [df_incid_france['jour'].values[-1]], y = [taux.values[-1]], name = "Taux de tests positifs", mode='markers', marker_size=25, showlegend = False, marker_color=clr),
              secondary_y=True)

#fig.add_trace(go.Scatter(x = [data_dep["jour"].values[-2]], y = [data_dep[data_dep["jour"] == data_dep["jour"].values[-2]]["incid_rolling"].values[-1]], line_color=clr, mode="markers", marker_size=15, marker_color=clr),
             # i, j, secondary_y=False)

date_plus_1 = (datetime.strptime(dates_incid[-1], '%Y-%m-%d') + timedelta(days=2)).strftime('%Y-%m-%d')

fig.update_xaxes(title_text="", range=["2020-05-18", date_plus_1],gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=30), tickangle=0, linewidth=0, linecolor='white')
#fig.update_yaxes(title_text="", range=[0, 5], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j, secondary_y=True)
fig.update_yaxes(title_text="", titlefont=dict(size=30),gridcolor='white', linewidth=0, ticksuffix=" tests", linecolor='white', tickfont=dict(size=30), nticks=8, secondary_y=False) #, type="log"
fig.update_yaxes(title_text="", titlefont=dict(size=30, color="blue"), ticksuffix=" %", range=[0, taux.max()*1.5], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=30, color=clr), nticks=8,  secondary_y=True)

for i in fig['layout']['annotations']:
    i['font'] = dict(size=30)

fig['layout']['annotations'] += (dict(
        x=dates_incid[-1], y = incid_rolling.values[-1], # annotation point math.log10(
        xref='x1', 
        yref='y1',
        text="<b>{} tests positifs</b><br>chaque jour<br>".format(math.trunc(round(incid_rolling.values[-1], 1)), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=30,
            ),
        ax=-250,
        ay=-150,
        arrowcolor="red",
        opacity=0.8,
        arrowsize=1,
        arrowwidth=3,
        arrowhead=0
    ),
    dict(
        x=dates_incid[-1], y = taux.values[-1], # annotation point
        xref='x1', 
        yref='y2',
        text="<b>{} %</b> des tests<br>sont <b>positifs</b>".format(str(round(taux.values[-1],2)).replace(".", ","), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=15,
        xanchor="center",
        align='center',
        font=dict(
            color=clr,
            size=30,
            ),
        ax=-300,
        ay=-160,
        arrowcolor=clr,
        opacity=1,
        arrowsize=1,
        arrowwidth=4,
        arrowhead=4
    ),
        dict(
        x=dates_incid[-1], y = tests_tot_rolling.values[-1], # annotation point math.log10(
        xref='x1', 
        yref='y1',
        text="<b>{} tests</b> sont réalisés<br>chaque jour<br>".format(math.trunc(round(tests_tot_rolling.values[-1], 0)), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="black",
            size=30,
            ),
        ax=-170,
        ay=-90,
        arrowcolor="black",
        opacity=0.7,
        arrowsize=1,
        arrowwidth=3,
        arrowhead=0
    ))


fig.update_layout(
    barmode="stack",
    paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
    plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
    title={
                'text': "",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    
    
    margin=dict(
        l=30,
        r=0,
        b=1000,
        t=32,
        pad=0
    ),
    bargap=0,
    legend_orientation="h",
    showlegend=True,

)
commentaire = "Mis à jour : {}.<br><br>Les barres rouges représentent le nombre de tests virologiques positifs et les barres<br>grises le nombre de tests négatifs (axe de gauche). Les données sont moyennées sur<br>7 jours afin de lisser les irrégularités. La ligne représente le taux de tests<br>positifs (axe de droite).<br>La couleur du trait de positivité dépend de sa valeur (vert si < 1%, rouge si > 5%).<br>Les données proviennent de Santé publique France.<br><br>Plus de graphiques sur covidtracker.fr. Auteur : Guillaume Rozier.".format(now.strftime('%d %B %Y'))
fig["layout"]["annotations"] += (
                    dict(
                        x=-0.08,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='left',
                        yanchor='top',
                        align="left",
                        text = commentaire,
                        showarrow = False,
                        font=dict(size=40), 
                        opacity=0.8
                    ),)


name_fig = "incidence_taux_france"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1700, height=2300)

fig["layout"]["annotations"] += (
                dict(
                    x=0.5,
                    y=1,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                    ),
                    )


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)

locale.setlocale(locale.LC_ALL, '')
#fig.show()


# ## Titre composition tests

# In[41]:


fig = go.Figure()

fig.update_xaxes(title_text="", visible=False)
fig.update_yaxes(title_text="", visible=False)

fig.update_layout(
    paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
    plot_bgcolor='#fffdf5',#f5f0e4 fcf8ed f0e8d5
)

commentaire = "Les points rouges représentent les données brutes quotidiennes. Les lignes rouges sont obtenues en effectuant la moyenne mobile<br>centrée, sur 7 jours. <i>Guillaume Rozier pour covidtracker.fr - {}</i>".format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y'))
fig["layout"]["annotations"] += (
                    dict(
                        x=0.5,
                        y=1.5,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<b>Analyse des tests du COVID-19 en France</b>",
                        showarrow = False,
                        font=dict(size=80), 
                        opacity=0.8
                    ),dict(
                        x=0.25,
                        y=0.2,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<b>À l'échelle nationale</b>",
                        showarrow = False,
                        font=dict(size=60), 
                        opacity=0.8
                    ),
                    dict(
                        x=0.25,
                        y=-0.4,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<sub>Échelle de gauche : nombre de tests</sub>",
                        showarrow = False,
                        font=dict(size=60), 
                        opacity=0.8
                    ),
                    dict(
                        x=0.75,
                        y=0.1,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<b>Dans chaque département</b>",
                        showarrow = False,
                        font=dict(size=60), 
                        opacity=0.8
                    ),
                    dict(
                        x=0.75,
                        y=-0.4,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<sub>Échelle de gauche : nombre de tests pour 100k habitants de chaque département</sub>",
                        showarrow = False,
                        font=dict(size=60), 
                        opacity=0.8
                    ))


name_fig = "title_incidence"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=3400, height=300)
#fig.show()


# ## R_effectif

# In[42]:


#### Calcul du R_effectif

# Paramètres R_effectif
std_gauss= 5
wind = 7
delai = 7

df_sursaud_dep = df_sursaud.groupby(["date_de_passage"]).sum().reset_index()
df_sursaud_dep = df_sursaud_dep.sort_values(by="date_de_passage")
nbre_pass = df_sursaud_dep["nbre_pass_corona"]

# Calcul suivant deux méthodes
df_sursaud_dep['reffectif_urgences'] = (nbre_pass.rolling(window= wind).sum() / nbre_pass.rolling(window = wind).sum().shift(delai) ).rolling(window=7).mean()
df_incid_france['reffectif_tests'] = (df_incid_france['P'].rolling(window= wind).sum() / df_incid_france['P'].rolling(window = wind).sum().shift(delai) ).rolling(window=7).mean()

# Calcul de la moyenne des deux
df_reffectif = pd.merge(df_sursaud_dep, df_incid_france, left_on="date_de_passage", right_on="jour", how="outer")
df_reffectif['reffectif_mean'] = df_reffectif[['reffectif_urgences', 'reffectif_tests']].mean(axis=1, skipna=False)
df_reffectif['reffectif_var'] = df_reffectif[['reffectif_urgences', 'reffectif_tests']].var(axis=1, skipna=False)

# Résultats
y_data = df_reffectif['reffectif_urgences']
y_data_tests = df_reffectif['reffectif_tests']

#### Construction du graphique
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Ajout R_effectif estimé via les urgences au graph
fig.add_trace(go.Scatter(x = df_reffectif["date_de_passage"], y = y_data.values,
                    mode='lines',
                    line=dict(width=2, color="rgba(96, 178, 219, 0.9)"),
                    name="À partir des données des admissions aux urgences",
                    marker_size=4,
                    showlegend=True
                       ))

# Ajout R_effectif estimé via les tests au graph
fig.add_trace(go.Scatter(x = df_reffectif["date_de_passage"], y = y_data_tests.shift(0).values,
                    mode='lines',
                    line=dict(width=2, color="rgba(108, 212, 141, 0.9)"),
                    name="À partir des données des tests PCR",
                    marker_size=5,
                    showlegend=True
                         ))

# Ajout R_effectif moyen au graph
fig.add_trace(go.Scatter(x = df_reffectif["date_de_passage"], y = df_reffectif['reffectif_mean'],
                    mode='lines',
                    line=dict(width=4, color="rgba(0,51,153,1)"),
                    name="R_effectif moyen",
                    marker_size=4,
                    showlegend=True
                         ))

# Calcul écart-type
y_std = (nbre_pass.rolling(window= wind, win_type="gaussian").sum(std= std_gauss) / nbre_pass.rolling(window = wind, win_type="gaussian").sum(std = std_gauss).shift(delai) ).rolling(window=7).std()
y_std_tests = (df_incid_france['T'].rolling(window= wind, win_type="gaussian").sum(std= std_gauss) / df_incid_france['T'].rolling(window = wind, win_type="gaussian").sum(std = std_gauss).shift(delai) ).rolling(window=7).std()

# Ajout du collier écart-type
fig.add_trace(go.Scatter(x = df_reffectif["jour"], y = df_reffectif['reffectif_tests'],
                    mode='lines',
                    line=dict(width=0),
                    name="",
                    marker_size=8,
                    showlegend=False
                            ))

fig.add_trace(go.Scatter(x = df_reffectif["jour"].values[101:], y = df_reffectif['reffectif_urgences'].values[101:],
                    mode='lines',
                    line=dict(width=0),
                    name="",
                    marker_size=100,
                    showlegend=False,
                    fill = 'tonexty', fillcolor='rgba(0,51,153,0.1)'
                            ))
# Mis en valeur de la dernière valeur du R_effectif
reffectif_now = df_reffectif[df_reffectif["date_de_passage"] == df_reffectif["jour"].dropna().max()]["reffectif_mean"].values[-1]
fig.add_trace(go.Scatter(x = [df_reffectif["jour"].dropna().max()], y = [reffectif_now],
                    mode='markers',
                    name="",
                    line=dict(width=4, color="rgba(0,51,153,1)"),
                    marker_color='rgba(0,51,153,1)',
                    marker_size=12,
                    showlegend=False
                            ))
# Modification du layout
fig.update_layout(
    margin=dict(
            l=0,
            r=0,
            b=0,
            t=80,
            pad=0
        ),
    legend_orientation="h",
    title={
                'text': "Estimation du <b>taux de reproduction R<sub>effectif</sub></b><br><sub>Différence entre le nb de suspicion Covid19 aux urgences à 7 jours d'intervalle (moyenne mobile de 7j)".format(),
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    annotations = [
                dict(
                    x=0.5,
                    y=-0.12,
                    xref='paper',
                    yref='paper',
                    opacity=0.8,
                    text='Date : {}. Source : Santé publique France. Auteur : Guillaume Rozier - covidtracker.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="", range=["2020-03-17", last_day_plot])
fig.update_yaxes(title="", range=[0, 3], secondary_y=False)

# Ajout de zones de couleur
fig.add_shape(
        # filled Rectangle
            type="rect",
            x0="2020-03-15",
            y0=1,
            x1=last_day_plot,
            y1=1,
            line=dict(
                color="orange",
                width=1,
                dash="dot"
            ),
            opacity=0.8
        )

fig.add_shape(
        # filled Rectangle
            type="rect",
            x0="2020-03-15",
            y0=1.5,
            x1=last_day_plot,
            y1=1.5,
            line=dict(
                color="red",
                width=1,
                dash="dot"
            ),
            opacity=0.8
        )

if reffectif_now < 1:
    comm_epid = "donc l'épidémie régresse"
else:
    comm_epid = "donc l'épidémie s'aggrave"
    

fig['layout']['annotations'] += (dict(
        x= df_reffectif["jour"].dropna().max(), y = reffectif_now, # annotation point
        xref='x1', 
        yref='y1',
        text="<b>Un malade contamine {}<br>autres personnes</b> en moyenne,<br>{}".format(str(round(reffectif_now, 2)).replace('.', ','), comm_epid),
        xshift=-5,
        yshift=10,
        xanchor="center",
        align='center',
        font=dict(
            color="rgba(0,51,153,1)",
            size=15
            ),
        opacity=1,
        ax=-170,
        ay=-150,
        arrowcolor="rgba(0,51,153,1)",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

name_fig = "reffectif"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[43]:


df_tests_viros_france = df_tests_viros.groupby(['jour', 'cl_age90']).sum().reset_index()
df_tests_viros_france = df_tests_viros_france[df_tests_viros_france['cl_age90'] != 0]


#df_essai = df_tests_viros_france.groupby(['cl_age90', 'jour']).sum().rolling(window=20).mean()
df_tests_rolling = pd.DataFrame()
array_positif= []
array_taux= []
array_incidence=[]
for age in list(dict.fromkeys(list(df_tests_viros_france['cl_age90'].values))):
    df_temp = pd.DataFrame()
    df_tests_viros_france_temp = df_tests_viros_france[df_tests_viros_france['cl_age90'] == age]
    df_temp['jour'] = df_tests_viros_france_temp['jour']
    df_temp['cl_age90'] = df_tests_viros_france_temp['cl_age90']
    df_temp['P'] = (df_tests_viros_france_temp['P']).rolling(window=7).mean()
    df_temp['T'] = (df_tests_viros_france_temp['T']).rolling(window=7).mean()
    df_temp['P_taux'] = (df_temp['P']/df_temp['T']*100)
    df_tests_rolling = pd.concat([df_tests_rolling, df_temp])
    df_tests_rolling.index = pd.to_datetime(df_tests_rolling["jour"])
    #tranche = df_tests_rolling[df_tests_rolling["cl_age90"]==age]
    tranche = df_tests_viros_france[df_tests_viros_france["cl_age90"]==age]
    tranche.index = pd.to_datetime(tranche["jour"])
    tranche = tranche[tranche.index.max() - timedelta(days=7*18-1):].resample('7D').sum()
    array_positif += [tranche["P"].astype(int)]
    array_taux += [np.round(tranche["P"]/tranche["T"]*100, 1)]
    array_incidence += [np.round(tranche["P"]/tranche["pop"]*7*100000,0).astype(int)]
    
    dates_heatmap = list(tranche.index.astype(str).values)
df_tests_rolling = df_tests_rolling[df_tests_rolling['jour'] > "2020-05-18"]
df_tests_rolling['cl_age90'] = df_tests_rolling['cl_age90'].replace(90,99)

dates_heatmap_firstday = tranche.index.values
dates_heatmap_lastday = tranche.index + timedelta(days=6)
dates_heatmap = [str(dates_heatmap_firstday[i])[8:10] + "/" + str(dates_heatmap_firstday[i])[5:7] + "<br>" + str(dates_heatmap_lastday[i])[8:10] + "/" + str(dates_heatmap_lastday[i])[5:7] for i, val in enumerate(dates_heatmap_firstday)]


# In[44]:


temp = df_tests_viros_france.groupby(["jour"]).sum().reset_index()


# In[45]:


for (val, valname) in [('P', 'positifs'), ('T', '')]:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==9][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[0]),
        stackgroup='one',
        groupnorm='percent', # sets the normalization for the sum of the stackgroup,
        name="0 à 9 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==19][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[1]),
        stackgroup='one',
        name="10 à 19 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==29][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[2]),
        stackgroup='one',
        name="20 à 29 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==39][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[3]),
        stackgroup='one',
        name="30 à 39 ans"
    ))

    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==49][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[4]),
        stackgroup='one',
        name="40 à 49 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==59][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[5]),
        stackgroup='one',
        name="50 à 59 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==69][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[6]),
        stackgroup='one',
        name="60 à 69 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==79][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[7]),
        stackgroup='one',
        name="70 à 79 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==89][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[8]),
        stackgroup='one',
        name = "80 à 89 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==99][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[9]),
        stackgroup='one',
        name="90+ ans"
    ))

    fig.update_layout(
        annotations = [
                    dict(
                        x=0,
                        y=1.05,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
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
                'text': "Répartition des tests{} réalisés en fonction de l'âge".format(" "+valname),
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
    name_fig = "repartition_age_tests{}".format(valname)
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[46]:


import plotly.figure_factory as ff

for (name, array, title, scale_txt, data_example, digits) in [("cas", array_positif, "Nombre de <b>tests positifs</b>", "", "", 0), ("taux", array_taux, "Taux de <b>positivité</b>", "%", "%", 1), ("incidence", array_incidence, "Taux d'<b>incidence</b>", " cas", " cas", 1)]: #
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    fig = ff.create_annotated_heatmap(
            z=array, #df_tests_rolling[data].to_numpy()
            x=dates_heatmap,
            y=[str(x-9) + " à " + str(x)+" ans" if x!=99 else "+ 90 ans" for x in range(9, 109, 10)],
            showscale=True,
            coloraxis="coloraxis",
            #text=df_tests_rolling[data],
            font_colors=["white", "white"],
            annotation_text = array
            )
    
    annot = []

    #fig.update_xaxes(title_text="", tickformat='%d/%m', nticks=20, ticks='inside', tickcolor='white')
    fig.update_xaxes(side="bottom", tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=9))
    #fig.update_yaxes(title_text="Tranche d'âge", ticksuffix=" ans", ticktext=["< 10", "10 - 20", "20 - 30", "30 - 40", "40 - 50", "50 - 60", "60 - 70", "70 - 80", "80 - 90", "> 90"], tickmode='array', tickvals=[9, 19, 29, 39, 49, 59, 69, 79, 89, 99], tickcolor="white")
    annots = annot + [
                    dict(
                        x=0.5,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        opacity=0.6,
                        font=dict(color="black", size=10),
                        text='Lecture : une case correspond au {} pour une tranche d\'âge (à lire à gauche) et à une date donnée (à lire en bas).<br>Du rouge correspond à un {} élevé.  <i>Date : {} - Source : covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                        showarrow = False
                    ),
                ]
    
        
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 11
        
    for annot in annots:
        fig.add_annotation(annot)
        
    if name == "incidence":
        cmax = 800
    elif name == "cas":
        cmax = 28000
    elif name == "taux":
        cmax = 18
        
    fig.update_layout(
        title={
            'text': "{} du Covid19 en fonction de l\'âge".format(title.replace("<br>", " ")),
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
            size=20),
        coloraxis=dict(
            cmin=0, cmax=cmax,
            colorscale = [[0, "green"], [0.08, "#ffcc66"], [0.25, "#f50000"], [0.5, "#b30000"], [1, "#3d0000"]],
            colorbar=dict(
                #title="{}<br>du Covid19<br> &#8205;".format(title),
                thicknessmode="pixels", thickness=8,
                lenmode="pixels", len=200,
                yanchor="middle", y=0.5,
                tickfont=dict(size=9),
                ticks="outside", ticksuffix="{}".format(scale_txt),
                )
        ),
        
    margin=dict(
                    b=80,
                    t=40,
                    pad=0
                ))

    name_fig = "heatmap_"+name
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[47]:


"""#OLD HEATMAP
for (name, data, title, scale_txt, data_example, digits) in [("cas", 'P', "Nombre de<br>tests positifs", "", "", 0), ("taux", 'P_taux', "Taux de<br>positivité", "%", "%", 1)]:
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    fig = go.Figure(data=go.Heatmap(
            z=df_tests_rolling[data],
            x=df_tests_rolling['jour'],
            y=df_tests_rolling['cl_age90'],
            coloraxis="coloraxis"
            ))

    #fig['layout']['annotations'] += (,)
    
    annot = []
    
        
    for cl_age in range(9, 109, 10):
        val = round(df_tests_rolling.loc[(df_tests_rolling["cl_age90"]==cl_age) & (df_tests_rolling["jour"]==df_tests_rolling["jour"].max()), data].values[0], digits)
    
        if digits == 0:
            val = math.trunc(val)
        
        annot += [dict(
                    x=df_tests_rolling['jour'].max(), y = cl_age, # annotation point
                    xref='x1', 
                    yref='y1',
                    text="{}{}".format(str(val).replace(".", ","), data_example),
                    xshift=0,
                    xanchor="center",
                    align='left',
                    font=dict(
                        color="black",
                        size=10
                        ),
                    opacity=0.6,
                    ax=20,
                    ay=0,
                    arrowcolor="black",
                    arrowsize=0.7,
                    arrowwidth=0.6,
                    arrowhead=4,
                    showarrow=True
                )]

    fig.update_xaxes(title_text="", tickformat='%d/%m', nticks=20, ticks='inside', tickcolor='white')
    fig.update_yaxes(title_text="Tranche d'âge", ticksuffix=" ans", ticktext=["< 10", "10 - 20", "20 - 30", "30 - 40", "40 - 50", "50 - 60", "60 - 70", "70 - 80", "80 - 90", "> 90"], tickmode='array', tickvals=[9, 19, 29, 39, 49, 59, 69, 79, 89, 99], tickcolor="white")
    fig.update_layout(
        title={
            'text': "{} du Covid19 en fonction de l\'âge".format(title.replace("<br>", " ")),
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
            size=20),
        coloraxis=dict(
            #cmin=0, cmax=100,
            colorscale='Inferno',
            colorbar=dict(
                #title="{}<br>du Covid19<br> &#8205;".format(title),
                thicknessmode="pixels", thickness=12,
                lenmode="pixels", len=300,
                yanchor="middle", y=0.5,
                tickfont=dict(size=9),
                ticks="outside", ticksuffix="{}".format(scale_txt),
                )
        ),
        annotations = annot + [
                    dict(
                        x=0.5,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        opacity=0.6,
                        font=dict(color="black", size=12),
                        text='Lecture : une case correspond au {} pour une tranche d\'âge (à lire à gauche) et à une date donnée (à lire en bas).<br>Du orange correspond à un {} élevé.  <i>Date : {} - Source : covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                        showarrow = False
                    ),
                ],
    margin=dict(
                    b=80,
                    t=40,
                    pad=0
                ))

    name_fig = "heatmap_"+name
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)"""


# In[48]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

y_vals = df_france['rea']/df_france['LITS']*100
clrs_dep = []

for val in y_vals.values:
    if val < 60:
        clrs_dep += ["green"]
    elif val < 100:
        clrs_dep += ["orange"]
    else:
        clrs_dep += ["red"]
    
fig = go.Figure()

fig.add_shape(
            type="line",
            x0="2000-01-01",
            y0=100,
            x1="2030-01-01",
            y1=100,
            opacity=1,
            fillcolor="orange",
            line=dict(
                color="red",
                width=1,
            )
        )
"""fig.add_shape(
            type="line",
            x0="2000-01-01",
            y0=100,
            x1="2030-01-01",
            y1=100,
            opacity=1,
            fillcolor="red",
            line=dict(
                color="red",
                width=1,
            )
        )
fig.add_shape(
            type="line",
            x0="2000-01-01",
            y0=80,
            x1="2030-01-01",
            y1=80,
            opacity=1,
            fillcolor="red",
            line=dict(
                color="red",
                width=1,
                dash="dot",
            )
        )"""

fig.add_trace(go.Bar(x = df_france['jour'], y = y_vals, opacity=0.8, marker_color=clrs_dep, name = "<b>nombre total</b> d'admissions aux urgences • d'actes SOS Médecin ", showlegend=False),)

fig.update_xaxes(title_text="", range=["2020-03-17", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white')
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white')
    
fig['layout']['annotations'] += (dict(
        x= dates[-1], y = y_vals.values[-1], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{}</b> % des lits de réa.<br>sont occupés par des<br>patients Covid19".format(math.trunc(round(y_vals.values[-1], 0) )),
        yshift=8,
        xanchor="center",
        align='center',
        font=dict(
            color=clrs_dep[-1],
            size=15
            ),
        opacity=1,
        ax=-50,
        ay=-100,
        arrowcolor=clrs_dep[-1],
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),
        dict(
        x= "2020-04-08", y = y_vals.values[21], # annotation point
        xref='x1', 
        yref='y1',
        text="&#8205; <br><b>{}</b> % des lits de réa. étaient occupés<br>par des patients Covid19 le 8 avril".format(math.trunc(round(y_vals.values[21], 0)) ),
        yshift=8,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=16
            ),
        opacity=1,
        ax=0,
        ay=-60,
        arrowcolor="red",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),
    dict(
        x=0.48,
        y=1.09,
        xref='paper',
        yref='paper',
        xanchor='center',
        text='par rapport au nombre de lits de réa. en France fin 2018 (DREES)',
        font=dict(size=15),
        showarrow = False)
                                
                                )

fig.update_layout(
    title={
                'text': "<b>Saturation des services de réanimation</b> par les patients Covid19",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'middle'},
                titlefont = dict(
                size=20),
    margin=dict(
        l=0,
        r=25,
        b=0,
        t=100,
        pad=0
    ),
    bargap=0,
    legend_orientation="h",
    showlegend=True,

)

fig["layout"]["annotations"] += (
                dict(
                    x=0,
                    y=1.03,
                    xref='paper',
                    yref='paper',
                    font=dict(size=9),
                    text='Date : {}. Source : Santé publique France et DREES. Auteur : @guillaumerozier - covidtracker.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),)
            

name_fig = "indic2_france"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)

fig["layout"]["annotations"] += (
                dict(
                    x=0.5,
                    y=1,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                    ),
                    )

print("> " + name_fig)


locale.setlocale(locale.LC_ALL, '')
#fig.show()


# In[49]:


"""
fig = make_subplots(rows=2, cols=1, shared_yaxes=True, subplot_titles=["Nombre de personnes<b> hospitalisées</b><br>(moyenne mobile 7 jours)", "Nombre de personnes en <b>réanimation</b><br> (moyenne mobile 7 jours)"], vertical_spacing = 0.15, horizontal_spacing = 0.1)

##
fig.add_trace(go.Bar(x=df_france['jour'], y=df_france['hosp'].rolling(window=7, center=True).mean(),
                    marker=dict(color =df_france['hosp_new'].rolling(window=7, center=True).mean(), coloraxis="coloraxis1"), ),
              1, 1)
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['hosp'],
                    mode="markers",
                    marker_size=8,
                    marker_symbol="x-thin",
                    marker_line_color="Black", marker_line_width=0.7, opacity=0.5),
              1, 1)
##
fig.add_trace(go.Bar(x=df_france['jour'], y=df_france['rea'].rolling(window=7, center=True).mean(),
                    marker=dict(color =df_france['rea_new'].rolling(window=7, center=True).mean(), coloraxis="coloraxis2"), ),
              2, 1)
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['rea'],
                    mode="markers",
                    marker_size=8,
                    marker_symbol="x-thin",
                    marker_line_color="Black", marker_line_width=0.7, opacity=0.5),
              2, 1)
##
fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=1, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=1, col=1)

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=2, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=2, col=1)


for i in fig['layout']['annotations']:
    i['font'] = dict(size=25)

fig.update_layout(
    margin=dict(
        l=0,
        r=150,
        b=0,
        t=90,
        pad=0
    ),
    bargap=0,
    coloraxis1=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['hosp_new'].max(), cmax=df_france['hosp_new'].max(),
                   colorbar=dict(
                        title="Solde quotidien de<br>pers. hospitalisées<br> &#8205; ",
                        thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="middle", y=0.79, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15))),
    coloraxis2=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['rea_new'].max(), cmax=df_france['rea_new'].max(),
                   colorbar=dict(
                        title="Solde quotidien de<br>pers. en réanimation<br> &#8205; ",
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="middle", y=0.22, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15))), 


                showlegend=False,

)
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
fig["layout"]["annotations"] += ( dict(
                        x=0.5,
                        y=0.52,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text='Source : Santé publique France - covidtracker.fr - {}'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

name_fig = "hosp_rea_bar_ROLLING"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=1200)

fig["layout"]["annotations"] += (
                dict(
                    x=0.5,
                    y=1,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                    ),
                    )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)


#fig.show()"""


# In[50]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
data= pd.DataFrame()
data["dc_new_r"] = df_france['dc_new'][1:].rolling(window=7, center=True).mean()
data["jour"] = df_france["jour"]

fig = go.Figure()
fig.add_trace(go.Bar(x=df_france.iloc[data.index]['jour'], y=data["dc_new_r"],
                    marker=dict(color = data["dc_new_r"].diff().fillna(method='backfill'), coloraxis="coloraxis"), ))
fig.add_trace(go.Scatter(x=df_france.iloc[data.index]['jour'], y=df_france['dc_new'][1:],
                    mode="markers",
                    marker_size=6,
                    marker_symbol="x-thin",
                    marker_line_color="Black", marker_line_width=0.6, opacity=0.5))

fig.update_xaxes(title_text="", range=["2020-03-24", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white')
fig.update_yaxes(title_text="", range=[0, 700], gridcolor='white', linewidth=1, linecolor='white')

fig.update_layout(
    margin=dict(
        l=0,
        r=150,
        b=0,
        t=90,
        pad=0
    ),
    title={
                'text': "<b>Nombre de décès quotidiens hospitaliers dus au Covid-19</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'middle'},
                titlefont = dict(
                size=20),
    bargap=0,
    coloraxis=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['dc_new'].rolling(window=7, center=True).mean().diff().max(), cmax=df_france['dc_new'].rolling(window=7, center=True).mean().diff().max(),
                   colorbar=dict(
                        title="Variation quotidienne<br>du nombre de<br>nouveaux décès<br> &#8205; ",
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=300,
                        yanchor="middle", y=0.5, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=8),
                        titlefont=dict(size=10))), 


                showlegend=False,

)


fig["layout"]["annotations"] += ( dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text='guillaumerozier.fr - {}'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0
                    ),
                                dict(
                        x=0.56,
                        y=1.08,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        text='moyenne mobile centrée sur 7 jours pour lisser les week-ends - Données Santé publique France - covidtracker.fr',
                        font=dict(size=15),
                        showarrow = False),)

fig.add_layout_image(
        dict(
            source="https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/covidtracker_logo_text.jpeg",
            xref="paper", yref="paper",
            x=1.15, y=1.1,
            sizex=0.15, sizey=0.15,
            xanchor="right", yanchor="top", opacity=0.8
            )
) 
data_au_max = data[data["jour"] == "2020-04-05"]["dc_new_r"].values
fig['layout']['annotations'] += (dict(
        x= dates[-4], y = data["dc_new_r"].values[-4], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{} décès</b> quotidiens<br>en moyenne sur 7 jours<br>(du {} au {})".format(math.trunc(round(data["dc_new_r"].values[-4], 0) ), datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=1,
        xanchor="center",
        align='center',
        font=dict(
            color = "black",
            size=15
            ),
        opacity=0.7,
        ax=-200,
        ay=-300,
        arrowcolor = "black",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=0
    ),
        dict(
        x= "2020-04-05", y = data_au_max[0], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{} décès</b> quotidiens<br>en moyenne sur 7 jours<br>(du 2 au 8 avril)".format(math.trunc(round(data_au_max[0], 0) )),
        yshift=-10,
        xanchor="center",
        align='center',
        font=dict(
            color = "black",
            size=15
            ),
        opacity=0.7,
        ax=0,
        ay=-100,
        arrowcolor = "black",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=0
    ),
        dict(
        x= dates[-1], y = df_france['dc_new'][1:].values[-1], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{} décès</b><br>le {}".format(math.trunc(round(df_france['dc_new'][1:].values[-1], 0) ), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=5,
        xanchor="center",
        align='center',
        font=dict(
            color = "grey",
            size=15
            ),
        opacity=0.9,
        ax=-25,
        ay=-150,
        arrowcolor = "grey",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ))

name_fig = "dc_new_bar"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)

fig["layout"]["annotations"] += (
                dict(
                    x=0.5,
                    y=1,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                    ),
                    )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)


#fig.show()


# In[51]:




fig = go.Figure()

y = [df_new.sum()["incid_rea"]]
fig.add_trace(go.Bar(x=["Hospitalisations cumulées"], y=y, marker_color="Red", text=str(y[0])+"<br>Réanimations cumulées")).update_xaxes(categoryorder="total descending")

y = [df_new.sum()["incid_dc"]]
fig.add_trace(go.Bar(x=["Décès hosp. cumulés"], y=y, marker_color="Black", text=y)).update_xaxes(categoryorder="total descending")

y = [df_new.sum()["incid_hosp"]-df_new.sum()["incid_rea"]]
fig.add_trace(go.Bar(x=["Hospitalisations cumulées"], y= y, marker_color="Orange", text=str(y[0])+"<br>Autres hospitalisations cumulées")).update_xaxes(categoryorder="total descending")

y = [df_new.sum()["incid_rad"]]
fig.add_trace(go.Bar(x=["Retours à domicile cumulés"], y=y, marker_color="Green", text=y)).update_xaxes(categoryorder="total descending")

fig.update_traces(textposition='auto')

fig.update_layout(
    barmode="stack",
    margin=dict(
        l=0,
        r=150,
        b=0,
        t=90,
        pad=0
    ),
    title={
                'text': "<b>Nombre cumulé de personnes hospitalisées, décédées et guéries du Covid-19</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'middle'},
                titlefont = dict(
                size=20),


                showlegend=False,

)

fig["layout"]["annotations"] += (
                                dict(
                        x=0.56,
                        y=1.08,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        text='Données : Santé publique France  -  guillaumerozier.fr  -  {}'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        font=dict(size=15),
                        showarrow = False),)

name_fig = "sum"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

fig["layout"]["annotations"] += (
                dict(
                    x=0.5,
                    y=1,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                    ),
                    )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)


#fig.show()


# ## Situation cas (bar chart)
# Où en sont les personnes atteintes du Covid (retour à domicile, décédées, en réa, hosp ou autre)

# In[52]:



df_region_sumj = df_region.groupby('jour').sum().reset_index()
df_region_sumj = pd.melt(df_region_sumj, id_vars=['jour'], value_vars=['rad', 'rea', 'dc', 'hosp_nonrea'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['jour'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)
df_bar = df_region_sumj

data = df_bar[df_bar["variable"] == "dc"]
fig = go.Figure(go.Bar(x=data['jour'], y=-data['value'], textposition='auto', name='Décès hosp. cumulés', marker_color='#000000', opacity=0.8))

data = df_bar[df_bar["variable"] == "rea"]
fig.add_trace(go.Bar(x=data['jour'], y=data['value'], textposition='auto', name='Actuellement en réa.', marker_color='#FF0000', opacity=0.8))

data = df_bar[df_bar["variable"] == "hosp_nonrea"]
fig.add_trace(go.Bar(x=data['jour'], y=data['value'], textposition='auto', name="Actuellement en autre hosp.", marker_color='#FFA200', opacity=0.8))

"""if len(df_confirmed[df_confirmed["date"].isin([dates[-1]])]) > 0:
    data = df_confirmed[df_confirmed["date"].isin(dates)].reset_index()
    sum_df = df_bar[df_bar["variable"] == "dc"]['value'].reset_index() + df_bar[df_bar["variable"] == "rea"]['value'].reset_index() +  df_bar[df_bar["variable"] == "hosp_nonrea"]['value'].reset_index() + df_bar[df_bar["variable"] == "rad"]['value'].reset_index()
    fig.add_trace(go.Bar(x=data['date'], y=data['France'] - sum_df['value'], text = data['France'] - sum_df['value'], textposition='auto', name='Non hospitalisés', marker_color='grey', opacity=0.8))
"""
data = df_bar[df_bar["variable"] == "rad"]

fig.add_trace(go.Bar(x=data['jour'], y=data['value'], textposition='auto', name='Retours à domicile cumulés', marker_color='green', opacity=0.8))
fig.update_yaxes(title="Nb. de cas")

fig.update_layout(
            bargap=0,
            legend_orientation="h",
            barmode='relative',
            title={
                'text': "Évolution de la <b>situation des malades</b> du Covid-19",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = dict(
                size=20),
            xaxis=dict(
                title='',
                tickformat='%d/%m',
                ticks="inside"
            ),
            annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)

name_fig = "situation_cas"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)

fig.update_layout(
    bargap=0,
    legend_orientation="h",
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# <br>
# <br>
# <br>
# 
# # Line charts

# ## Décès hospitalisations et réanimations (line chart)

# In[53]:


df_france = df.groupby('jour').sum().reset_index()

#fig = go.Figure()
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['rea'],
                    mode='lines+markers',
                    name="Réanimations", #(<i>axe de gauche</i>)
                    line=dict(width=2),
                    marker_size=8,
                            ))
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['dc'],
                    mode='lines+markers',
                    name="décès hospitaliers cumulés", #(<i>axe de droite</i>)
                    line=dict(width=2),
                    marker_size=8,
                    
                            ),
             #secondary_y=True
             )
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['hosp_nonrea'],
                    mode='lines+markers',
                    name="Autres hospitalisations", #(<i>axe de gauche</i>)
                    line=dict(width=2),
                    marker_size=8,
                            ))
    
#fig = px.line(, color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    legend_orientation="v",
    title={
                'text': "Nombre d'<b>hospitalisations et réanimations</b> et <b>décès</b> ", #(<i>Attention ! Axes distincs</i>)
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de personnes (réa et hosp)")
fig.update_yaxes(title="Nb. de décès hosp.", secondary_y=True)

name_fig = "dc_hosp_rea_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

if show_charts:
    fig.show()
print("> " + name_fig)


# ## Décès cumulés (line chart)

# In[54]:



fig = px.line(x=df_region['jour'], y=df_region['dc'], color=df_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de décès hosp. cumulés")

name_fig = "dc_cum_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[55]:



fig = px.line(x = df_new_region['jour'], y = df_new_region['incid_dc'], color = df_new_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "Nombre de <b>décès quotidiens</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de décès hosp. en 24h")

name_fig = "dc_journ_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations

# In[56]:



fig = px.line(x=df_region['jour'], y=df_region['hosp'], color=df_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "Nombre de <b>patients hospitalisés</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients hospitalisés")

name_fig = "hosp_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations (entrées - sorties) (line chart)

# In[57]:



fig = px.line(x=df_region['jour'], y=df_region['hosp_new'], color=df_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "<b>Variation des hospitalisations</b> (entrées - sorties)",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de nouveaux patients hospitalisés")

name_fig = "hosp_variation_journ_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Admissions en hospitalisation (line chart)

# In[58]:



fig = px.line(x = df_new_region['jour'], y = df_new_region['incid_hosp'].rolling(window=7).mean(), color = df_new_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
#.rolling(window=7, center=True).mean()
fig.update_layout(
    title={
                'text': "<b>Nouvelles admissions en hospitalisation</b> (moyenne mobile 7 derniers j.)",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour", range=[dates[6], last_day_plot])
fig.update_yaxes(title="Admissions hospitalisations")

name_fig = "hosp_admissions_journ_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[59]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
colors_reg = px.colors.qualitative.G10 + px.colors.qualitative.Dark24

for graph, data_name in [("", "cas"), ("pop", "cas pour 100 k. hab.")]:
    df_incid_reg = df_incid.groupby(['jour', 'regionName']).sum().reset_index()
    df_incid_reg["P_pop"] = df_incid_reg["P"]*100000/df_incid_reg["pop"]
    
    if graph == "pop":
        reg_ordered = list(dict.fromkeys(list(df_incid_reg[df_incid_reg["jour"] == df_incid_reg["jour"].max()].sort_values(by=['P_pop'], ascending=False)["regionName"].values)))
    else:
        reg_ordered = list(dict.fromkeys(list(df_incid_reg[df_incid_reg["jour"] == df_incid_reg["jour"].max()].sort_values(by=['P'], ascending=False)["regionName"].values)))
    
    fig = go.Figure()
    
    if graph == "pop":
        y = (df_incid_france["P"]*100000/df_incid_france["pop"]).rolling(window=7).mean()
    else:
        y = df_incid_france["P"].rolling(window=7).mean()
        
    fig.add_trace(go.Scatter(
            x = df_incid_france["jour"],
            y = y,
            line=dict(width=9, color="Black"),
            name = "<b>France</b><br>" + str(round(y.values[-1],1)) + " {} en 24h".format(data_name),
            opacity=1))
    
    for i, reg in enumerate(reg_ordered):
        df_incid_reg_one = df_incid_reg[df_incid_reg["regionName"] == reg]
        
        if graph == "pop":
            y = df_incid_reg_one["P_pop"]
        else:
            y = df_incid_reg_one["P"]
            
        fig.add_trace(go.Scatter(
            x = df_incid_reg_one["jour"],
            y = y.rolling(window=7).mean(),
            line=dict(width=5, color=colors_reg[i]),
            name = "<br><b>" + reg + "</b><br>" + str(round(y.values[-1], 0)) + " {} en 24h".format(data_name),
            opacity=0.9
        ))
    
    fig.update_layout(
        title={
                    'text': "<b>Covid19 : nombre de {}</b>".format(data_name),
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
            titlefont = dict(
                    size=25),
            annotations = [
                    dict(
                        x=0.6,
                        y=1.034,
                        xref='paper',
                        yref='paper',
                        font=dict(size=18),
                        text='Moyenne mobile 7 jours',
                        showarrow=False
                    ),
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : covidtracker.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    )]
                     )
    fig.update_xaxes(range=[dates[-90], last_day_plot], nticks=20, tickformat="%d %b")

    name_fig = "cas_reg" + graph
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=1000)


    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[60]:


def prep_course():
    colors_regs_def = {}
    for i, reg in enumerate(regions):
        df_incid_reg.loc[df_incid_reg["regionName"]==reg, "incidence_rolling"] =             (df_incid_reg.loc[df_incid_reg["regionName"]==reg, "P"].rolling(window=7).sum()*100000/df_incid_reg.loc[df_incid_reg["regionName"]==reg, "pop"])

        df_incid_reg.loc[df_incid_reg["regionName"]==reg, "P_rolling"] = df_incid_reg.loc[df_incid_reg["regionName"]==reg, "P"].rolling(window=7).mean()
        colors_regs_def[reg] = colors_reg[i]

        df_region.loc[df_region["regionName"]==reg, "dc_pop_new_rolling"] = df_region.loc[df_region["regionName"]==reg, "dc_new"].rolling(window=7).mean()*10000000/df_region.loc[df_region["regionName"]==reg, "regionPopulation"]

    
    """(df_incid_reg, "incidence_rolling", dates_incid, "Incidence", "course_incidence", "regionName"),    (df_incid_reg, "P_rolling", dates_incid, "Cas de Covid19", "course_cas", "regionName"),    (df_region, "dc_pop_new_rolling", dates, "Décès pour 1M hab.", "course_dc", "regionName")]:"""


# In[61]:


#COURSE
n1 = 80
df_incid_reg = df_incid.groupby(['jour', 'regionName']).sum().reset_index()
df_incid_reg["P_pop"] = df_incid_reg["P"]*100000/df_incid_reg["pop"]


for (dataset, column, dates_to_use, title, folder) in [    (df_incid_reg, "incidence_rolling", dates_incid, "Incidence", "course_incidence"),    (df_incid_reg, "P_rolling", dates_incid, "Cas de Covid19", "course_cas"),    (df_region, "dc_pop_new_rolling", dates, "Décès hosp. quotidiens pour 10M hab.", "course_dc")]:
    
        colors_regs_def = {}
        for i, reg in enumerate(regions):
            df_incid_reg.loc[df_incid_reg["regionName"]==reg, "incidence_rolling"] =                 (df_incid_reg.loc[df_incid_reg["regionName"]==reg, "P"].rolling(window=7).sum()*100000/df_incid_reg.loc[df_incid_reg["regionName"]==reg, "pop"])

            df_incid_reg.loc[df_incid_reg["regionName"]==reg, "P_rolling"] = df_incid_reg.loc[df_incid_reg["regionName"]==reg, "P"].rolling(window=7).mean()
            colors_regs_def[reg] = colors[i]

            df_region.loc[df_region["regionName"]==reg, "dc_pop_new_rolling"] = df_region.loc[df_region["regionName"]==reg, "dc_new"].rolling(window=7).mean()*10000000/df_region.loc[df_region["regionName"]==reg, "regionPopulation"]

        max_value = 0
        for i in range(-n1, 0):
            data_temp = dataset[dataset["jour"] == dates_to_use[i]].sort_values(by=['regionName'], ascending=False)
            max_value = max(max_value, data_temp[column].max())

        for i in range(-n1, 0):   
            fig = go.Figure()

            data_temp = dataset[dataset["jour"] == dates_to_use[i]].sort_values(by=[column], ascending=True)
            #data_temp = data_temp[-10:]

            colors_regs = []
            for reg in data_temp["regionName"]:
                colors_regs += [colors_regs_def[reg]]

            fig.add_trace(go.Bar(
                x = data_temp[column],
                y = data_temp["regionName"],
                text = ["<b>" + str(d) + "</b>" for d in data_temp[column].astype(int).values],
                textposition='auto',
                textangle=0,
                marker = dict(color=data_temp[column], coloraxis = "coloraxis",), #colors_regs 
                orientation="h"))

            fig.update_xaxes(range=[0, max_value])

            fig.update_layout(
                title={
                        'text': "<b>{}</b> - ".format(title) + datetime.strptime(dates_to_use[i], '%Y-%m-%d').strftime('%d %B'),
                        'y':0.98,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                titlefont = dict(
                        size=20),

                coloraxis=dict(
                    cmin=0, cmax=max_value*0.8,
                    colorscale = [[0, "green"], [0.2, "#ffcc66"], [0.8, "#f50000"], [1, "#b30000"]],
                    colorbar=dict(
                        #title="{}<br>du Covid19<br> &#8205;".format(title),
                        thicknessmode="pixels", thickness=6,
                        lenmode="pixels", len=200,
                        yanchor="middle", y=0.5,
                        tickfont=dict(size=7),
                        ticks="outside", ticksuffix="",
                        )
                ),

                annotations = [
                        dict(
                            x=-0.06,
                            y=1.09,
                            xref='paper',
                            yref='paper',
                            font=dict(size=11),
                            text='Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.',                    
                            showarrow = False
                        )],

                margin=dict(
                        l=50,
                        r=5,
                        b=0,
                        t=60,
                        pad=0
                    ),
            )

            fig.write_image(PATH + "images/charts/france/{}/{}.jpeg".format(folder, i), scale=2, width=650, height=450)


# In[62]:


#COURSE REA
n2 = len(dates_clage)

for (dataset, column, dates_to_use, title, folder) in [    (df_clage_france, "rea", dates_clage, "Personnes en réanimation pour Covid19", "course_rea_clage_rolling"),    (df_clage_france, "hosp", dates_clage, "Personnes hospitalisées pour Covid19", "course_hosp_clage_rolling")]:
        
        for clage in [i for i in range(9, 99, 10)] + [90]:
            dataset.loc[dataset["cl_age90"]==clage, column+"_rolling"] = dataset.loc[dataset["cl_age90"]==clage, column].rolling(window=7).mean().fillna(method="ffill")

        max_value = 0
        for i in range(-n2, 0):
            data_temp = dataset[ (dataset["jour"] == dates_to_use[i]) & (dataset["cl_age90"] > 0)].sort_values(by=['cl_age90'], ascending=False)
            max_value = max(max_value, data_temp[column].max())


        for i in range(-n2, 0):   
            fig = go.Figure()

            data_temp = dataset[(dataset["jour"] == dates_to_use[i]) & (dataset["cl_age90"] > 0)].sort_values(by=["cl_age90"], ascending=True)
            #data_temp = data_temp[-10:]

            fig.add_trace(go.Bar(
                x = data_temp[column],
                y = [str(age-9) + " - " + str(age) + " ans" for age in range(9, 99, 10) ] + ["> 90 ans"],
                text = ["<b>" + str(d) + "</b>" for d in data_temp[column].astype(int).values],
                textposition='auto',
                textangle=0,
                marker = dict(color=data_temp[column], coloraxis = "coloraxis",), #colors_regs 
                orientation="h"))

            fig.update_xaxes(range=[0, max_value])

            fig.update_layout(
                title={
                        'text': "<b>{}</b> - ".format(title) + datetime.strptime(dates_to_use[i], '%Y-%m-%d').strftime('%d %B'),
                        'y':0.98,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                titlefont = dict(
                        size=20),

                coloraxis=dict(
                    cmin=0, cmax=max_value*0.8,
                    colorscale = [[0, "green"], [0.2, "#ffcc66"], [0.8, "#f50000"], [1, "#b30000"]],
                    colorbar=dict(
                        #title="{}<br>du Covid19<br> &#8205;".format(title),
                        thicknessmode="pixels", thickness=6,
                        lenmode="pixels", len=200,
                        yanchor="middle", y=0.5,
                        tickfont=dict(size=7),
                        ticks="outside", ticksuffix="",
                        )
                ),

                annotations = [
                        dict(
                            x=0.12,
                            y=1.09,
                            xref='paper',
                            yref='paper',
                            font=dict(size=11),
                            text='Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.',                    
                            showarrow = False
                        )],

                margin=dict(
                        l=50,
                        r=5,
                        b=0,
                        t=60,
                        pad=0
                    ),
            )

            fig.write_image(PATH + "images/charts/france/{}/{}.jpeg".format(folder, i), scale=2, width=650, height=450)


# In[63]:


"""
i=0
with imageio.get_writer(PATH + "images/charts/france/course_incidence/course.gif", mode='I', duration=0.2) as writer: 
    for i in range(-n, 0):
        image = imageio.imread((PATH + "images/charts/france/course_incidence/{}.jpeg").format(i))
        writer.append_data(image)
        
        if i==-n:
            for k in range(6):
                writer.append_data(image)
        if i==-1:
            for k in range(12):
                writer.append_data(image)
        i+=1
"""


# In[64]:


#import glob
for (folder, n, fps) in [("course_rea_clage_rolling", n2, 7), ("course_hosp_clage_rolling", n2, 7), ("course_incidence", n1, 5), ("course_dc", n1, 5), ("course_cas", n1, 5),]:
    img_array = []
    for i in range(-n, 0):
        img = cv2.imread((PATH + "images/charts/france/{}/{}.jpeg").format(folder, i))
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)

        if i==-n:
            for k in range(4):
                img_array.append(img)

        if i==-1:
            for k in range(12):
                img_array.append(img)

    out = cv2.VideoWriter(PATH + 'images/charts/france/{}/course.mp4'.format(folder),cv2.VideoWriter_fourcc(*'MP4V'), fps, size)

    for i in range(len(img_array)):
        out.write(img_array[i])

    out.release()
    
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-i", PATH + "images/charts/france/{}/course.mp4".format(folder), PATH + "images/charts/france/{}/course_opti.mp4".format(folder)])
        subprocess.run(["rm", PATH + "images/charts/france/{}/course.mp4".format(folder)])

        #subprocess.run(["rm", 'images/charts/france/{}/course265.mp4'.format(folder)])
        #subprocess.run(["ffmpeg", "-i", 'images/charts/france/{}/course.mp4'.format(folder), "-b", "1000k" \
         #               'images/charts/france/{}/course265.webm'.format(folder)])
        #subprocess.run(["ffmpeg", "-i", 'images/cdoharts/france/{}/course.mp4'.format(folder), "-vcodec", "libx265", "-crf", "28", \
                        #'images/charts/france/{}/course265.webm'.format(folder)])
            #ffmpeg -i images/charts/france/course_rea_clage_rolling/course.mp4 -vcodec libvpx-vp9 -b:v 1M -acodec libvorbis output.webm
                         
    except:
        print("error conversion h265")


# In[65]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
fig = go.Figure()

df_tests_ages = df_tests_viros.groupby(['jour', 'cl_age90']).sum().reset_index()

"""fig.add_trace(go.Scatter(
        x = df_incid_france["jour"],
        y = df_incid_france["P"].rolling(window=7).mean(),
        line=dict(width=7, color="Black"),
        name = "<b>France</b><br>" + str(df_incid_france["P"].values[-1]) + " cas en 24h",
        opacity=1))"""

for i, age in enumerate([9, 19, 29, 39, 49, 59, 69, 79, 89, 90]):
    df_incid_age_one = df_tests_ages[df_tests_ages["cl_age90"] == age]
    
    fig.add_trace(go.Scatter(
        x = df_incid_age_one["jour"],
        y = df_incid_age_one["P"].rolling(window=7).mean(),
        line=dict(width=5),
        name = "<br><b>" + str(age) + "</b><br>" + str(df_incid_age_one["P"].values[-1]) + " cas en 24h",
        opacity=1
    ))
    

fig.update_layout(
    title={
                'text': "<b>Nombre de cas positifs au Covid19</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=25),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : covidtracker.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(range=[dates[-90], last_day_plot], nticks=20, tickformat="%d %b")

name_fig = "cas_age"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=1000)


plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Réanimations par région (line chart)

# In[66]:


fig = px.line(x=df_region['jour'], y=df_region['rea'], color=df_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "Nombre de <b>patients en réanimation</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                    size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients en réanimation")

name_fig = "rea_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Réanimations par département (line chart)

# In[67]:


df_last_d = df[df['jour'] == dates[-1]]
#deps_ordered = df_last_d.sort_values(by=['rea'], ascending=False)["dep"].values
deps_ordered = df_last_d.sort_values(by=['dep'], ascending=True)["dep"].values

fig = go.Figure()
for dep in deps_ordered:
    fig.add_trace(go.Scatter(x=df['jour'], y=df[df["dep"] == dep]["rea"],
                    mode='lines+markers',
                    name=dep,
                    line=dict(width=2),
                    marker_size=8,
                            ))

fig.update_layout(
    title={
                'text': "Nb. de <b>patients en réanimation</b> par département",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients en réa. ou soins intensifs")

name_fig = "rea_dep"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations par département (line chart)

# In[68]:


df_last_d = df[df['jour'] == dates[-1]]
#deps_ordered = df_last_d.sort_values(by=['rea'], ascending=False)["dep"].values
deps_ordered = df_last_d.sort_values(by=['dep'], ascending=True)["dep"].values

fig = go.Figure()
for dep in deps_ordered:
    fig.add_trace(go.Scatter(x=df['jour'], y=df[df["dep"] == dep]["hosp"],
                    mode='lines+markers',
                    name=dep,
                    line=dict(width=2),
                    marker_size=8,
                            ))

fig.update_layout(
    title={
                'text': "Nb. de <b>patients hospitalisés</b> par département",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients hospitalisés")

name_fig = "hosp_dep"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Hospitalisations par habitant / région

# In[69]:


"""
fig = px.line(x=df_region['jour'], y=df_region['hosp_pop'], labels={'color':'Région'}, color=df_region["regionName"], color_discrete_sequence=colors)
fig.update_layout(
    title={
                'text': "Nb. de <b>patients hospitalisés</b> <b>par habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients hospitalisés/100k hab. (de ch. région)")

name_fig = "hosp_hab"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
if show_charts:
    fig.show()
"""


# <br>
# 
# ## Capacité réanimation (line chart)

# In[70]:


"""
df_rean = df.groupby('jour').sum().reset_index()
df_rean["lim_rea_prev"] = [14000 for i in range(len(dates))]
df_rean["lim_rea"] = [10000 for i in range(len(dates))]
df_rean = pd.melt(df_rean, id_vars=['jour'], value_vars=['rea', 'lim_rea', 'lim_rea_prev'])

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_rean['jour'], y=df_rean[df_rean['variable'] == 'rea']['value'],
                    mode='lines+markers',
                    name='Nb. patients réa.',
                    line=dict(width=4),
                    marker_size=11,))

fig.add_trace(go.Scatter(x=df_rean['jour'], y=df_rean[df_rean['variable'] == 'lim_rea_prev']['value'],
                    mode='lines',
                    name='Capacité max. prévue',
                    line=dict(width=4),
                    marker_size=11,))

fig.add_trace(go.Scatter(x=df_rean['jour'], y=df_rean[df_rean['variable'] == 'lim_rea']['value'],
                    mode='lines',
                    name='Capacité approx. actuelle',
                    line=dict(width=4),
                    marker_size=11,))

fig.update_layout(
    title={
                'text': "Nb. de <b>patients en réanimation</b> et de lits disponibles",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
            size=20),
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "capacite_rea"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1000, height=700)

fig.update_layout(
    legend_orientation="h",
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()"""


# <br>
# 
# ## Décès cumulés (région)

# In[71]:


fig = px.line(x=df_region['jour'], y=df_region['dc'], color=df_region["regionName"], labels={'color':'Région'}, color_discrete_sequence=colors).update_traces(mode='lines+markers')
fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b> par région",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
    
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de décès hosp. cumulés")

name_fig = "dc_cum_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Nouveaux décès quotidiens (line chart)

# In[72]:


fig = px.line(x=df_new_region['jour'], y=df_new_region['incid_dc'].rolling(window=7, center=True).mean(), color=df_new_region["regionName"], labels={'color':'Région'}, color_discrete_sequence=colors).update_traces(mode='lines+markers')
fig.update_layout(
    yaxis_type="log",
    title={
                'text': "<b>Nouveaux décès</b> par région (moyenne mobile 7 j.)",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
    
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour", range=[dates[6], last_day_plot])
fig.update_yaxes(title="Nb. de décès hosp.")

name_fig = "dc_nouv_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[73]:


fig = go.Figure()

for col in ["black", "color"]:
    i=0  
    for dep in departements:
        if (i==len(colors)):
            i=0
            
        if col=="black":
            colortemp = "black"
            leg=False
            opa=0.07
            size=2
            vis=True
            gp="g"
        else:
            colortemp=colors[i]
            leg=True
            opa=0.9
            size=3.5
            vis='legendonly'
            gp="g"+dep
            
        if dep in ["13", "75", "69"]:
            vis=True
        
        
        df_incid_dep = df_incid[df_incid["dep"]==dep]
        dep_name = df_incid_dep["departmentName"].values[0]
        fig.add_trace(go.Scatter(x=df_incid_dep['jour'], y=df_incid_dep['P'].rolling(window=7, center=False).mean(), marker_color=colortemp, mode="lines", line_width=size, name=dep, visible=vis, showlegend=leg, legendgroup=gp, opacity=opa, hovertemplate = '%{y:.2f} cas<br>%{x}<br>' + dep_name + " (" + dep + ")"))
        if leg:
            fig.add_trace(go.Scatter(x=[df_incid_dep['jour'].values[-1]], y=[df_incid_dep['P'].rolling(window=7, center=False).mean().dropna().values[-1]], marker_color=colortemp, mode="markers+text", marker_size=6, name=dep, text=[dep], textposition='middle right', visible=vis, legendgroup=gp, showlegend=False, hovertemplate = 'Pr %{y:$.2f}'))
        i+=1
                            
fig.update_layout(
    margin=dict(
                l=0,
                r=0,
                b=0,
                t=20,
                pad=0
            ),
    yaxis_type="log",
    
    title={
                'text': "",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
    
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour", fixedrange=True)
fig.update_yaxes(title="Nb. de cas positifs.", fixedrange=True)

name_fig = "testspositifs_nouv_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    margin=dict(
                l=20,
                r=190,
                b=0,
                t=0,
                pad=0
            ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False, config={"displayModeBar": False})
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés par habitant (région)

# In[74]:


"""
fig = px.line(x=df_region['jour'], y = df_region['dc']/df_region['regionPopulation']*100000, labels={'color':'Région'}, color=df_region["regionName"], color_discrete_sequence=colors)

fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b> par <b>habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. décès cumulés / 100k hab. de chaq. région")

name_fig = "dc_cum_hab_line"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
if show_charts:
    fig.show()
"""


# <br>
# <br>
# <br>
# <br>
# 
# # Other bar charts

# <br>
# 
# ## Décès cumulés par région / temps

# In[75]:


fig = px.bar(x=df_region['jour'], y = df_region['dc'], color=df_region["regionName"], labels={'color':'Région'}, color_discrete_sequence=colors, opacity=0.9)

fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b> par région",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
    
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de décès cumulés")
#fig.show()

name_fig = "dc_cum_region"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=500)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés par région / 3 derniers jours

# In[76]:



#df_region4 = df_region.groupby("regionName", "jour").sum().reset_index()
df_region_sans = df_region.drop( df_region[ df_region["regionName"].isin(["Martinique", "Guadeloupe", "Guyane", "La Réunion"]) ].index)
fig = go.Figure()


fig.add_trace(go.Bar(
    x = df_region_sans[df_region_sans["jour"] == dates[-4]]['regionName'],
    y = df_region_sans[df_region_sans["jour"] == dates[-4]]['dc'],
    name = datetime.strptime(dates[-4], '%Y-%m-%d').strftime('%d %B'),
    marker_color='indianred',
    opacity=0.3
)).update_xaxes(categoryorder="total ascending")

fig.add_trace(go.Bar(
    x = df_region_sans[df_region_sans["jour"] == dates[-3]]['regionName'],
    y = df_region_sans[df_region_sans["jour"] == dates[-3]]['dc'],
    name = datetime.strptime(dates[-3], '%Y-%m-%d').strftime('%d %B'),
    marker_color='indianred',
    opacity=0.4
))

fig.add_trace(go.Bar(
    x = df_region_sans[df_region_sans["jour"] == dates[-2]]['regionName'],
    y = df_region_sans[df_region_sans["jour"] == dates[-2]]['dc'],
    name = datetime.strptime(dates[-2], '%Y-%m-%d').strftime('%d %B'),
    marker_color='indianred',
    opacity=0.5
))

fig.add_trace(go.Bar(
    x = df_region_sans[df_region_sans["jour"] == dates[-1]]['regionName'],
    y = df_region_sans[df_region_sans["jour"] == dates[-1]]['dc'],
    name = datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B'),
    marker_color='indianred'
)).update_xaxes(categoryorder="total ascending")


# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    barmode='group', xaxis_tickangle=-45,
    
    title={
                'text': "<b>Décès cumulés</b> par région",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis_title="",
    yaxis_title="Nb. de décès cumulés",
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "dc_cum_region_comp"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1300, height=600)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés VS. Décès cumulés par habitant / région

# In[77]:


fig = go.Figure()
df_region3 = df_region[df_region["jour"] == dates[-1]].groupby("regionName").sum().reset_index()
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(
    x=df_region3['regionName'], 
    y = df_region3['dc'],
    name = "Nombre décès cumulés",
    width=0.3,
    marker_color='indianred'
),
             secondary_y = False).update_xaxes(categoryorder="total descending")

fig.add_trace(go.Bar(
    x=df_region3['regionName'], 
    y = df_region3['dc_pop'],
    name = "Nb. décès cum./100k hab.",
    marker_color='indianred',
    opacity=0.6,
    width=0.3,
    offset=0.15
    
),
             secondary_y = True)

fig.update_layout(
    barmode='group', 
    xaxis_tickangle=-45,
    
    title={
                'text': "Comparaison des <b>décès cumulés</b> et <b>décès cumulés par habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis_title="",
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France, INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_yaxes(title_text="Nb. décès cumulés", secondary_y=False)
fig.update_yaxes(title_text="Nb. décès cumulés/100k hab.", secondary_y=True)

name_fig = "dc_cum_hab_nonhab_comp"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Situation des malades / région

# In[78]:


#df_region_sumj = df_region.groupby('regionName').sum().reset_index()
df_region_sumj = df_region[df_region['jour'] == dates[-1]]

df_region_sumj = pd.melt(df_region_sumj, id_vars=['regionName'], value_vars=['rad', 'rea', 'dc', 'hosp_nonrea'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['regionName'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)


# In[79]:


data = df_region_sumj[df_region_sumj["variable"] == "dc"]
fig = go.Figure(go.Bar(x=data['regionName'], y=data['value'], text=data['value'], textposition='auto', name='Décès', marker_color='#000000', opacity=0.8))

data = df_region_sumj[df_region_sumj["variable"] == "rea"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text=data['value'], textposition='auto', name='Réanimation', marker_color='#FF0000', opacity=0.8))

data = df_region_sumj[df_region_sumj["variable"] == "hosp_nonrea"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text= data['value'], textposition='auto', name='Autre hospitalisation', marker_color='#FFA200', opacity=0.8))

data = df_region_sumj[df_region_sumj["variable"] == "rad"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text= data['value'], textposition='auto', name='Retour à domicile', marker_color='green', opacity=0.8))
fig.update_yaxes(title="Nb. de cas")

fig.update_layout(
            barmode='stack',
            title={
                'text': "<b>Situation des malades hospitalisés</b> du Covid-19",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = dict(
                size=20),
            xaxis=dict(
                title='',
                tickformat='%d/%m',
                nticks=len(dates)+5
            ),
            annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    
                    showarrow = False
                )]
)
fig.update_xaxes(categoryorder="total descending")     

name_fig = "situation_cas_region"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Situation des malades par habitant / région

# In[80]:


df_region_sumj = df_region[df_region['jour'] == dates[-1]]
df_region_sumj = pd.melt(df_region_sumj, id_vars=['regionName'], value_vars=['rad_pop', 'rea_pop', 'dc_pop', 'hosp_nonrea_pop'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['regionName'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)


# In[81]:


"""data = df_region_sumj[df_region_sumj["variable"] == "dc_pop"]
fig = go.Figure(go.Bar(x=data['regionName'], y=data['value'], text=round(data['value']), textposition='auto', name='Décès/100k hab.', marker_color='black', opacity=0.7))

data = df_region_sumj[df_region_sumj["variable"] == "rea_pop"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text=round(data['value']), textposition='auto', name='Réanimation/100k hab.', marker_color='red', opacity=0.7))

data = df_region_sumj[df_region_sumj["variable"] == "hosp_nonrea_pop"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text= round(data['value']), textposition='auto', name='Autre hospitalisation/100k hab.', marker_color='#FFA200', opacity=0.7))

data = df_region_sumj[df_region_sumj["variable"] == "rad_pop"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text=round(data['value']), textposition='auto', name='Retour à dom./100k hab', marker_color='green', opacity=0.7))
fig.update_yaxes(title="Nb. de cas")

fig.update_layout(
            barmode='stack',
            title={
                'text': "<b>Situation des malades hospitalisés</b> du Covid-19 <b>par habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = dict(
                size=20),
            xaxis=dict(
                title='',
                tickformat='%d/%m',
                nticks=len(dates)+5
            ),
            annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)
fig.update_xaxes(categoryorder="total descending")        

name_fig = "situation_cas_region_hab"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()"""


# <br>
# <br>
# <br>
# <br>
# 
# # Expérimentations (brouillon)

# In[82]:


"""
df_region_last_d = df_region[df_region['jour'] == dates[-1]]
reg_ordered = df_region_last_d.sort_values(by=['rea'], ascending=False)["regionName"].values

fig = go.Figure()
for reg in tqdm(reg_ordered):
    showld = True
    for dep in deps_ordered:
        fig.add_trace(go.Scatter(x=df['jour'], y=df[ (df["regionName"] == reg) & (df["dep"] == dep) ]["rea"],
                        mode='lines+markers',
                        legendgroup = reg,
                        name = dep,
                        marker = dict(color = colors[list(reg_ordered).index(reg)]),
                        line=dict(width=1.5),
                        showlegend = showld))
        showld = False

fig.update_layout(
    title={
                'text': "Nb. de <b>patients en réanimation</b> par région",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients en réanimation")

name_fig = "rea_reg"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

if show_charts:
    fig.show()
"""

