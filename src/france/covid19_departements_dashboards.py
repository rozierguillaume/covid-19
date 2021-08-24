#!/usr/bin/env python
# coding: utf-8

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


def nbWithSpaces(nb):
    str_nb = str(int(round(nb)))
    if(nb>100000):
        return str_nb[:3] + " " + str_nb[3:]
    elif(nb>10000):
        return str_nb[:2] + " " + str_nb[2:]
    elif(nb>1000):
        return str_nb[:1] + " " + str_nb[1:]
    else:
        return str_nb


# In[3]:


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


# In[4]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[5]:


data.download_data_variants_deps()
df_variants = data.import_data_variants_deps()


# In[6]:


df_departements = df.groupby(["jour", "departmentName"]).sum().reset_index()
df_incid_departements = df_incid[df_incid["cl_age90"]==0].groupby(["jour", "departmentName", "dep"]).sum().reset_index()

df_new_departements = df_new.groupby(["jour", "departmentName"]).sum().reset_index()

departements = list(dict.fromkeys(list(df_departements['departmentName'].values))) 

dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 
last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")
last_day_plot_plus2 = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=3)).strftime("%Y-%m-%d")

departements_nb = list(dict.fromkeys(list(df_tests_viros['dep'].values))) 


# In[7]:


lits_reas = pd.read_csv(PATH+'data/france/lits_rea.csv', sep=",")

df_departements_lits = df_departements.merge(lits_reas, left_on="departmentName", right_on="nom_dpt")


# In[8]:


data.download_donnees_vaccination_par_tranche_dage_type_de_vaccin_et_departement()
df_vaccination = data.import_donnees_vaccination_par_tranche_dage_type_de_vaccin_et_departement()
df_vaccination = df_vaccination[df_vaccination["libelle_classe_age"] != "Tout âge"]


# In[9]:


def cas_journ(departement):

    df_incid_dep = df_incid_departements[df_incid_departements["departmentName"] == departement]
    df_incid_dep_rolling = df_incid_dep["P"].rolling(window=7, center=True).mean()
    df_incid_tests_dep_rolling = df_incid_dep["T"].rolling(window=7, center=True).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "cas_journ_"+departement, [0, df_incid_dep["P"].max()]
    title = "<b>Cas positifs</b> au Covid19 - <b>" + departement + "</b>"

    fig = go.Figure()
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[""], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"],
        y = df_incid_dep_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='rgb(8, 115, 191)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.3)",
        showlegend=False
    ), secondary_y=True)
    
    fig.add_trace(go.Bar(
        x = df_incid_dep["jour"],
        y = df_incid_tests_dep_rolling,
        name = "Tests réalisés",
        marker_color='rgba(0, 0, 0, 0.2)',
        opacity=0.8,
        showlegend=False,
    ), secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x = [dates_incid[-4]],
        y = [df_incid_dep_rolling.values[-4]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ), secondary_y=True)

    """fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"],
        y = df_incid_dep["P"],
        name = "",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ), secondary_y=True)"""

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), secondary_y=True)
    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), secondary_y=False)
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

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
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates_incid[-4], y = df_incid_dep_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y2',
            text=" <b>{} {}".format('%d' % df_incid_dep_rolling.values[-4], "cas quotidiens<br></b>en moyenne du {} au {}.".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=1,
            ax=-250,
            ay=-70,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),dict(
            x = dates_incid[-4], y = df_incid_tests_dep_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_incid_tests_dep_rolling.values[-4], "tests réalisés<br></b>en moyenne du {} au {}.".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=0,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgba(0, 0, 0, 0.5)",
                size=15
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=1,
            ax=-250,
            ay=-70,
            arrowcolor="rgba(0, 0, 0, 0.5)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ))

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)

#cas_journ("Savoie")


# In[10]:


def nombre_variants(departement):
    df_incid_dep = df_incid_departements[df_incid_departements["departmentName"] == departement]
    df_incid_dep["P_rolling"] = df_incid_dep["P"].rolling(window=7).mean()
    
    df_variants_dep = df_variants[df_variants["dep"] == df_incid_dep["dep"].values[0]]
    
    fig = go.Figure()
    n_days = len(df_variants_dep)

    y=df_incid_dep["P_rolling"].values[-n_days:] * (100 - df_variants_dep.tx_C1.values)/100
    proportion = str(round(y[-1]/df_incid_dep["P_rolling"].values[-1]*100, 1)).replace(".", ",")
    fig.add_trace(
        go.Scatter(
            x=df_variants_dep.jour,
            y=y,
            name="<b>Autres </b><br>" + str(nbWithSpaces(y[-1])) + " cas (" + proportion + " %)",
            stackgroup='one'
        )
    )

    y=df_incid_dep["P_rolling"].values[-n_days:] * df_variants_dep.tx_C1.values/100
    proportion = str(round(y[-1]/df_incid_dep["P_rolling"].values[-1]*100, 1)).replace(".", ",")
    fig.add_trace(
        go.Scatter(
            x=df_variants_dep.jour,
            y=y,
            name="Mutation L452R, dont <b>Delta </b><br>" + str(nbWithSpaces(y[-1])) + " cas (" + proportion + " %)",
            showlegend=True,
            stackgroup='one'
        )
    )

    fig.update_yaxes(ticksuffix="")

    fig.update_layout(
         title={
            'text': "Nombre de variants dans les cas détectés - " + departement,
            'y':0.97,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
             'font': {'size': 20}
        },
        annotations = [
                        dict(
                            x=0.5,
                            y=1.1,
                            xref='paper',
                            yref='paper',
                            text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                            showarrow = False
                        )]
    )
    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format("variants_nombre_"+departement), scale=1.5, width=750, height=500)


# In[11]:


"""import numpy as np
def cas_journ_departements_couvre_feu(departements):
    fig = go.Figure()
    
    normalisation = True
    
    range_x, name_fig, range_y, n = ["2020-10-29", last_day_plot], "impact_couvre_feu", [0, df_incid_departements["P"].max()*0.7], 30
    title = "<b>Taux d'incidence</b>"
    
    deps_couvre_feu_2_janvier = ["Hautes-Alpes", "Alpes-Maritimes", "Ardennes", "Doubs", "Jura", "Marne", "Haute-Marne", "Meurthe-et-Moselle", "Meuse", "Haute-Saône", "Vosges", "Territoire de Belfort", "Moselle", "Nièvre", \
                                 "Saône-et-Loire"]
    deps_couvre_feu_8_janvier = ["Bas-Rhin", "Haut-Rhin", "Côte-d'or", "Cher", "Allier", "Bouches-du-Rhône", "Vaucluse", "Alpes-de-Haute-Provence"]
    #deps_couvre_feu_8_janvier = []
    
    df_incid_dep_couvre_feu = [0]*n
    df_incid_dep_couvre_feu_8 = [0]*n
    df_incid_dep_autres = [0]*n
    
    df_incid_dep_couvre_feu_ecart = [0]*n
    df_incid_dep_couvre_feu_ecart_8 = [0]*n
    df_incid_dep_autres_ecart = [0]*n
    
    n_deps_couvre_feu = 0
    n_deps_couvre_feu_8 = 0
    n_autres_deps = 0
    
    pop_deps_couvre_feu = 0
    pop_deps_couvre_feu_8 = 0
    pop_autres_deps = 0
    
    for departement in departements:
        df_incid_dep = df_incid_departements[df_incid_departements["departmentName"] == departement]
        
        n_days= (datetime.strptime(max(df_incid_dep["jour"]), '%Y-%m-%d') - datetime.strptime("2021-01-02", '%Y-%m-%d')).days
        
        df_incid_dep_rolling = df_incid_dep["P"].rolling(window=7, center=True).sum()*100000#/df_incid_dep["T"].rolling(window=7, center=False).mean() * 100
        values = df_incid_dep_rolling.values[-n:]
        
        if departement in deps_couvre_feu_2_janvier:
            df_incid_dep_couvre_feu += values
            n_deps_couvre_feu += 1
            pop_deps_couvre_feu += df_incid_dep["pop"].values[0]
            
        elif departement in deps_couvre_feu_8_janvier:
            df_incid_dep_couvre_feu_8 += values
            n_deps_couvre_feu_8 += 1
            pop_deps_couvre_feu_8 += df_incid_dep["pop"].values[0]
            
        else:
            df_incid_dep_autres += values
            n_autres_deps += 1
            pop_autres_deps += df_incid_dep["pop"].values[0]
            
            

    df_incid_dep_couvre_feu_mean = np.array(df_incid_dep_couvre_feu)/pop_deps_couvre_feu
    df_incid_dep_couvre_feu_8_mean = np.array(df_incid_dep_couvre_feu_8)/pop_deps_couvre_feu_8
    df_incid_dep_autres_mean = np.array(df_incid_dep_autres)/pop_autres_deps
    
    suffix = ""
    if normalisation:
        suffix = " %"
        df_incid_dep_couvre_feu_8_mean=df_incid_dep_couvre_feu_8_mean/df_incid_dep_couvre_feu_8_mean[-n_days-1]*100-100
        df_incid_dep_couvre_feu_mean=df_incid_dep_couvre_feu_mean/df_incid_dep_couvre_feu_mean[-n_days-1]*100-100
        df_incid_dep_autres_mean=df_incid_dep_autres_mean/df_incid_dep_autres_mean[-n_days-1]*100-100
    
    #df_incid_dep_autres_mean/=df_incid_dep_autres_mean[-n_days-1]
    
    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"].values[-n:],
        y = df_incid_dep_couvre_feu_mean,
        name = "Départements en couvre-feu renforcé (02/01)",
        marker_color='rgb(8, 115, 191)',
        line_width=5,
        opacity=0.8,
        showlegend=True
    ))
    
    if len(deps_couvre_feu_8_janvier)>0:
        fig.add_trace(go.Scatter(
            x = df_incid_dep["jour"].values[-n:],
            y = df_incid_dep_couvre_feu_8_mean,
            name = "Départements en couvre-feu renforcé (08/01)",
            marker_color='orange',
            line_width=5,
            opacity=0.8,
            showlegend=True
        ))
    
    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"].values[-n:],
        y = df_incid_dep_autres_mean,
        name = "Départements en couvre-feu classique",
        marker_color='black',
        line_width=5,
        opacity=0.8,
        showlegend=True
    ))

    ###
    
    max_value = max(max(df_incid_dep_autres_mean), max(df_incid_dep_couvre_feu_8_mean), max(df_incid_dep_couvre_feu_mean))
    min_value = min(0, min(df_incid_dep_autres_mean), min(df_incid_dep_couvre_feu_8_mean), min(df_incid_dep_couvre_feu_mean))

    fig.add_shape(type="line",
        x0="2021-01-12", y0=min_value*1.5, x1="2021-01-12", y1=max_value*1.5,
        line=dict(color="rgba(8, 115, 191, 1)",width=2, dash="dot")
        )
    
    fig.add_shape(type="line",
        x0="2021-01-02", y0=min_value*1.5, x1="2021-01-02", y1=max_value*1.5,
        line=dict(color="rgba(8, 115, 191, 1)",width=2, dash="dot")
        )
    
    ### Orange
    annots = []
    if len(deps_couvre_feu_8_janvier)> 0:
        fig.add_shape(type="line",
            x0="2021-01-08", y0=min_value*1.5, x1="2021-01-08", y1=max_value*1.5,
            line=dict(color="orange",width=2, dash="dot")
            )

        fig.add_shape(type="line",
            x0="2021-01-18", y0=min_value*1.5, x1="2021-01-18", y1=max_value*1.5,
            line=dict(color="orange",width=2, dash="dot")
            )
        annots = [dict(
                        x=df_incid_dep["jour"].values[-3],
                        y=df_incid_dep_autres_mean[-4],
                        xref='x1',
                        yref='y1',
                        ax=150,
                        ay=200,
                        font=dict(size=12, color="black"),
                        arrowcolor='black',
                        text= ["+"+str(round(value, 1))+" %" if value>0 else str(round(value, 1)) + " %" for value in [df_incid_dep_autres_mean[-4]]][0], #str(round(df_incid_dep_couvre_feu_8_mean[-4], 1))+" %",                    
                        showarrow = False
                    ),
                  dict(
                        x=df_incid_dep["jour"].values[-3],
                        y=df_incid_dep_couvre_feu_8_mean[-4],
                        xref='x1',
                        yref='y1',
                        ax=150,
                        ay=200,
                        font=dict(size=12, color="orange"),
                        arrowcolor='orange',
                        text= ["+"+str(round(value, 1))+" %" if value>0 else str(round(value, 1))+" %" for value in [df_incid_dep_couvre_feu_8_mean[-4]]][0], #str(round(df_incid_dep_couvre_feu_8_mean[-4], 1))+" %",                    
                        showarrow = False
                    ),
                  dict(
                        x=df_incid_dep["jour"].values[-3],
                        y=df_incid_dep_couvre_feu_mean[-4],
                        xref='x1',
                        yref='y1',
                        ax=150,
                        ay=200,
                        font=dict(size=12, color='rgb(8, 115, 191)'),
                        arrowcolor='rgb(8, 115, 191)',
                        text= ["+"+str(round(value, 1))+" %" if value>0 else str(round(value, 1))+" %" for value in [df_incid_dep_couvre_feu_mean[-4]]][0], #str(round(df_incid_dep_couvre_feu_8_mean[-4], 1))+" %",                    
                        showarrow = False
                    ),
                  dict(
                        x="2021-01-08",
                        y=max_value*0.95,
                        xref='x1',
                        yref='y1',
                        font=dict(size=9, color="orange"),
                        arrowcolor="orange",
                        text="Couvre feu 08/01",                    
                        showarrow = True
                    ),
                    dict(
                        x="2021-01-18",
                        y=max_value*0.95,
                        xref='x1',
                        yref='y1',
                        font=dict(size=9, color="orange"),
                        text='J+10',                    
                        arrowcolor="orange",
                        showarrow = True
                    ),]
    
    fig.update_yaxes(zerolinecolor='Grey', range=[min_value*1.5, max_value*1.5], tickfont=dict(size=18), ticksuffix=suffix)
    fig.update_xaxes( ticks='inside', tickangle=0, tickfont=dict(size=18))
    
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.2,
        xanchor="left",
        x=0.1
    ))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
                b=50,
                t=70,
                pad=0
            ),
        
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = annots + [
                dict(
                        x=0.45,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        xanchor="center",
                        font=dict(size=14),
                        text='{}</b>'.format("Nb de cas/semaine/100k hab. Moyennes pondérées à la population de chaque dép."),                    
                        showarrow = False
                    ),
                    dict(
                        x=0,
                        y=1.0,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b'), "Nb de cas/semaine/100k hab."),                    
                        showarrow = False
                    ),
                    dict(
                        x="2021-01-02",
                        y=max_value*0.95,
                        xref='x1',
                        yref='y1',
                        font=dict(size=9, color="rgba(8, 115, 191, 1)"),
                        arrowcolor="rgba(8, 115, 191, 1)",
                        text='Couvre feu 02/01'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b'), "Nb de cas/semaine/100k hab."),                    
                        showarrow = True
                    ),
                    dict(
                        x="2021-01-12",
                        y=max_value*0.95,
                        xref='x1',
                        yref='y1',
                        font=dict(size=9, color="rgb(8, 115, 191)"),
                        text='J+10',                    
                        arrowcolor="rgba(8, 115, 191, 1)",
                        showarrow = True
                    ),
                    ]
                     )

    fig.write_image(PATH+"images/charts/france/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
    
    print("> " + name_fig)

cas_journ_departements_couvre_feu(departements)"""


