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
import plotly.express as px
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


COULEUR_NON_VACCINES = "#C65102"
COULEUR_COMPLETEMENT_VACCINES = "#00308F"


# In[4]:


df_drees = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-resultats-issus-des-appariements-entre-si-vic-si-dep-et-vac-si/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")
df_drees = df_drees.sort_values(by="date")
df_drees = df_drees[df_drees["vac_statut"]!="Ensemble"]


# In[5]:


df_drees_non_vaccines = df_drees[df_drees["vac_statut"]=="Non-vaccinés"]
df_drees_non_vaccines["effectif J-7"] = df_drees_non_vaccines["effectif J-7"].rolling(window=7).mean()

df_drees_completement_vaccines = df_drees[df_drees["vac_statut"].isin(["Vaccination complète",])].groupby("date").sum().reset_index()
df_drees_completement_vaccines["effectif J-7"] = df_drees_completement_vaccines["effectif J-7"].rolling(window=7).mean()

df_drees_partiellement_vaccines = df_drees[df_drees["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
df_drees_partiellement_vaccines["effectif J-7"] = df_drees_partiellement_vaccines["effectif J-7"].rolling(window=7).mean()

#df_drees_ensemble = df_drees[df_drees["vac_statut"]=="Ensemble"]
df_drees_ensemble = df_drees.groupby("date").sum().reset_index()


# In[6]:


locale.setlocale(locale.LC_TIME, 'fr_FR')
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)
fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
    title={
                    'text': "<b>Cas positifs</b> Covid symptomatiques",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {} - Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)
y=df_drees_non_vaccines["nb_PCR+_sympt"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif J-7"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " cas symptomatiques<br>non vaccinés</b><br>pour 10 Mio non vaccinés",
    font=dict(color=COULEUR_NON_VACCINES),
    showarrow=False,
    yshift=30
)
y=df_drees_completement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif J-7"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " cas symptomatiques<br>vaccinés</b><br>pour 10 Mio vaccinés",
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    yshift=0,
    xshift=60
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Cas pos. sympt. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m")
name_fig = "pcr_plus_sympt_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[7]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["HC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["HC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["HC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["HC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["HC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["HC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)


"""fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["HC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["n_dose1"].rolling(window=30).sum() * 1000000,
        name="Partiellement vaccinés",
        line_color="#1E90FF",
        line_width=3
    )
)"""

fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
    title={
                        'text': "<b>Admissions à l'hôpital</b> pour Covid",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)
y=df_drees_non_vaccines["HC"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif J-7"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " admissions<br>non vaccinées</b><br>pour 10 Mio de non vaccinés",
    font=dict(color=COULEUR_NON_VACCINES),
    showarrow=False,
    yshift=30
)

y=df_drees_completement_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif J-7"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " admissions<br>vaccinées</b><br>pour 10 Mio de vaccinés",
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    yshift=0,
    xshift=60,
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations pour suspicion Covid19.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m")
name_fig = "hc_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[8]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["SC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["SC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        mode="markers",
        marker_size=10,
        showlegend=False
    )
)
fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["SC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["SC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        mode="markers",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["SC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["SC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
    title={
                    'text': "<b>Admissions</b> <b>en soins critiques</b> Covid",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {} - Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)
y=df_drees_non_vaccines["SC"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif J-7"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " admissions<br>non vaccinées</b><br>pour 10 Mio non vaccinés",
    font=dict(color=COULEUR_NON_VACCINES),
    showarrow=False,
    yshift=30
)
y=df_drees_completement_vaccines["SC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif J-7"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " admissions<br>vaccinées</b><br>pour 10 Mio vaccinés",
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    yshift=0,
    xshift=60
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m")
name_fig = "sc_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[9]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["DC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000,
        name="Non vaccinés",
        line_color=COULEUR_NON_VACCINES,
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["DC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color=COULEUR_NON_VACCINES,
        marker_size=10,
        showlegend=False
    )
)
fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["DC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["DC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["DC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["DC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
    title={
                        'text': "<b>Décès</b> Covid à l'hôpital",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)
y=df_drees_non_vaccines["DC"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif J-7"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " décès<br>non vaccinés</b><br>pour 10 Mio non vaccinés",
    font=dict(color=COULEUR_NON_VACCINES),
    showarrow=False,
    yshift=30
)
y=df_drees_completement_vaccines["DC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif J-7"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " décès<br>vaccinés</b><br>pour 10 Mio vaccinés",
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    yshift=30
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Décès à l'hôpital pour suspicion Covid19.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Décès hosp. quot. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m")
name_fig = "dc_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[10]:





# In[11]:


positif_vax = round((df_drees_completement_vaccines["nb_PCR+_sympt"].values[-1]/df_drees_ensemble["nb_PCR+_sympt"].values[-1])*100)
pop_vax = round((df_drees_completement_vaccines["effectif J-7"].values[-1]/df_drees_ensemble["effectif J-7"].values[-1])*100)

stages = ["<b>Population générale</b>", "<b>Cas positifs symptomatiques</b>"]
df_mtl = pd.DataFrame(dict(number=[pop_vax, positif_vax], stage=stages))
df_mtl['État vaccinal'] = 'Complètement vacciné (%)'

df_toronto = pd.DataFrame(dict(number=[100-pop_vax, 100-positif_vax], stage=stages))
df_toronto['État vaccinal'] = 'Non vacciné (%)'

df = pd.concat([df_mtl, df_toronto], axis=0)
fig = px.funnel(df, y='number', x='stage', color='État vaccinal', height=700, width=700, orientation="v", title="<b>Statut vaccinal des cas symptomatiques</b><br><span style='font-size: 10px;'>Données DREES au 01/08/21 - Guillaume Rozier</span>")
fig.show()


# In[12]:


taux_positif_vax = round((df_drees_completement_vaccines["nb_PCR+_sympt"].values[-1]/df_drees_completement_vaccines["nb_PCR_sympt"].values[-1])*100)
taux_positif_non_vax = round((df_drees_non_vaccines["nb_PCR+_sympt"].values[-1]/df_drees_non_vaccines["nb_PCR_sympt"].values[-1])*100)

stages = ["<b><br><span style='font-size:15px;'>Non vacciné</b></span>", "<b><br><span style='font-size:15px;'>Vacciné</span></b>"]
df_mtl = pd.DataFrame(dict(number=[taux_positif_non_vax, taux_positif_vax], stage=stages))
df_mtl['Résultat'] = '<b>Positif</b> (%)'
df_toronto = pd.DataFrame(dict(number=[100-taux_positif_non_vax, 100-taux_positif_vax], stage=stages))
df_toronto['Résultat'] = '<b>Négatif</b> (%)'
df = pd.concat([df_toronto, df_mtl], axis=0)
fig = px.funnel(df, y='number', x='stage', color='Résultat', height=700, width=600, orientation="v", title="<b>Résultat des tests des personnes symptomatiques</b><br><span style='font-size: 10px;'>Données DREES 01/08/21 - Guillaume Rozier</span>")
fig.show()


# In[22]:


#df = pd.concat([df_completement_vaccine, df_partiellement_vaccine, df_non_vaccine], axis=0)

hosp_vax = int(round((df_drees_completement_vaccines["HC"].values[-1]/df_drees_ensemble["HC"].values[-1])*100))
hosp_partiellement_vax = int(round((df_drees_partiellement_vaccines["HC"].values[-1]/df_drees_ensemble["HC"].values[-1])*100))

pop_vax = int(round((df_drees_completement_vaccines["effectif J-7"].values[-1]/df_drees_ensemble["effectif J-7"].values[-1])*100))
pop_partiellement_vax = int(round((df_drees_partiellement_vaccines["effectif J-7"].values[-1]/df_drees_ensemble["effectif J-7"].values[-1])*100))

x=["<b>Population générale</b>", "<b>Hospitalisés</b>"]
y1 = [100-pop_vax-pop_partiellement_vax, 100-hosp_partiellement_vax-hosp_vax]
fig = go.Figure()
fig.add_trace(go.Funnel(
    name = 'Non vaccinés',
    orientation = "v",
    x = x,
    marker=dict(color="#e76f41"),
    text=[str(val) + " %" for val in y1],
    textinfo="text",
    y = y1,
))

y2 = [pop_partiellement_vax, hosp_partiellement_vax]
fig.add_trace(go.Funnel(
    name = 'Partiellement vaccinés',
    orientation = "v",
    x = x,
    y = y2,
    marker=dict(color="#e9c46a"),
    text=[str(val) + " %" for val in y2],
    textinfo="text",
    textposition = "inside",
))

y3 = [pop_vax, hosp_vax]
fig.add_trace(go.Funnel(
    name = 'Totalement vaccinés',
    orientation = "v",
    x = x,
    y = y3,
    marker=dict(color="#2a9d8f"),
    text=[str(val) + " %" for val in y3],
    textinfo="text"
    ))
fig.update_layout(
    title=f"<b>État vaccinal des personnes admises à l'hôpital</b><br><span style='font-size: 10px;'><b>Lecture :</b> {y3[0]}% des Français sont vaccinés, mais ils représentent {y3[1]}% des admissions à l'hôpital.<br>Données DREES {datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')} - @GuillaumeRozier</span>",
    font=dict(size=10)
)
name_fig = "popgen_hosp_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=600, height=600)

