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

The charts are exported to 'charts/images/france'.
Data is download to/imported from 'data/france'.
Requirements: please see the imports below (use pip3 to install them).

"""


# In[2]:


import pandas as pd
import france_data_management as data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import plotly
import cv2
PATH = "../../"
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


# In[3]:


data.download_data()


# In[43]:


df_hosp_nouveaux_dep = data.import_data_new()
df_hosp_nouveaux_dep = df_hosp_nouveaux_dep[df_hosp_nouveaux_dep["dep"].str.len()<3].groupby("jour").sum().reset_index()

df_tests_viros_dep = data.import_data_tests_viros()
df_tests_viros_dep = df_tests_viros_dep[df_tests_viros_dep["cl_age90"]==0]
df_tests_viros_dep = df_tests_viros_dep[df_tests_viros_dep["dep"].str.len()<3].groupby("jour").sum().reset_index()

df_metropole = df_tests_viros_dep.merge(df_hosp_nouveaux_dep, left_on="jour", right_on="jour")


# In[46]:


df_hosp_nouveaux_dep = data.import_data_new()
df_hosp_nouveaux_dep = df_hosp_nouveaux_dep[df_hosp_nouveaux_dep["dep"].str.len()==3].groupby("jour").sum().reset_index()

df_tests_viros_dep = data.import_data_tests_viros()
df_tests_viros_dep = df_tests_viros_dep[df_tests_viros_dep["cl_age90"]==0]
df_tests_viros_dep = df_tests_viros_dep[df_tests_viros_dep["dep"].str.len()==3].groupby("jour").sum().reset_index()

df_dromcom = df_tests_viros_dep.merge(df_hosp_nouveaux_dep, left_on="jour", right_on="jour")


# In[5]:


df_hosp = data.import_data_hosp_clage().groupby(["jour", "cl_age90"]).sum().reset_index()
df_hosp_nouveaux = data.import_data_new().groupby("jour").sum().reset_index()

df_hosp = df_hosp[df_hosp.cl_age90 == 0].groupby("jour").sum().reset_index()

df_tests_viro = data.import_data_tests_sexe()
df_tests_viro = df_tests_viro[df_tests_viro.cl_age90 == 0].groupby("jour").sum().reset_index()


# In[6]:


df = df_tests_viro.merge(df_hosp_nouveaux, left_on="jour", right_on="jour")

df = df.reset_index()
df["hosp_cas_ratio"] = df.incid_hosp.rolling(window=7).mean()/df.P.rolling(window=7).mean().shift(7) * 100
df["dc_cas_ratio"] = df.incid_dc.rolling(window=7).mean()/df.P.rolling(window=7).mean().shift(14) * 100


# In[7]:


y1 = df.P.rolling(window=7).mean()/67000000*100000
y2 = df.incid_dc.rolling(window=7).mean().shift(-14)/67000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    marker_color='black',
    fillcolor="rgba(0,0,0,0.3)",
    name="Décès hospitaliers<br>avancés de 14 j.<br>pour {} Mio".format(round(coef_normalisation/1000000)),
    fill='tozeroy'))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Décès hospitaliers",
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
                            text="Cas pour 100 000 habitants et décès hospitaliers avancés de 14 j. pour {} Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/1000000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_dc_comparaison"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[70]:



pop=df_metropole["pop"].values[0]
y1 = df_metropole.P.rolling(window=7).mean()/pop*100000
y2 = df_metropole.incid_dc.rolling(window=7).mean().shift(-14)/pop

coef_normalisation = 10000000 #y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    marker_color='black',
    fillcolor="rgba(0,0,0,0.3)",
    name="Décès hospitaliers<br>avancés de 14 j.<br>pour {} Mio".format(round(coef_normalisation/1000000)),
    fill='tozeroy'))
fig.update_yaxes(range=[-80, 80])
fig.update_layout(
    title={
                        'text': "Cas vs. Décès hospitaliers [Fr. métrop.]",
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
                            text="Cas pour 100 000 habitants et décès hospitaliers avancés de 14 j. pour {} Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/1000000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_dc_comparaison_metropole"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[69]:


pop = df_dromcom["pop"].values[0]
y1 = df_dromcom.P.rolling(window=7).mean()/pop*100000
y2 = df_dromcom.incid_dc.rolling(window=7).mean().shift(-14)/pop

coef_normalisation = 10000000#y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    marker_color='black',
    fillcolor="rgba(0,0,0,0.3)",
    name="Décès hospitaliers<br>avancés de 14 j.<br>pour {} Mio".format(round(coef_normalisation/1000000)),
    fill='tozeroy'))
fig.update_yaxes(range=[-80, 80])
fig.update_layout(
    title={
                        'text': "Cas vs. Décès hospitaliers [DROM-COM]",
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
                            text="Cas pour 100 000 habitants et décès hospitaliers avancés de 14 j. pour {} Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/1000000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_dc_comparaison_dromcom"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[9]:


y1 = df.P.rolling(window=7).mean()/67000000*100000
y2 = df.incid_hosp.rolling(window=7).mean().shift(-7)/67000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    name="Adm. hôpital<br>avancées de 7 j.<br>pour {} Mio".format(round(coef_normalisation/100000)),
    marker_color='rgb(209, 102, 21)',
    fillcolor="rgba(209, 102, 21,0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Admissions à l'hôpital",
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
                            text="Cas pour 100 000 habitants et admissions à l'hôpital avancées de 7 jours pour {} Million d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/100000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_hospitalisations_comparaison"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[21]:


y1 = df_metropole.P.rolling(window=7).mean()/67000000*100000
y2 = df_metropole.incid_hosp.rolling(window=7).mean().shift(-7)/67000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    name="Adm. hôpital<br>avancées de 7 j.<br>pour {} Mio".format(round(coef_normalisation/100000)),
    marker_color='rgb(209, 102, 21)',
    fillcolor="rgba(209, 102, 21,0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Admissions à l'hôpital [Fr. métrop.]",
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
                            text="Cas pour 100 000 habitants et admissions à l'hôpital avancées de 7 jours pour {} Million d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/100000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_hospitalisations_comparaison_metropole"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[10]:


y1 = df.P.rolling(window=7).mean()/67000000*100000
y2 = df.incid_rea.rolling(window=7).mean().shift(-7)/67000000*5000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    name="Adm. soins critiques<br>avancées de 7 j.<br>pour 5 Mio",
    marker_color='rgb(201, 4, 4)',
    fillcolor="rgba(201, 4, 4,0.3)",
    fill='tozeroy'))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Admissions en soins critiques",
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
                            text="Cas pour 100 000 habitants et admissions en soins critiques (avancées de 7j) pour 5 Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_sc_comparaison"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[22]:


y1 = df_metropole.P.rolling(window=7).mean()/67000000*100000
y2 = df_metropole.incid_rea.rolling(window=7).mean().shift(-7)/67000000*5000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    name="Adm. soins critiques<br>avancées de 7 j.<br>pour 5 Mio",
    marker_color='rgb(201, 4, 4)',
    fillcolor="rgba(201, 4, 4,0.3)",
    fill='tozeroy'))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Admissions en soins critiques [Fr. métrop.]",
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
                            text="Cas pour 100 000 habitants et admissions en soins critiques (avancées de 7j) pour 5 Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_sc_comparaison_metropole"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[11]:



y1 = df.incid_hosp.rolling(window=7).mean().shift()
y2 = df.P.rolling(window=7).mean().shift(7)*0.09

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    line_width=8,
    opacity=0.2,
    name="Adm. hôpital",
    marker_color='orange',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    ))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    line_width=2,
    opacity=1,
    showlegend=False,
    marker_color='orange',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    ))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y2,
    line_width=8,
    opacity=0.2,
    name="Estimation adm. hôp.",
    marker_color='rgb(8, 115, 191)',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    ))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y2,
    line_width=2,
    opacity=1,
    showlegend=False,
    marker_color='rgb(8, 115, 191)',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    ))
fig.update_xaxes(range=["2021-01-01", df.jour.max()])
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Estimation des hospitalisations à partir des cas",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.17,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="La courbe bleue représente l'estimation des hospitalisations à partir des cas,<br>en fixant le taux d'hospitaliastion à sa valeur de janvier 2021<br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

#name_fig = "cas_hospitalisations_ratio"
#fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[12]:


date_old_wave = "2020-07-25"
date_new_wave = "2021-06-10"


# In[13]:


df_old_wave = df[df["jour"] >= date_old_wave]
df_new_wave = df[df["jour"] >= date_new_wave]

y2 = df_new_wave.incid_hosp.rolling(window=7).mean()
y1 = df_old_wave.incid_hosp.rolling(window=7).mean().values[:len(y2)+150]
x = [i for i in range(max(len(y1), len(y2)))]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x,
    y=y1,
    name="Vague 2020",
    line_width=4,
    marker_color="rgba(0, 0, 0, 0.4)",
    fillcolor="rgba(0, 0, 0, 0.05)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=x,
    y=y2,
    name="Vague 2021",
    line_width=4,
    marker_color='rgba(209, 102, 21, 1)',
    fillcolor='rgba(209, 102, 21, 0.3)',
    fill='tozeroy'))

fig.update_yaxes()
fig.update_layout(
    xaxis=dict(
        title="Numéro de jour à partir du <span style='color: rgba(0, 0, 0, 0.6);'>25 juillet 2020</span> • <span style='color: rgba(209, 102, 21, 1);'>10 juin 2021</span>"
    ),
    title={
                'text': "Admissions hôpital",
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
                            text="Vague 2020 à partir du 25 juillet 2020, vague 2021 à partir du 10 juin 2021 <br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "comparaison_vagues_hosp"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[14]:


y2 = df_new_wave.incid_rea.rolling(window=7).mean().dropna()
y1 = df_old_wave.incid_rea.rolling(window=7).mean().dropna().values[:len(y2)+150]
x = [i for i in range(max(len(y1), len(y2)))]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x,
    y=y1,
    name="Vague 2020",
    line_width=4,
    marker_color="rgba(0, 0, 0, 0.4)",
    fillcolor="rgba(0, 0, 0, 0.05)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=x,
    y=y2,
    name="Vague 2021",
    line_width=4,
    marker_color="rgba(201, 4, 4, 1)",
    fillcolor="rgba(201, 4, 4, 0.3)",
    fill='tozeroy'))

fig.update_yaxes()
fig.update_layout(
    xaxis=dict(
        title="Numéro de jour à partir du <span style='color: rgba(0, 0, 0, 0.6);'>25 juillet 2020</span> • <span style='color: rgba(201, 4, 4, 1);'>10 juin 2021</span>"
    ),
    title={
                'text': "Admissions soins critiques",
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
                            text="Vague 2020 à partir du 25 juillet 2020, vague 2021 à partir du 10 juin 2021 <br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "comparaison_vagues_sc"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[15]:


y2 = df_new_wave.incid_dc.rolling(window=7).mean().dropna()
y1 = df_old_wave.incid_dc.rolling(window=7).mean().dropna().values[:len(y2)+150]
x = [i for i in range(max(len(y1), len(y2)))]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x,
    y=y1,
    name="Vague 2020",
    line_width=4,
    marker_color="rgba(0, 0, 0, 0.4)",
    fillcolor="rgba(0, 0, 0, 0.05)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=x,
    y=y2,
    name="Vague 2021",
    line_width=4,
    marker_color="rgba(0, 0, 0, 1)",
    fillcolor="rgba(0, 0, 0, 0.3)",
    fill='tozeroy'))

fig.update_yaxes()
fig.update_layout(
    xaxis=dict(
        title="Numéro de jour à partir du <span style='color: rgba(0, 0, 0, 0.4);'>25 juillet 2020</span> • <span style='color: rgba(0, 0, 0, 1);'>10 juin 2021</span>"
    ),
    title={
                'text': "Décès hospitaliers",
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
                            text="Vague 2020 à partir du 25 juillet 2020, vague 2021 à partir du 10 juin 2021 <br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "comparaison_vagues_dc"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[16]:


y2 = df_new_wave["P"].rolling(window=7).mean().dropna()
y1 = df_old_wave["P"].rolling(window=7).mean().dropna().values[:len(y2)+150]
x = [i for i in range(max(len(y1), len(y2)))]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x,
    y=y1,
    name="Vague 2020",
    line_width=4,
    marker_color="rgba(0, 0, 0, 0.4)",
    fillcolor="rgba(0, 0, 0, 0.05)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=x,
    y=y2,
    name="Vague 2021",
    line_width=4,
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))

fig.update_yaxes()
fig.update_layout(
    xaxis=dict(
        title="Numéro de jour à partir du <span style='color: rgba(0, 0, 0, 0.6);'>25 juillet 2020</span> • <span style='color: rgba(209, 102, 21, 1);'>10 juin 2021</span>"
    ),
    title={
                        'text': "Cas positifs au Covid",
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
                            text="Vague 2020 à partir du 25 juillet 2020, vague 2021 à partir du 10 juin 2021. <br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "comparaison_vagues_cas"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[17]:


df_2021 = df[df["jour"] >= "2021-01-01"]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_2021.jour,
    y=df_2021.hosp_cas_ratio,
    line_color="black",
    showlegend=False))

fig.add_trace(go.Scatter(
    x=[df_2021.jour.values[-1]],
    y=[df_2021.hosp_cas_ratio.values[-1]],
    mode="markers",
    marker_size=7,
    line_color="black",
    showlegend=False))

fig.update_yaxes(ticksuffix=" %")
fig.update_layout(
    title={
                        'text': "Proportion des cas qui sont hospitalisés",
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
                            text="Proportion des admissions à l'hôpital par rapport aux cas positifs 7 jours plus tôt<br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)
y=df_2021.hosp_cas_ratio.values[-1]
fig['layout']['annotations'] += (dict(
                x = df.jour.values[-1], y = y, # annotation point
                xref='x1', 
                yref='y1',
                text="<b>{} %</b> des cas<br>sont hospitalisés".format(round(y, 1)),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="rgb(8, 115, 191)",
                    size=12
                    ),
                opacity=1,
                ax=80,
                ay=0,
                arrowcolor="rgb(8, 115, 191)",
                arrowsize=1.5,
                arrowwidth=0.5,
                arrowhead=0,
                showarrow=True
            ),)

name_fig = "cas_hospitalisations_ratio"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=950, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[18]:


df_2021 = df[df["jour"] >= "2021-01-01"]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_2021.jour,
    y=df_2021.dc_cas_ratio,
    line_color="black",
    showlegend=False))

fig.add_trace(go.Scatter(
    x=[df_2021.jour.values[-1]],
    y=[df_2021.dc_cas_ratio.values[-1]],
    mode="markers",
    marker_size=7,
    line_color="black",
    showlegend=False))

fig.update_yaxes(ticksuffix=" %")
fig.update_layout(
    title={
                        'text': "Proportion des cas qui sont décédés",
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
                            text="Proportion des décès hospitaliers par rapport aux cas positifs 14 jours plus tôt<br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)
y=df_2021.dc_cas_ratio.values[-1]
fig['layout']['annotations'] += (dict(
                x = df.jour.values[-1], y = y, # annotation point
                xref='x1', 
                yref='y1',
                text="<b>{} %</b> des cas<br>sont décédés".format(round(y, 1)),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="rgb(8, 115, 191)",
                    size=12
                    ),
                opacity=1,
                ax=80,
                ay=0,
                arrowcolor="rgb(8, 115, 191)",
                arrowsize=1.5,
                arrowwidth=0.5,
                arrowhead=0,
                showarrow=True
            ),)

name_fig = "cas_dc_ratio"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=950, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[19]:


im1 = cv2.imread(PATH + 'images/charts/france/comparaison_vagues_cas.jpeg')
im2 = cv2.imread(PATH + 'images/charts/france/comparaison_vagues_hosp.jpeg')
im3 = cv2.imread(PATH + 'images/charts/france/comparaison_vagues_sc.jpeg')
im4 = cv2.imread(PATH + 'images/charts/france/comparaison_vagues_dc.jpeg')

im_haut = cv2.hconcat([im1, im2])
im_bas = cv2.hconcat([im3, im4])

im_totale = cv2.vconcat([im_haut, im_bas])
cv2.imwrite(PATH + 'images/charts/france/comparaison_vagues_dashboard.jpeg', im_totale)


# In[ ]:




