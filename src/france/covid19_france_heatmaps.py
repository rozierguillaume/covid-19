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


# In[1]:


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
import plotly.figure_factory as ff

PATH="../../"

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
now = datetime.now()


# In[2]:


df, df_confirmed, dates, _, _, _, _, df_incid, df_tests_viros = data.import_data()


# In[8]:


deps_tests = list(dict.fromkeys(list(df_tests_viros['dep'].values))) 
deps_name = np.array(list(dict.fromkeys(list(df["departmentName"].values)))[:])

#df_tests_viros = df_tests_viros[df_tests_viros['cl_age90'] != 0]

for (name, data, title, scale_txt, data_example, digits) in [("cas", '', "Taux d'<br>incidence", " cas", " cas", 1)]:
    for idx,dep in enumerate(deps_tests): #
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        
        df_tests_viros_dep = df_tests_viros[df_tests_viros["dep"] == dep]
        #df_tests_viros_dep = df_tests_viros_dep.groupby(['jour', 'cl_age90']).sum().reset_index()
        
        df_tests_rolling = pd.DataFrame()
        array_positif = []
        array_taux = []
        array_incidence = []
        for age in sorted(list(dict.fromkeys(list(df_tests_viros_dep['cl_age90'].values)))): 
            tranche = df_tests_viros_dep[df_tests_viros_dep["cl_age90"]==age]
            tranche.index = pd.to_datetime(tranche["jour"])
            tranche = tranche[tranche.index.max() - timedelta(days=7*32-1):].resample('7D').sum()
            
            array_positif += [tranche["P"].astype(int)]
            array_taux += [np.round((tranche["P"].fillna(0)/tranche["T"].fillna(1)).fillna(0)*100, 1)]
            array_incidence += [round(tranche["P"].fillna(0) / tranche["pop"] * 7 * 100000).astype(int)]
            dates_heatmap = list(tranche.index.astype(str).values)

        
        dates_heatmap_firstday = tranche.index.values
        dates_heatmap_lastday = tranche.index + timedelta(days=6)
        dates_heatmap = [str(dates_heatmap_firstday[i])[8:10] + "/" + str(dates_heatmap_firstday[i])[5:7] + "<br>" + str(dates_heatmap_lastday[i])[8:10] + "/" + str(dates_heatmap_lastday[i])[5:7] for i, val in enumerate(dates_heatmap_firstday)]

        fig = ff.create_annotated_heatmap(
            z=array_incidence, #df_tests_rolling[data].to_numpy()
            x=dates_heatmap,
            y=[" <b>Tous âges</b>"] + [" " + str(x-9) + " à " + str(x)+" ans" if x!=99 else "+ 90 ans" for x in range(9, 109, 10)],
            showscale=True,
            font_colors=["white", "white"],
            coloraxis="coloraxis",
            #text=df_tests_rolling[data],
            annotation_text = array_incidence
            )

        annot = []

        fig.update_xaxes(side="bottom", tickfont=dict(size=9))
        fig.update_yaxes(tickfont=dict(size=9))
        fig['layout']['yaxis'].update(side='right')
    
        fig.update_layout(
            title={
                'text': "{} du Covid19 en fonction de l\'âge • <b>Dép. {}</b>".format(title.replace("<br>", " "), dep),
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
            coloraxis=dict(
                cmin=0, cmax=800,
                colorscale = [[0, "green"], [0.08, "#ffcc66"], [0.25, "#f50000"], [0.5, "#b30000"], [1, "#3d0000"]], #[[0, "green"], [0.2, "#ffcc66"], [0.8, "#f50000"], [1, "#b30000"]],
                #color_continuous_scale=["green", "red"],
                colorbar=dict(
                    #title="{}<br>du Covid19<br> &#8205;".format(title),
                    thicknessmode="pixels", thickness=12,
                    lenmode="pixels", len=300,
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
        
        annotations = annot + [
                        dict(
                            x=0.5,
                            y=-0.16,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            opacity=0.6,
                            font=dict(color="black", size=12),
                            text='Lecture : une case correspond au {} pour une tranche d\'âge (à lire à droite) et à une date donnée (à lire en bas).<br>Du rouge correspond à un {} élevé.  <i>Date : {} - Source : <b>@GuillaumeRozier</b> covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                            showarrow = False
                        ),
                    ]
        fig.update_layout(coloraxis_colorbar_x=-0.15)
        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 10
            fig.layout.annotations[i].text = "<b>"+fig.layout.annotations[i].text+"</b>"
        
        for annot in annotations:
            fig.add_annotation(annot)

        name_fig = "heatmaps_deps/heatmap_"+"taux"+"_"+dep
        fig.write_image(PATH+"images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1300, height=550)
        #fig.write_image(PATH+"images/charts/france/{}_SD.jpeg".format(name_fig), scale=0.5, width=900, height=550)
        #fig.show()
        plotly.offline.plot(fig, filename = PATH+'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[9]:


df_incid_regions = df_incid.groupby(["jour", "regionName", "cl_age90"]).sum().reset_index()
regs = list(dict.fromkeys(list(df_incid_regions['regionName'].values))) 

for (name, data, title, scale_txt, data_example, digits) in [("cas", '', "Taux d'<br>incidence", " cas", " cas", 1)]:
    for idx, reg in enumerate(regs): #deps_tests.drop("975", "976", "977", "978")
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        
        df_incid_reg = df_incid_regions[df_incid_regions["regionName"] == reg]
        
        df_tests_rolling = pd.DataFrame()
        array_positif = []
        array_taux = []
        array_incidence = []
        for age in list(dict.fromkeys(list(df_incid_reg['cl_age90'].values))):
            print(age)
            tranche = df_incid_reg[df_incid_reg["cl_age90"]==age]
            tranche.index = pd.to_datetime(tranche["jour"])
            tranche = tranche[tranche.index.max() - timedelta(days=7*32-1):].resample('7D').sum()
            
            array_positif += [tranche["P"].astype(int)]
            array_taux += [np.round((tranche["P"].fillna(0)/tranche["T"].fillna(1)).fillna(0)*100, 1)]
            array_incidence += [np.trunc(tranche["P"].fillna(0) / tranche["pop"] * 7 * 100000).astype(int)]
            dates_heatmap = list(tranche.index.astype(str).values)

        dates_heatmap_firstday = tranche.index.values
        dates_heatmap_lastday = tranche.index + timedelta(days=6)
        dates_heatmap = [str(dates_heatmap_firstday[i])[8:10] + "/" + str(dates_heatmap_firstday[i])[5:7] + "<br>" + str(dates_heatmap_lastday[i])[8:10] + "/" + str(dates_heatmap_lastday[i])[5:7] for i, val in enumerate(dates_heatmap_firstday)]

        fig = ff.create_annotated_heatmap(
            z=array_incidence, #df_tests_rolling[data].to_numpy()
            x=dates_heatmap,
            y=["<b>Tous âges</b>"] + [str(x-9) + " à " + str(x)+" ans" if x!=99 else "+ 90 ans" for x in range(9, 109, 10)],
            showscale=True,
            font_colors=["white", "white"],
            coloraxis="coloraxis",
            #text=df_tests_rolling[data],
            annotation_text = array_incidence
            )

        annot = []

        fig.update_xaxes(side="bottom", tickfont=dict(size=9))
        fig.update_yaxes(tickfont=dict(size=9))
    
        fig.update_layout(
            title={
                'text': "{} du Covid19 en fonction de l\'âge • <b>{}</b>".format(title.replace("<br>", " "), reg),
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
            coloraxis=dict(
                cmin=0, cmax=800,
                colorscale = [[0, "green"], [0.08, "#ffcc66"], [0.25, "#f50000"], [0.5, "#b30000"], [1, "#3d0000"]], #[[0, "green"], [0.2, "#ffcc66"], [0.8, "#f50000"], [1, "#b30000"]],
                #color_continuous_scale=["green", "red"],
                colorbar=dict(
                    #title="{}<br>du Covid19<br> &#8205;".format(title),
                    thicknessmode="pixels", thickness=12,
                    lenmode="pixels", len=300,
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
        
        annotations = annot + [
                        dict(
                            x=0.5,
                            y=-0.16,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            opacity=0.6,
                            font=dict(color="black", size=12),
                            text='Lecture : une case correspond au {} pour une tranche d\'âge (à lire à droite) et à une date donnée (à lire en bas).<br>Du rouge correspond à un {} élevé.  <i>Date : {} - Source : <b>@guillaumerozier</b> covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                            showarrow = False
                        ),
                    ]
        
        fig['layout']['yaxis'].update(side='right')
        fig.update_layout(coloraxis_colorbar_x=-0.15)
        
        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 11
            fig.layout.annotations[i].text = "<b>"+fig.layout.annotations[i].text+"</b>"
        
        for annot in annotations:
            fig.add_annotation(annot)

        name_fig = "heatmaps_regs/heatmap_"+"taux"+"_"+reg
        fig.write_image(PATH+"images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1300, height=550)
        #fig.write_image(PATH+"images/charts/france/{}_SD.jpeg".format(name_fig), scale=0.5, width=900, height=550)
        #fig.show()
        #plotly.offline.plot(fig, filename = PATH+'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[ ]:


"""OLD
deps_tests = list(dict.fromkeys(list(df_tests_viros['dep'].values))) 
deps_name = np.array(list(dict.fromkeys(list(df["departmentName"].values)))[:])

df_tests_viros = df_tests_viros[df_tests_viros['cl_age90'] != 0]

for (name, data, title, scale_txt, data_example, digits) in [("taux", 'P_taux', "Taux de<br>positivité", "%", "%", 1)]:
    for idx,dep in enumerate(deps_tests):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        
        df_tests_viros_dep = df_tests_viros[df_tests_viros["dep"] == dep]
        df_tests_viros_dep = df_tests_viros_dep.groupby(['jour', 'cl_age90']).sum().reset_index()
        
        #df_essai = df_tests_viros_france.groupby(['cl_age90', 'jour']).sum().rolling(window=20).mean()
        df_tests_rolling = pd.DataFrame()
        for age in list(dict.fromkeys(list(df_tests_viros_dep['cl_age90'].values))):
            df_temp = pd.DataFrame()
            df_tests_viros_dep_temp = df_tests_viros_dep[df_tests_viros_dep['cl_age90'] == age]
            df_temp['jour'] = df_tests_viros_dep_temp['jour']
            df_temp['cl_age90'] = df_tests_viros_dep_temp['cl_age90']
            df_temp['P'] = (df_tests_viros_dep_temp['P']).rolling(window=7).mean()
            df_temp['T'] = (df_tests_viros_dep_temp['T']).rolling(window=7).mean()
            df_temp['P_taux'] = (df_temp['P']/df_temp['T']*100).rolling(window=7).mean()
            df_tests_rolling = pd.concat([df_tests_rolling, df_temp])
        df_tests_rolling = df_tests_rolling[df_tests_rolling['jour'] > "2020-05-18"]
        df_tests_rolling['cl_age90'] = df_tests_rolling['cl_age90'].replace(90,99)

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
                cmin=0, cmax=15,
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
                            y=0.5,
                            xref='paper',
                            yref='paper',
                            opacity=0.6,
                            font=dict(color="white", size=55),
                            text="Dép. <b>{}</b>".format(dep),
                            showarrow=False
                        ),
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

        name_fig = "heatmaps_deps/heatmap_"+name+"_"+dep
        fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
        #fig.show()
        plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)"""


# In[ ]:


"""string= ""
for dep in deps_tests:
    string += "<a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/heatmaps_deps/heatmap_taux_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"> <img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/heatmaps_deps/heatmap_taux_{}_SD.jpeg\" width=\"20%\"</a>\n".format(dep, dep)
print(string)"""


# In[ ]:


"""for (name, data, title, scale_txt, data_example, digits) in [("taux_reg", 'P_taux', "Taux de<br>positivité", "%", "%", 1)]:
    
    ni, nj = 5, 4
    i, j = 1, 1

    df_region[val+"_new"] = df_region[val].diff()
    max_value = df_region[val].max()
    
    regions_ordered = df_region[df_region['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["regionName"].values
    regions_ordered = list(dict.fromkeys(list(regions_ordered)))[:]
    
    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles=[ "<b>"+ str(r) +"</b>" for r in (regions_ordered[:11] + [""] + regions_ordered[11:14]+[""]+regions_ordered[14:])], vertical_spacing = 0.06, horizontal_spacing = 0.01)
    
    
    df_tests_viros = df_tests_viros[df_tests_viros['cl_age90'] != 0]
        
    for region in regions_ordered:

        #df_essai = df_tests_viros_france.groupby(['cl_age90', 'jour']).sum().rolling(window=20).mean()
        df_tests_rolling = pd.DataFrame()
        df_tests_viros_reg = df_tests_viros[df_tests_viros["reg"] == reg].groupby(['jour', 'cl_age90']).sum().reset_index()
        
        for age in list(dict.fromkeys(list(df_tests_viros_reg['cl_age90'].values))):
            df_temp = pd.DataFrame()
            df_tests_viros_france_temp = df_tests_viros_france[df_tests_viros_france['cl_age90'] == age]
            df_temp['jour'] = df_tests_viros_france_temp['jour']
            df_temp['cl_age90'] = df_tests_viros_france_temp['cl_age90']
            df_temp['P'] = (df_tests_viros_france_temp['P']).rolling(window=7).mean()
            df_temp['T'] = (df_tests_viros_france_temp['T']).rolling(window=7).mean()
            df_temp['P_taux'] = (df_tests_viros_france_temp['P']/df_tests_viros_france_temp['T']*100).rolling(window=7).mean()
            df_tests_rolling = pd.concat([df_tests_rolling, df_temp])
        df_tests_rolling = df_tests_rolling[df_tests_rolling['jour'] > "2020-05-18"]
        df_tests_rolling['cl_age90'] = df_tests_rolling['cl_age90'].replace(90,99)
        
        fig.add_trace(data=go.Heatmap(
                z=df_tests_rolling[data],
                x=df_tests_rolling['jour'],
                y=df_tests_rolling['cl_age90'],
                coloraxis="coloraxis"
                ), i,j)

        j+=1
        if j == nj+1 or ((i >= 3) & (j == nj) & (i<5)):
            i+=1
            j=1
    
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
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)"""