# In[12]:


"""import numpy as np
def cas_journ_departements_couvre_feu_hosp(departements):
    fig = go.Figure()
    
    normalisation = True
    
    range_x, name_fig, range_y, n = ["2020-10-29", last_day_plot], "impact_couvre_feu", [0, df_incid_departements["P"].max()*0.7], 20
    title = "<b>Taux d'incidence</b>"
    
    deps_couvre_feu_2_janvier = ["Hautes-Alpes", "Alpes-Maritimes", "Ardennes", "Doubs", "Jura", "Marne", "Haute-Marne", "Meurthe-et-Moselle", "Meuse", "Haute-Saône", "Vosges", "Territoire de Belfort", "Moselle", "Nièvre", \
                                 "Saône-et-Loire"]
    deps_couvre_feu_8_janvier = ["Bas-Rhin", "Haut-Rhin", "Côte-d'or", "Cher", "Allier", "Bouches-du-Rhône", "Vaucluse", "Alpes-de-Haute-Provence"]
    deps_couvre_feu_8_janvier = []
    
    df_incid_dep_couvre_feu = [0]*n
    df_incid_dep_couvre_feu_8 = [0]*n
    df_incid_dep_autres = [0]*n
    
    df_incid_dep_couvre_feu_ecart = [0]*n
    df_incid_dep_couvre_feu_ecart_8 = [0]*n
    df_incid_dep_autres_ecart = [0]*n
    
    n_deps_couvre_feu = 0
    n_deps_couvre_feu_8 = 0
    n_autres_deps = 0
    
    pop_deps_couvre_feu = 0
    pop_deps_couvre_feu_8 = 0
    pop_autres_deps = 0
    
    for departement in departements:
        #df_dep = df_departements[df_departements["departmentName"] == departement]
        df_new_dep = df_new_departements[df_new_departements["departmentName"] == departement]
        print(max(df_new_dep["jour"]))
        n_days= (datetime.strptime(max(df_new_dep["jour"]), '%Y-%m-%d') - datetime.strptime("2021-01-05", '%Y-%m-%d')).days
        
        df_incid_dep_rolling = df_new_dep["incid_hosp"].rolling(window=7, center=True).mean() #/df_incid_dep["T"].rolling(window=7, center=False).mean() * 100
        values = df_incid_dep_rolling.values[-n:]
        
        if departement in deps_couvre_feu_2_janvier:
            df_incid_dep_couvre_feu += values
            n_deps_couvre_feu += 1
            pop_deps_couvre_feu += df_incid_dep["pop"].values[0]
            
        elif departement in deps_couvre_feu_8_janvier:
            df_incid_dep_couvre_feu_8 += values
            n_deps_couvre_feu_8 += 1
            pop_deps_couvre_feu_8 += df_incid_dep["pop"].values[0]
            
        else:
            df_incid_dep_autres += values
            n_autres_deps += 1
            pop_autres_deps += df_incid_dep["pop"].values[0]
            
            

    df_incid_dep_couvre_feu_mean = np.array(df_incid_dep_couvre_feu)/pop_deps_couvre_feu
    df_incid_dep_couvre_feu_8_mean = np.array(df_incid_dep_couvre_feu_8)/pop_deps_couvre_feu_8
    df_incid_dep_autres_mean = np.array(df_incid_dep_autres)/pop_autres_deps
    
    suffix = ""
    if normalisation:
        suffix = " %"
        df_incid_dep_couvre_feu_8_mean=df_incid_dep_couvre_feu_8_mean/df_incid_dep_couvre_feu_8_mean[-n_days-1]*100-100
        df_incid_dep_couvre_feu_mean=df_incid_dep_couvre_feu_mean/df_incid_dep_couvre_feu_mean[-n_days-1]*100-100
        df_incid_dep_autres_mean=df_incid_dep_autres_mean/df_incid_dep_autres_mean[-n_days-1]*100-100
    
    #df_incid_dep_autres_mean/=df_incid_dep_autres_mean[-n_days-1]
    
    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"].values[-n:],
        y = df_incid_dep_couvre_feu_mean,
        name = "Départements en couvre-feu renforcé (02/01)",
        marker_color='rgb(8, 115, 191)',
        line_width=5,
        opacity=0.8,
        showlegend=True
    ))
    
    if len(deps_couvre_feu_8_janvier)>0:
        fig.add_trace(go.Scatter(
            x = df_incid_dep["jour"].values[-n:],
            y = df_incid_dep_couvre_feu_8_mean,
            name = "Départements en couvre-feu renforcé (08/01)",
            marker_color='orange',
            line_width=5,
            opacity=0.8,
            showlegend=True
        ))
    
    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"].values[-n:],
        y = df_incid_dep_autres_mean,
        name = "Départements en couvre-feu classique",
        marker_color='black',
        line_width=5,
        opacity=0.8,
        showlegend=True
    ))

    ###
    
    max_value = max(max(df_incid_dep_autres_mean), max(df_incid_dep_couvre_feu_8_mean), max(df_incid_dep_couvre_feu_mean))
    min_value = min(0, min(df_incid_dep_autres_mean), min(df_incid_dep_couvre_feu_8_mean), min(df_incid_dep_couvre_feu_mean))

    fig.add_shape(type="line",
        x0="2021-01-12", y0=min_value*1.5, x1="2021-01-12", y1=max_value*1.5,
        line=dict(color="rgba(8, 115, 191, 1)",width=2, dash="dot")
        )
    
    fig.add_shape(type="line",
        x0="2021-01-02", y0=min_value*1.5, x1="2021-01-02", y1=max_value*1.5,
        line=dict(color="rgba(8, 115, 191, 1)",width=2, dash="dot")
        )
    
    ### Orange
    annots = []
    if len(deps_couvre_feu_8_janvier)> 0:
        fig.add_shape(type="line",
            x0="2021-01-08", y0=min_value*1.5, x1="2021-01-08", y1=max_value*1.5,
            line=dict(color="orange",width=2, dash="dot")
            )

        fig.add_shape(type="line",
            x0="2021-01-18", y0=min_value*1.5, x1="2021-01-18", y1=max_value*1.5,
            line=dict(color="orange",width=2, dash="dot")
            )
        annots = [dict(
                        x="2021-01-08",
                        y=max_value*0.95,
                        xref='x1',
                        yref='y1',
                        font=dict(size=9, color="orange"),
                        arrowcolor="orange",
                        text="Couvre feu 08/01",                    
                        showarrow = True
                    ),
                    dict(
                        x="2021-01-18",
                        y=max_value*0.95,
                        xref='x1',
                        yref='y1',
                        font=dict(size=9, color="orange"),
                        text='J+10',                    
                        arrowcolor="orange",
                        showarrow = True
                    ),]
    
    fig.update_yaxes(zerolinecolor='Grey', range=[min_value*1.5, max_value*1.5], tickfont=dict(size=18), ticksuffix=suffix)
    fig.update_xaxes( ticks='inside', tickangle=0, tickfont=dict(size=18))
    
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.2,
        xanchor="left",
        x=0.1
    ))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
                b=50,
                t=70,
                pad=0
            ),
        
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = annots + [
                dict(
                        x=0.45,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        xanchor="center",
                        font=dict(size=14),
                        text='{}</b>'.format("Nb de cas/semaine/100k hab. Moyennes pondérées à la population de chaque dép."),                    
                        showarrow = False
                    ),
                    dict(
                        x=0,
                        y=1.0,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b'), "Nb de cas/semaine/100k hab."),                    
                        showarrow = False
                    ),
                    dict(
                        x="2021-01-02",
                        y=max_value*0.95,
                        xref='x1',
                        yref='y1',
                        font=dict(size=9, color="rgba(8, 115, 191, 1)"),
                        arrowcolor="rgba(8, 115, 191, 1)",
                        text='Couvre feu 02/01'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b'), "Nb de cas/semaine/100k hab."),                    
                        showarrow = True
                    ),
                    dict(
                        x="2021-01-12",
                        y=max_value*0.95,
                        xref='x1',
                        yref='y1',
                        font=dict(size=9, color="rgb(8, 115, 191)"),
                        text='J+10',                    
                        arrowcolor="rgba(8, 115, 191, 1)",
                        showarrow = True
                    ),
                    ]
                     )

    fig.write_image(PATH+"images/charts/france/{}_hosp.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)

cas_journ_departements_couvre_feu_hosp(departements)"""


