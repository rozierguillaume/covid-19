#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

import holoviews as hv
import plotly.graph_objects as go
import plotly.express as pex
from plotly.subplots import make_subplots
hv.extension('bokeh')
PATH = "../../"


# In[2]:


women_bins = np.array([-600, -623, -653, -650, -670, -578, -541, -411, -322, -230])
men_bins = np.array([600, 623, 653, 650, 670, 578, 541, 360, 312, 170])

y = list(range(0, 100, 10))

layout = go.Layout(yaxis=go.layout.YAxis(title='Age'),
                   xaxis=go.layout.XAxis(
                       range=[-1200, 1200],
                       tickvals=[-1000, -700, -300, 0, 300, 700, 1000],
                       ticktext=[1000, 700, 300, 0, 300, 700, 1000],
                       title='Number'),
                   barmode='overlay',
                   bargap=0.1)

data = [go.Bar(y=y,
               x=men_bins,
               orientation='h',
               name='Men',
               hoverinfo='x',
               marker=dict(color='black')
               ),
        go.Bar(y=y,
               x=women_bins,
               orientation='h',
               name='Women',
               text=-1 * women_bins.astype('int'),
               hoverinfo='text',
               marker=dict(color='black')
               )]

fig = go.Figure(dict(data=data, layout=layout))
fig


# In[3]:


fig = make_subplots(rows=1, cols=2, start_cell="bottom-left")


fig.add_trace(go.Bar(x=[-1, -1, -1], y=["0 ans", "1 ans", "2 ans"], orientation='h'),
              row=1, col=1)

fig.add_trace(go.Bar(x=[10, 20, 18], y=["0 ans", "1 ans", "2 ans"], orientation='h'),
              row=1, col=2)

fig.update_layout(
                   barmode='overlay',
                   bargap=0.1)

fig.update_xaxes(range=[-30, 0], tickvals=[-30, 0], ticktext=[30, 0], row=1, col=1)
fig.update_xaxes(range=[0, 30], row=1, col=2)

fig.show()


# In[72]:


df_drees = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-resultats-issus-des-appariements-entre-si-vic-si-dep-et-vac-si/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")
df_drees = df_drees.sort_values(by="date")


# In[81]:





# In[43]:


df_drees = df_drees[df_drees["vac_statut"]!="Ensemble"]
df_drees_ensemble = df_drees.groupby("date").sum().reset_index()

df_drees_non_vaccines = df_drees[df_drees["vac_statut"]=="Non-vaccinés"]
df_drees_non_vaccines["effectif J-7"] = df_drees_non_vaccines["effectif J-7"].rolling(window=7).mean()

df_drees_completement_vaccines = df_drees[df_drees["vac_statut"].isin(["Vaccination complète",])].groupby("date").sum().reset_index()
df_drees_completement_vaccines["effectif J-7"] = df_drees_completement_vaccines["effectif J-7"].rolling(window=7).mean()

