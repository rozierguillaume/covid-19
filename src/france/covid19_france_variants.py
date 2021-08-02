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
PATH = "../../"
import france_data_management as data
import plotly.graph_objects as go
import locale
from datetime import datetime
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
now = datetime.now()


# In[24]:


data.download_data()
df_tests =data.import_data_tests_sexe()
df_tests = df_tests[df_tests.cl_age90 == 0]
df_tests["P_rolling"] = df_tests["P"].rolling(window=7).mean()


# In[25]:


data.download_data_variants()
df_variants = data.import_data_variants()


# In[26]:


df_variants["jour"] = df_variants.semaine.apply(lambda x: x[11:]) 


# In[27]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=df_variants.tx_A1,
        name="Mutation E484K (" + str(df_variants.tx_A1.values[-1]).replace(".", ",") + " %)<br>dont Beta",
        showlegend=True,
    )
)

fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=df_variants.tx_B1,
        name="Mutation E484Q (" + str(df_variants.tx_B1.values[-1]).replace(".", ",") + " %)<br>dont Kappa",
    )
)

fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=df_variants.tx_C1,
        name="Mutation L452R (" + str(df_variants.tx_C1.values[-1]).replace(".", ",") + " %)<br>dont Delta",
        showlegend=True,
    )
)
y=100 - df_variants.tx_A1 - df_variants.tx_B1 - df_variants.tx_C1
fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=y,
        name="Autres (" + str(round(y.values[-1], 1)).replace(".", ",") + " %)",
        showlegend=True,
    )
)

fig.update_yaxes(ticksuffix="%")

fig.update_layout(
     title={
        'text': "Proportion de variants dans les tests positifs (en %)",
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
         'font': {'size': 30}
    },
    annotations = [
                    dict(
                        x=0.5,
                        y=1.1,
                        xref='paper',
                        yref='paper',
                        text='Mis à jour le {}. Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.'.format(now.strftime('%d %B')),
                        showarrow = False
                    )]
)
fig.write_image(PATH+"images/charts/france/{}.jpeg".format("variants_pourcent"), scale=2, width=1000, height=600)


# In[28]:


fig = go.Figure()
n_days = len(df_variants)

pourcent=100 - df_variants.tx_C1.values
y=df_tests["P_rolling"].values[-n_days:] * pourcent/100
fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=y,
        name="<b>Autres souches</b><br>" + str(nbWithSpaces(y[-1])).replace(".", ",") + " (" + str(round(pourcent[-1], 1)).replace(".", ",") + " %) ",
        stackgroup='one'
    )
)

pourcent=df_variants.tx_C1.values
y=df_tests["P_rolling"].values[-n_days:] * pourcent/100
fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=y,
        name="Mutation L452R, dont <b>Delta </b><br>" + str(nbWithSpaces(y[-1])).replace(".", ",") + " (" + str(pourcent[-1]).replace(".", ",") + " %) ",
        stackgroup='one'
    )
)


fig.update_yaxes(ticksuffix="")

fig.update_layout(
     title={
        'text': "Nombre de variants dans les cas détectés",
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
         'font': {'size': 30}
    },
    annotations = [
                    dict(
                        x=0.5,
                        y=1.1,
                        xref='paper',
                        yref='paper',
                        text='Mis à jour : {}. Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.'.format(now.strftime('%d %B')),
                        showarrow = False
                    )]
)
fig.write_image(PATH+"images/charts/france/{}.jpeg".format("variants_nombre"), scale=2, width=1000, height=600)