# In[13]:


def incid_dep(departement):
        
    df_incid_dep = df_incid_departements[df_incid_departements["departmentName"] == departement]
    df_incid_dep_rolling = df_incid_dep["P"].rolling(window=7, center=True).sum()/df_incid_dep["pop"] * 100000
    dep_nb = df_incid_dep["dep"].values[0]
    
    range_x, name_fig, range_y = ["2020-09-29", last_day_plot], "incid_"+departement, [0, df_incid_dep_rolling.max()]
    title = "<b>" + departement + " (" + dep_nb + ")" + "</b>"

    fig = go.Figure()
    
    fig.add_shape(type="line",
    x0="2019-03-17", y0=50, x1="2021-03-17", y1=50,
        line=dict(color="Red",width=1.5, dash="dot")
    )
    
    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"][:len(df_incid_dep["jour"])-13],
        y = df_incid_dep_rolling[:len(df_incid_dep_rolling)-13],
        name = "",
        marker_color='rgb(8, 115, 191)',
        line_width=0.5,
        mode="lines",
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.2)",
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"][len(df_incid_dep["jour"])-14:],
        y = df_incid_dep_rolling[len(df_incid_dep_rolling)-14:],
        name = "",
        marker_color='rgb(8, 115, 191)',
        mode="lines",
        line_width=2,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.4)",
        showlegend=False
    ))


    fig.add_trace(go.Scatter(
        x = [dates_incid[-4]],
        y = [df_incid_dep_rolling.values[-4]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        marker_size=30,
        opacity=1,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), visible=False)
    fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
                    size=50),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

    
                     )

    fig['layout']['annotations'] += (dict(
            x = dates_incid[-4], y = df_incid_dep_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_incid_dep_rolling.values[-4], "".format()),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=50
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=1,
            ax=-40,
            ay=-50,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)
    
    incid_j0 = df_incid_dep_rolling.dropna().values[-1]
    incid_j7 = df_incid_dep_rolling.dropna().values[-8]
    
    if incid_j0 > 50:
        if (incid_j0 - incid_j7) < 0:
            class_dep = "higher_low"
        else:
            class_dep = "higher_high"
    else:
        if (incid_j0 - incid_j7) < 0:
            class_dep = "lower_low"
        else:
            class_dep = "lower_high" 
            
    folder = "covidep/"+class_dep
    
    fig.write_image(PATH+"images/charts/france/{}/{}.svg".format(folder, name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    
    return class_dep
#incid_dep("Savoie")


# In[14]:


def comparaison_cas_dc(departement):
    df_incid_dep = df_incid_departements[df_incid_departements["departmentName"] == departement]
    df_dep = df_new_departements[df_new_departements["departmentName"] == departement]
    
    y1 = df_incid_dep.incidence
    y2 = (df_dep.incid_dc/df_dep.departmentPopulation).rolling(window=7).mean().shift(-12)

    coef_normalisation = 50000000 #y1.max()/y2.max()
    max_y = math.ceil(max(y1.max(), y2.max()*coef_normalisation)*1.1 / 100) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_incid_dep.jour,
        y=y1,
        name="Cas pour 100 k",
        marker_color='rgb(8, 115, 191)',
        fillcolor="rgba(8, 115, 191, 0.3)",
        fill='tozeroy'))
    fig.add_trace(go.Scatter(
        x=df_incid_dep.jour,
        y=-y1,
        name="Miroir des cas",
        marker_color='rgba(8, 115, 191, 0.2)',
        line=dict(
            dash="dot")
    ))
    fig.add_trace(go.Scatter(
        x=df_dep.jour,
        y=-y2*coef_normalisation,
        marker_color='black',
        fillcolor="rgba(0,0,0,0.3)",
        name="Décès hospitaliers<br>décalés de 12 j.<br>pour {} Mio".format(round(coef_normalisation/1000000)),
        fill='tozeroy'))
    fig.update_yaxes(range=[-max_y, max_y], tickvals=[-max_y, -max_y/2, 0, max_y/2, max_y], ticktext=[max_y, max_y/2, 0, max_y/2, max_y])
    fig.update_layout(
        title={
                    'text': "Cas vs. Décès hospitaliers - {}".format(departement),
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
        titlefont = dict(
                        size=30),
        annotations = [
                            dict(
                                x=0.5,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="Cas pour 100 000 habitants et décès hospitaliers avancés de 12 j. pour {} Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/1000000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )

    fig.write_image(PATH + "images/charts/france/departements_dashboards/comparaison_cas_dc_{}.jpeg".format(departement), scale=2, width=900, height=600)
    #plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#comparaison_cas_dc("Pyrénées-Orientales")


# In[15]:


def hosp_journ(departement):   
    df_dep = df_departements[df_departements["departmentName"] == departement]
    df_new_dep = df_new_departements[df_new_departements["departmentName"] == departement]
    #df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "hosp_journ_"+departement
    title = "Personnes <b>hospitalisées</b> pour Covid19 - <b>" + departement +"</b>"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = df_dep["jour"],
        y = df_dep["hosp"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(209, 102, 21)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_dep["hosp"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(209, 102, 21)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Bar(
        x = df_new_dep["jour"],
        y = df_new_dep["incid_hosp"],
        name = "Admissions hosp.",
        marker_color='rgb(209, 102, 21)',
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_dep["jour"],
        y = df_new_dep["incid_hosp"].rolling(window=7).mean(),
        name = "Admissions hosp.",
        marker_color='rgb(209, 102, 21)',
        #mode="lines"
        line_width=2,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

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
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_dep["hosp"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_dep["hosp"].values[-1], "personnes<br>hospitalisées</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-250,
            ay=-90,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
            dict(
            x = df_new_dep["jour"].values[-1], y = (df_new_dep["incid_hosp"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_dep["incid_hosp"].values[-1], "<br>admissions"),
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
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)


# In[16]:


def hosp_comparaison_vagues(departement):   
    df_dep = df_departements[df_departements["departmentName"] == departement]
    #df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "hosp_comp_vagues_"+departement
    title = ""#"<b>Personnes hospitalisées</b> pour Covid19 - " + departement

    fig = go.Figure()
    
    premiere_vague = df_dep[ df_dep["jour"] < "2020-08"]["hosp"].max()
    premiere_vague_date = df_dep[ df_dep["hosp"] == premiere_vague]["jour"].min()
    
    deuxieme_vague = df_dep[ df_dep["jour"] > "2020-09"]["hosp"].max()
    deuxieme_vague_date = df_dep[ (df_dep["hosp"] == deuxieme_vague) & (df_dep["jour"] > "2020-09")]["jour"].min()
    
    color_deuxieme_vague = "green"
    if deuxieme_vague > premiere_vague:
        color_deuxieme_vague = "red"
    
    hosp_values = df_dep["hosp"].values
    trace_to_add = [max(0, hosp - premiere_vague) for hosp in hosp_values]
    
    
    #deuxieme_vague += [df_dep[ df_dep["jour"] > "2020-09"]["hosp"].max()]
    color = ["red" if hosp > premiere_vague else "rgb(209, 102, 21)" for hosp in df_dep["hosp"].values]
    fig.add_trace(go.Bar(
        x = df_dep["jour"],
        y = df_dep["hosp"].values - trace_to_add,
        name = "Nouveaux décès hosp.",
        marker_color="orange",
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    fig.add_trace(go.Bar(
        x = df_dep["jour"],
        y = trace_to_add,
        name = "Nouveaux décès hosp.",
        marker_color="red",
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    fig.add_shape(
            type="line",
            x0="2000-01-01",
            y0=premiere_vague,
            x1="2030-01-01",
            y1=premiere_vague,
            opacity=1,
            #fillcolor="orange",
            line=dict(
                dash="dash",
                color="black",
                width=1,
            )
        )

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18),  range=["2020-03-15", last_day_plot])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,1)',
        bargap=0,
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='stack',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=-0.08,
                        xref='paper',
                        yref='paper',
                        text="Date : {}. Source : Santé publique France. Auteur : Guillaume Rozier - covidtracker.fr - nombre d'hospitalisations".format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = deuxieme_vague_date, y = deuxieme_vague, # annotation point
            xref='x1', 
            yref='y1',
            text="Deuxième vague",
            xshift=-5,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color=color_deuxieme_vague,
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-150,
            ay=-50,
            arrowcolor=color_deuxieme_vague,
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),dict(
            x = premiere_vague_date, y = premiere_vague, # annotation point
            xref='x1', 
            yref='y1',
            text="Première vague",
            xshift=0,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=0,
            ay=-50,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ))

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=1000, height=700)

    print("> " + name_fig)
    
#hosp_comparaison_vagues("Savoie")


# In[17]:


def hosp_journ_elias(dep):
    df_new_dep = df_new[df_new["departmentName"]==dep]

    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "hosp_journ_flux_"+dep, [0, df_new_dep["incid_hosp"].max()*0.9]
    title = "<b>Entrées et sorties de l'hôpital</b> pour Covid19 • <b>" + dep + "</b>"
    
    for i in [""]:
        if i=="log":
            title+= " [log.]"

        fig = go.Figure()
        
        entrees_rolling = df_new[df_new["departmentName"]==dep]["incid_hosp"].rolling(window=7).mean().values
        
        fig.add_trace(go.Scatter(
            x = dates,
            y =entrees_rolling,
            name = "",
            marker_color='red',
            line_width=6,
            opacity=1,
            fill='tozeroy',
            fillcolor="rgba(235, 64, 52,0.5)",
            showlegend=False
        ))
        
        rad_rolling = df_new_dep["incid_rad"].rolling(window=7).mean()
        dc_rolling = df_new_dep["incid_dc"].rolling(window=7).mean()
        sorties_rolling = (rad_rolling + dc_rolling).values
        
        fig.add_trace(go.Scatter(
            x = dates,
            y = sorties_rolling,
            name = "",
            marker_color='green',
            line_width=0,
            opacity=1,
            fill='tozeroy',
            fillcolor="rgba(12, 161, 2, 0.5)",
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x = dates,
            y = [entrees_rolling[i] if entrees_rolling[i]<sorties_rolling[i] else sorties_rolling[i] for i in range(len(entrees_rolling))],
            name = "",
            marker_color='yellow',
            line_width=0,
            opacity=1,
            fill='tozeroy',
            fillcolor="rgba(255, 255, 255, 1)",
            showlegend=False
        ))

        
        fig.add_trace(go.Scatter(
            x = dates,
            y = sorties_rolling,
            name = "",
            marker_color='green',
            line_width=6,
            opacity=1,
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x = dates,
            y =entrees_rolling,
            name = "",
            marker_color='red',
            line_width=6,
            opacity=1,
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
        line=dict(color="green",width=0.5, dash="dot")
        )

        fig.add_trace(go.Scatter(
            x = [dates[-1]],
            y = [sorties_rolling[-1]],
            name = "",
            mode="markers",
            marker_color='green',
            marker_size=13,
            opacity=1,
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x = [dates[-1]],
            y = [entrees_rolling[-1]],
            name = "",
            mode="markers",
            marker_color='red',
            marker_size=13,
            opacity=1,
            showlegend=False
        ))

        ###
        fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), ) #range=["2020-03-17", last_day_plot_dashboard]
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=range_y)
        
        # Here we modify the tickangle of the xaxis, resulting in rotated labels.
        fig.update_layout(
            paper_bgcolor='rgba(255,255,255,1)',
            plot_bgcolor='rgba(255,255,255,1)',
            margin=dict(
                    l=50,
                    r=150,
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
                            y=1.01,
                            font=dict(size=14),
                            xref='paper',
                            yref='paper',
                            text="Moyenne mobile 7 jours. Données Santé publique France. Auteurs @eorphelin @guillaumerozier - <b>covidtracker.fr</b>.", #'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    
                            showarrow = False
                        ),

                        ]
                    )

        if entrees_rolling[-1]<sorties_rolling[-1]:
            y_e = -20
            y_s = -100
        else:
            y_e = -100
            y_s = -20
            
        fig['layout']['annotations'] += (
            dict(
            x = "2020-05-20", y = (entrees_rolling[62]+sorties_rolling[62])/2, # annotation point
            xref='x1', 
            yref='y1',
            text="L'aire représente le solde.<br>Si elle est <span style='color:green'>verte</span>, il y a plus de sorties que d'entrées,<br>le nombre de lits occupés diminue.",
            xshift=0,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=10
                ),
            bgcolor="rgba(255, 255, 255, 0)",
            opacity=0.8,
            ax=80,
            ay=-100,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=6,
            showarrow=True
        ),
            dict(
                x = dates[-1], y = (entrees_rolling[-1]), # annotation point
                xref='x1', 
                yref='y1',
                text=" <b>{} {}".format(round(entrees_rolling[-1], 1), "entrées à l'hôpital</b><br>en moyenne le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="red",
                    size=12
                    ),
                bgcolor="rgba(255, 255, 255, 0)",
                opacity=0.8,
                ax=100,
                ay=y_e,
                arrowcolor="red",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
            ),
            dict(
                x = dates[-1], y = (sorties_rolling[-1]), # annotation point
                xref='x1', 
                yref='y1',
                text=" <b>{} {}".format(round(sorties_rolling[-1], 1), "sorties de l'hôpital</b><br>en moyenne le {}.<br>dont {} décès et<br>{} retours à domicile".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), round(dc_rolling.values[-1], 1), round(rad_rolling.values[-1], 1))),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="green",
                    size=12
                    ),
                bgcolor="rgba(255, 255, 255, 0)",
                opacity=0.8,
                ax=100,
                ay=y_s,
                arrowcolor="green",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
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
                text="",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                showarrow=False
                        ))

        fig.write_image(PATH + "images/charts/france/departements_dashboards/{}.jpeg".format(name_fig+i), scale=1.5, width=1100, height=600)

        #plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/departements_dashboards/{}.html'.format(name_fig+i), auto_open=False)
        print("> " + name_fig)
            