df_drees_partiellement_vaccines = df_drees[df_drees["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
df_drees_partiellement_vaccines["effectif J-7"] = df_drees_partiellement_vaccines["effectif J-7"].rolling(window=7).mean()


# In[75]:


x=["<b>Population générale</b>", "<b>Hospitalisés</b>"]

fig = go.Figure()
fig.add_trace(go.Funnel(
    name = 'Non vaccinés',
    orientation = "v",
    x = x,
    marker=dict(color="#e76f41"),
    text=["45 %", "84 %"],
    textinfo="text",
    y = [45, 82],
))

fig.add_trace(go.Funnel(
    name = 'Partiellement vaccinés',
    orientation = "v",
    x = x,
    y = [20, 10],
    marker=dict(color="#e9c46a"),
    text=["20 %", "9 %"],
    textinfo="text",
    textposition = "inside",
))

fig.add_trace(go.Funnel(
    name = 'Totalement vaccinés',
    orientation = "v",
    x = x,
    y = [35, 7],
    marker=dict(color="#2a9d8f"),
    text=["35 %", "7 %"],
    textinfo="text"
    ))
fig.update_layout(
    title="<b>État vaccinal des personnes en soins critiques</b><br><span style='font-size: 10px;'>Données DREES 20 juillet 2021 - Guillaume Rozier</span>",
    font=dict(size=10)
)
fig.show()


# In[76]:


x=["<b>Population générale</b>", "<b>Hospitalisés</b>"]

fig = go.Figure()
fig.add_trace(go.Funnel(
    name = 'Non vaccinés',
    orientation = "v",
    x = x,
    marker=dict(color="#e76f41"),
    text=["45 %", "75 %"],
    textinfo="text",
    y = [45, 82],
))

fig.add_trace(go.Funnel(
    name = 'Partiellement vaccinés',
    orientation = "v",
    x = x,
    y = [20, 10],
    marker=dict(color="#e9c46a"),
    text=["20 %", "13 %"],
    textinfo="text",
    textposition = "inside",
))

fig.add_trace(go.Funnel(
    name = 'Totalement vaccinés',
    orientation = "v",
    x = x,
    y = [35, 7],
    marker=dict(color="#2a9d8f"),
    text=["35 %", "12 %"],
    textinfo="text"
    ))
fig.update_layout(
    title="<b>État vaccinal des personnes décédées</b><br><span style='font-size: 10px;'>Données DREES 20 juillet 2021 - Guillaume Rozier</span>",
    font=dict(size=10)
)
fig.show()


# In[147]:


x=["<b>Population générale</b>", "<b>Hospitalisés</b>"]

fig = go.Figure()
fig.add_trace(go.Funnel(
    name = 'Non vaccinés',
    orientation = "v",
    x = x,
    marker=dict(color="#e76f41"),
    text=["62 %", "92 %"],
    textinfo="text",
    y = [62, 92],
))

fig.add_trace(go.Funnel(
    name = 'Partiellement vaccinés',
    orientation = "v",
    x = x,
    y = [27, 6],
    marker=dict(color="#e9c46a"),
    text=["27 %", "6 %"],
    textinfo="text",
    textposition = "inside",
))

fig.add_trace(go.Funnel(
    name = 'Totalement vaccinés',
    orientation = "v",
    x = x,
    y = [10, 2],
    marker=dict(color="#2a9d8f"),
    text=["10 %", "2 %"],
    textinfo="text"
    ))
fig.update_layout(
    title="<b>État vaccinal des personnes hospitalisées [20-30 ans]</b><br><span style='font-size: 10px;'>Données DREES 31 mai - 11 juillet 2021 - Guillaume Rozier</span>",
    font=dict(size=10)
)
fig.show()


# In[141]:


x=["Non vaccinés", "Partiellement vaccinés", "Totalement vaccinés"]

fig = go.Figure()

pop_non_vaccinee = 67000000 * 0.45 / 1000000
pop_partiellement_vaccinee = 67000000 * 0.2 / 1000000
pop_totalement_vaccinee = 67000000 * 0.35 / 1000000

y=[502/pop_non_vaccinee, 86/pop_partiellement_vaccinee, 77/pop_totalement_vaccinee]
fig.add_trace(go.Bar(
    name = 'Décédés',
    orientation = "v",
    x = x,
    y = y,
    marker=dict(color="#0b032d"),
    text=np.array(y).round(),
    textposition='auto',
    ))
y=[1047/pop_non_vaccinee, 108/pop_partiellement_vaccinee, 83/pop_totalement_vaccinee]
fig.add_trace(go.Bar(
    name = 'Admis en réanimation',
    orientation = "v",
    x = x,
    y = y,
    marker=dict(color="#843b62"),
    text=np.array(y).round(),
    textposition='auto',
))

y=[3968/pop_non_vaccinee, 492/pop_partiellement_vaccinee, 364/pop_totalement_vaccinee]
fig.add_trace(go.Bar(
    name = 'Admis hôpital',
    orientation = "v",
    x = x,
    marker=dict(color="#f67e7d"),
    y = y,
    text=np.array(y).round(),
    textposition='auto',
))

fig.update_layout(
    barmode="stack",
    title="<b>Nombre de formes graves pour 1 Mio hab. de chaque catégorie</b><br><span style='font-size: 10px;'>Données DREES 20 juillet 2021 - Guillaume Rozier</span>",
    titlefont=dict(size=18)
)

fig.add_annotation(x="Non vaccinés", y=132,
            text="Pour 1 Mio d'habitants <b>non vaccinés</b>,<br><b>132</b> ont été hospitalisés<br>(31 mai - 11 juillet)",
            showarrow=True,
            ax=200,
            arrowhead=1)


fig.show()


# In[6]:


fig = go.Figure()

total_i, total_j = 100, 100
total = total_i*total_j
total_hosp = 10
total_rea = 5
total_dc = 1

for i in range(1, total_i+1):
    for j in range(1, total_i+1):
        if (i*j) >= (total - total_dc):
            fig.add_trace(
                go.Scatter(x=[0+i, 0+i, 1+i, 1+i], y=[0+j, 1+j, 1+j, 0+j], fill="toself", fillcolor="black", line_width=0,  showlegend=False, mode="lines")
            )
        elif (i*j) >= (total - total_rea):
            fig.add_trace(
                go.Scatter(x=[0+i, 0+i, 1+i, 1+i], y=[0+j, 1+j, 1+j, 0+j], fill="toself", fillcolor="red", line_width=0,  showlegend=False, mode="lines")
            )
        elif (i*j) >= (total - total_hosp):
            fig.add_trace(
                go.Scatter(x=[0+i, 0+i, 1+i, 1+i], y=[0+j, 1+j, 1+j, 0+j], fill="toself", fillcolor="orange", line_width=0,  showlegend=False, mode="lines")
            )
        else:
            fig.add_trace(
                go.Scatter(x=[0+i, 0+i, 1+i, 1+i], y=[0+j, 1+j, 1+j, 0+j], fill="toself", fillcolor="blue", line_width=0.2,  line_color="white", showlegend=False, mode="lines", )
            )     

fig.update_xaxes(range=[0, 100])
fig.update_yaxes(range=[0, 100])
fig.write_image(PATH + "images/charts/france/{}.jpeg".format("carres_cas_vaccination"), scale=2, width=900, height=900)


# In[3]:


fig

