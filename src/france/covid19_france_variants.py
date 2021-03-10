#!/usr/bin/env python
# coding: utf-8

# In[88]:


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


# In[89]:


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


# In[107]:


import pandas as pd
PATH = "../../"
import france_data_management as data
import plotly.graph_objects as go
import locale
from datetime import datetime
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
now = datetime.now()


# In[91]:


data.download_data()
df_tests =data.import_data_tests_sexe()
df_tests = df_tests[df_tests.cl_age90 == 0]
df_tests["P_rolling"] = df_tests["P"].rolling(window=7).mean()
df_tests


# In[92]:


data.download_data_variants()
df_variants = data.import_data_variants()
df_variants


# In[93]:


df_variants["jour"] = df_variants.semaine.apply(lambda x: x[11:]) 
df_variants = df_variants[df_variants.cl_age90==0]
df_variants


# In[94]:


df_variants.Nb_tests_PCR_TA_crible / (df_variants.Prc_tests_PCR_TA_crible/100)


# In[108]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=df_variants.Prc_susp_501Y_V1,
        name="% variant UK (" + str(df_variants.Prc_susp_501Y_V1.values[-1]).replace(".", ",") + " %)",
    )
)

fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=df_variants.Prc_susp_ABS,
        name="% souche classique (" + str(df_variants.Prc_susp_ABS.values[-1]).replace(".", ",") + " %)",
        showlegend=True,
    )
)

fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=df_variants.Prc_susp_IND,
        name="% variants indéterminés (" + str(df_variants.Prc_susp_IND.values[-1]).replace(".", ",") + " %)",
        showlegend=True,
    )
)

fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=df_variants.Prc_susp_501Y_V2_3,
        name="% variants SA + BZ (" + str(df_variants.Prc_susp_501Y_V2_3.values[-1]).replace(".", ",") + " %)",
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


# In[113]:


fig = go.Figure()
n_days = len(df_variants)

y=df_tests["P_rolling"].values[-n_days:] * df_variants.Prc_susp_501Y_V2_3.values/100
fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=y,
        name="<b>Variants SA + BZ </b><br>" + str(nbWithSpaces(y[-1])) + " (" + str(df_variants.Prc_susp_501Y_V2_3.values[-1]).replace(".", ",") + " %) ",
        showlegend=True,
        stackgroup='one'
    )
)

y=df_tests["P_rolling"].values[-n_days:] * df_variants.Prc_susp_IND.values/100
fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=y,
        name="<b>Variants indéterminés </b><br>" + str(nbWithSpaces(y[-1])) + " (" + str(df_variants.Prc_susp_IND.values[-1]).replace(".", ",") + " %) ",
        showlegend=True,
        stackgroup='one'
    )
)

y=df_tests["P_rolling"].values[-n_days:] * df_variants.Prc_susp_ABS.values/100
fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=y,
        name="<b>Souche classique </b><br>" + str(nbWithSpaces(y[-1])) + " (" + str(df_variants.Prc_susp_ABS.values[-1]).replace(".", ",") + " %) ",
        showlegend=True,
        stackgroup='one'
    )
)

y=df_tests["P_rolling"].values[-n_days:] * df_variants.Prc_susp_501Y_V1.values/100
fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=y,
        name="<b>Variant UK </b><br>" + str(nbWithSpaces(y[-1])).replace(".", ",") + " (" + str(df_variants.Prc_susp_501Y_V1.values[-1]).replace(".", ",") + " %) ",
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