#hosp_journ_elias("Savoie")


# In[18]:


def rea_journ(departement):
    df_dep = df_departements[df_departements["departmentName"] == departement]
    df_new_dep = df_new_departements[df_new_departements["departmentName"] == departement]
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "rea_journ_" + departement
    title = "Personnes en <b>réanimation</b> pour Covid19 - <b>" + departement + "</b>"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_dep["rea"],
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
        y = [df_dep["rea"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(201, 4, 4)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Bar(
        x = df_new_dep["jour"],
        y = df_new_dep["incid_rea"],
        name = "Admissions",
        marker_color='rgb(201, 4, 4)',
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_dep["jour"],
        y = df_new_dep["incid_rea"].rolling(window=7).mean(),
        name = "Admissions",
        marker_color='rgb(201, 4, 4)',
        marker_size=2,
        opacity=0.8,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

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
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_dep["rea"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_dep["rea"].values[-1], "personnes<br>en réanimation</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-250,
            ay=-90,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
           dict(
            x = df_new_dep["jour"].values[-1], y = (df_new_dep["incid_rea"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_dep["incid_rea"].values[-1], "<br>admissions"),
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
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    
#rea_journ("Isère")


# In[19]:


def dc_journ(departement): 
    df_dep = df_new_departements[df_new_departements["departmentName"] == departement]
    dc_new_rolling = df_dep["incid_dc"].rolling(window=7).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "dc_journ_"+departement, [0, df_dep["incid_dc"].max()]
    title = "Décès <b>hospitaliers quotidiens</b> du Covid19 - <b>" + departement + "</b>"

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x = df_dep["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(0,0,0,0.3)",
        showlegend=False
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
        x = df_dep["jour"],
        y = df_dep["incid_dc"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

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
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                         font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = dc_new_rolling.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % math.trunc(round(dc_new_rolling.values[-1], 2)), "décès quotidiens</b><br>en moyenne<br>du {} au {}.".format(datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-250,
            ay=-90,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    
#dc_journ("Paris")


# In[20]:



def saturation_rea_journ(dep):
    df_dep = df_departements_lits[df_departements_lits["departmentName"] == dep]
    df_saturation = 100 * df_dep["rea"] / df_dep["LITS_y"]
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "saturation_rea_journ_"+dep, [0, df_saturation.max()]
    title = "<b>Occupation des réa.</b> par les patients Covid19 - " + dep

    fig = go.Figure()

    colors_sat = ["green" if val < 40 else "red" if val > 80  else "orange" for val in df_saturation.values]
    fig.add_trace(go.Bar(
        x = df_dep["jour"],
        y = df_saturation,
        name = "Saturation",
        marker_color=colors_sat,
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(8, 115, 191, 0.3)",
        showlegend=False
    ))

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

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
                    size=20),
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
            x = dates[-1], y = df_saturation.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % round(df_saturation.values[-1]), " %</b> des lits de réa. occupés par<br>des patients Covid19 le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color=colors_sat[-1],
                size=20
                ),
            opacity=1,
            ax=-250,
            ay=-70,
            arrowcolor=colors_sat[-1],
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    return df_saturation.values[-1]


# In[21]:


#for dep in departements:
    #comparaison_cas_dc(dep)


# In[22]:


import cv2
import shutil
        
shutil.rmtree(PATH+"images/charts/france/covidep")
os.mkdir(PATH+"images/charts/france/covidep")
os.mkdir(PATH+"images/charts/france/covidep/lower_low")
os.mkdir(PATH+"images/charts/france/covidep/higher_low")
os.mkdir(PATH+"images/charts/france/covidep/lower_high")
os.mkdir(PATH+"images/charts/france/covidep/higher_high")
stats = {"higher_low": [], "higher_high": [], "lower_low": [], "lower_high": [], "update": dates[-1][-2:] + "/" + dates[-1][-5:-3]}

for dep in departements:
    hosp_journ_elias(dep)
    class_dep = incid_dep(dep)
    stats[class_dep] += [dep]
    cas_journ(dep)
    hosp_journ(dep)
    rea_journ(dep)
    dc_journ(dep)
    hosp_comparaison_vagues(dep)
    comparaison_cas_dc(dep)
    
    im1 = cv2.imread(PATH+'images/charts/france/departements_dashboards/cas_journ_{}.jpeg'.format(dep))
    im2 = cv2.imread(PATH+'images/charts/france/departements_dashboards/hosp_journ_{}.jpeg'.format(dep))
    im3 = cv2.imread(PATH+'images/charts/france/departements_dashboards/rea_journ_{}.jpeg'.format(dep))
    im4 = cv2.imread(PATH+'images/charts/france/departements_dashboards/dc_journ_{}.jpeg'.format(dep))

    im_haut = cv2.hconcat([im1, im2])
    #cv2.imwrite('images/charts/france/tests_combinaison.jpeg', im_h)
    im_bas = cv2.hconcat([im3, im4])

    im_totale = cv2.vconcat([im_haut, im_bas])
    cv2.imwrite(PATH+'images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg'.format(dep), im_totale)
    
    #os.remove(PATH+'images/charts/france/departements_dashboards/cas_journ_{}.jpeg'.format(dep))
    #os.remove('images/charts/france/departements_dashboards/hosp_journ_{}.jpeg'.format(dep))
    #os.remove(PATH+'images/charts/france/departements_dashboards/rea_journ_{}.jpeg'.format(dep))
    #os.remove(PATH+'images/charts/france/departements_dashboards/dc_journ_{}.jpeg'.format(dep))

with open(PATH + 'images/charts/france/covidep/stats.json', 'w') as outfile:
    json.dump(stats, outfile)
    


# In[23]:


for dep in departements:
    print("variants " + dep)
    nombre_variants(dep)


# In[24]:


with open(PATH_STATS + 'incidence_departements.json', 'r') as f:
    incidence_departements = json.load(f)
    
for dep in departements:
    saturation_rea = saturation_rea_journ(dep)
    incidence_departements["donnees_departements"][dep]["saturation_rea"] = saturation_rea

with open(PATH_STATS + 'incidence_departements.json', 'w') as outfile:
    json.dump(incidence_departements, outfile)


# In[25]:


n_tot=1
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

for i in range(0, n_tot):
    evol_tests_deps, evol_hosp_deps = [], []

    fig = go.Figure()
    fig.add_shape(type="rect",
            x0=-1000, y0=0, x1=0, y1=1000,
            line=dict(color="orange",width=0.5, dash="dot"), fillcolor="orange", opacity=0.2,
            layer="below"
        )
    fig.add_shape(type="rect",
            x0=0, y0=-1000, x1=1000, y1=0,
            line=dict(color="orange",width=0.5, dash="dot"), fillcolor="orange", opacity=0.2,
            layer="below"
        )

    fig.add_shape(type="rect",
            x0=0, y0=0, x1=1000, y1=1000,
            line=dict(color="Red",width=0.5, dash="dot"), fillcolor="red", opacity=0.2,
            layer="below"
        )

    fig.add_shape(type="rect",
            x0=-1000, y0=-1000, x1=0, y1=0,
            line=dict(color="red",width=0.5, dash="dot"), fillcolor="green", opacity=0.2,
            layer="below"
        )
    
    ### Reds
    """for (color, x_sign, y_sign, translation_x, translation_y) in [("red", "+", "+", 0, 0), ("orange", "+", "+", -200, 0), ("orange", "+", "+", 0, -200), ("green", "-", "-", 0, 0)]:
        for j in range(4):
            x0=j*50+translation_x
            y0=0+translation_y
            x1=50+j*50+translation_x
            y1=50+j*50+translation_y
            
            if y_sign == "-":
                y0 = -y0
                y1 = -y1
                
            if x_sign == "-":
                x0 = -x0
                x1 = -x1

            fig.add_shape(type="rect",
                    x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(color="red",width=0.5, dash="dot"), fillcolor=color, opacity=0.07+0.07*j,
                    layer="below" 
                )
            
            x0=0+translation_x
            y0=0+j*50+translation_y
            x1=0+j*50+translation_x
            y1=50+j*50+translation_y
            
            if y_sign == "-":
                y0 = -y0
                y1 = -y1
                
            if x_sign == "-":
                x0 = -x0
                x1 = -x1
                
            fig.add_shape(type="rect",
                    x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(color="red",width=0.5, dash="dot"), fillcolor=color, opacity=0.07+0.07*j,
                    layer="below"
                )"""
    

    deps_vert, deps_orange, deps_rouge = [], [], []
    nb_vert, nb_orange, nb_rouge = 0, 0, 0
    for dep in departements:
        df_incid_dep = df_incid_departements[df_incid_departements["departmentName"]==dep]
        tests_dep_rolling = df_incid_dep["P"].rolling(window=7).mean().values
        evol_tests_dep = (tests_dep_rolling[-1-i] - tests_dep_rolling[-8-i]) / tests_dep_rolling[-8] * 100
        evol_tests_deps += [evol_tests_dep]

        hosp_dep_rolling = df_new_departements[df_new_departements["departmentName"]==dep]["incid_hosp"].rolling(window=7).mean().values
        evol_hosp_dep = ( hosp_dep_rolling[-1-i] - hosp_dep_rolling[-8-i]) / hosp_dep_rolling[-8] * 100
        evol_hosp_deps += [evol_hosp_dep]

        if (evol_tests_dep < 0) & (evol_hosp_dep<0):
            color = "green"
            deps_vert += [df_incid_dep["dep"].values[0]]
            nb_vert += 1

        elif (evol_tests_dep > 0) & (evol_hosp_dep > 0):
            color = "red"
            deps_rouge += [df_incid_dep["dep"].values[0]]
            nb_rouge += 1

        else:
            color = "orange"
            deps_orange += [df_incid_dep["dep"].values[0]]
            nb_orange += 1

        fig.add_trace(go.Scatter(
            x = [evol_tests_dep],
            y = [evol_hosp_dep],
            name = dep,
            text=["<b>"+df_incid_dep["dep"].values[0]+"</b>"],
            textfont=dict(size=10),
            marker=dict(size=15,
                        color = color,
                        line=dict(width=0.3,
                            color='DarkSlateGrey')),
            line_width=8,
            opacity=0.8,
            fill='tozeroy',
            mode='markers+text',
            fillcolor="rgba(8, 115, 191, 0.3)",
            textfont_color="white",
            showlegend=False,
            textposition="middle center"
        ))
    
    def make_string_deps(deps_list):
        deps_list = sorted(deps_list)
        list_string = [""]
        
        for idx,dep in enumerate(deps_list):
            list_string[-1] += dep

            if (idx==len(deps_list)-1) or (len(list_string[-1])/150 >= 1):
                list_string += [""]
            else:
                list_string[-1] += ", "
                
        return_string=""    
        for idx,liste in enumerate(list_string):
            return_string += liste
            if idx < len(list_string)-1:
                return_string += "<br>"
                
        if len(return_string)==0:
            return_string = "aucun"
            
        return return_string
    
    #liste_deps_str = "{} en <b>vert</b> : {}<br><br>{} en <b>orange</b> : {}<br><br>{} en <b>rouge</b> : {}".format(nb_vert, make_string_deps(deps_vert), nb_orange, make_string_deps(deps_orange), nb_rouge, make_string_deps(deps_rouge))
    liste_deps_str_vert = "<span style='color: green;'>Vert ({})</span> : {}<br>".format(nb_vert, make_string_deps(deps_vert))
    liste_deps_str_orange = "<span style='color: orange;'>Orange ({})</span> : {}<br>".format(nb_orange, make_string_deps(deps_orange))
    liste_deps_str_rouge = "<span style='color: red;'>Rouge ({})</span> : {}<br>".format(nb_rouge, make_string_deps(deps_rouge))
    
    liste_deps_str = liste_deps_str_vert + liste_deps_str_orange + liste_deps_str_rouge
    
    fig['layout']['annotations'] += (dict(
            x = 100, y = 100, # annotation point
            xref='x1', yref='y1',
            text="Les cas augmentent.<br>Les admissions à l'hôpital augmentent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = -50, y = -50, # annotation point
            xref='x1', yref='y1',
            text="Les cas baissent.<br>Les admissions à l'hôpital baissent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = -50, y = 100, # annotation point
            xref='x1', yref='y1',
            text="Les cas baissent.<br>Les admissions à l'hôpital augmentent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = 100, y = -50, # annotation point
            xref='x1', yref='y1',
            text="Les cas augmentent.<br>Les admissions à l'hôpital baissent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
                x=0.5,
                y=1.05,
                xref='paper',
                yref='paper',
                font=dict(size=14),
                text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                        ),
            dict(
                x=-0.08,
                y=-0.3,
                xref='paper',
                yref='paper',
                font=dict(size=14),
                align="left",
                text=liste_deps_str, showarrow = False
          ),)

    fig.update_xaxes(title="Évolution hebdomadaire des cas positifs", range=[-100, 200], ticksuffix="%")
    fig.update_yaxes(title="Évolution hedbomadaire des admissions à l'hôpital", range=[-100, 200], ticksuffix="%")
    fig.update_layout(
         title={
                        'text': "<b>Évolution des cas et hospitalisations dans les départements</b> • {}".format(datetime.strptime(dates[-i-1], '%Y-%m-%d').strftime('%d %b')),
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
        titlefont = dict(
                    size=20),
        margin=dict(
            b=200
        ),
        )
    fig.write_image(PATH+"images/charts/france/evolution_deps/{}_{}.jpeg".format("evolution_deps", dates_incid[-(i+1)]), scale=3, width=1000, height=900)
    
    if i==0:
            fig.write_image(PATH+"images/charts/france/evolution_deps/{}_{}.jpeg".format("evolution_deps", 0), scale=3, width=1000, height=900)
            plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/evolution_deps/evolution_deps_0.html', auto_open=False)


# In[26]:


#import glob
n_tot = 40

import cv2
for (folder, n, fps) in [("evolution_deps", n_tot, 3)]:
    img_array = []
    for i in range(n-1, 0-1, -1):
        print(i)
        try:
            img = cv2.imread((PATH + "images/charts/france/{}/evolution_deps_{}.jpeg").format(folder, dates_incid[-(i+1)]))
            height, width, layers = img.shape
            size = (width,height)
            img_array.append(img)

            if i==-n:
                for k in range(4):
                    img_array.append(img)

            if i==-1:
                for k in range(12):
                    img_array.append(img)
        except:
            print("image manquante")

    out = cv2.VideoWriter(PATH + 'images/charts/france/{}/evolution_deps.mp4'.format(folder),cv2.VideoWriter_fourcc(*'MP4V'), fps, size)

    for i in range(len(img_array)):
        out.write(img_array[i])

    out.release()
    
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-i", PATH + "images/charts/france/{}/evolution_deps.mp4".format(folder), PATH + "images/charts/france/{}/evolution_deps_opti.mp4".format(folder)])
        subprocess.run(["rm", PATH + "images/charts/france/{}/evolution_deps.mp4".format(folder)])   
    except:
        print("error conversion h265")


# In[27]:


"""for idx,dep in enumerate(departements):
    numero_dep = df[df["departmentName"] == dep]["dep"].values[-1]
    
    heading = "<!-- wp:heading --><h2 id=\"{}\">{}</h2><!-- /wp:heading -->\n".format(dep, dep + " (" + numero_dep + ")")
    string = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg\" width=\"75%\"> </a></p>\n".format(dep, dep)
    string2 = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/heatmaps_deps/heatmap_taux_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/heatmaps_deps/heatmap_taux_{}.jpeg\" width=\"60%\"> </a></p>\n".format(numero_dep, numero_dep)
    string_saturation = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/saturation_rea_journ_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/saturation_rea_journ_{}.jpeg\" width=\"60%\"> </a></p>\n".format(dep, dep)
    space = "<!-- wp:spacer {\"height\":50} --><div style=\"height:50px\" aria-hidden=\"true\" class=\"wp-block-spacer\"></div><!-- /wp:spacer -->"
    retourmenu="<a href=\"#Menu\">Retour au menu</a>"
    print(space+retourmenu+heading+string+string2+string_saturation)
"""


# In[28]:


"""#print("<!-- wp:buttons --><div class=\"wp-block-buttons\">\n")
output = ""
for dep in departements:
    numero_dep = df[df["departmentName"] == dep]["dep"].values[-1]
    output+= "<a href=\"#{}\">{} ({})</a> • ".format(dep, dep, numero_dep)
#print(output[:-2])

"""
#print("<!-- /wp:buttons -->")

