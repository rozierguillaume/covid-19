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

The charts are exported to 'charts/images/france'.
Data is download to/imported from 'data/france'.
Requirements: please see the imports below (use pip3 to install them).

"""


# In[89]:


import pandas as pd
import france_data_management as data
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# In[71]:


df_hosp = data.import_data_hosp_clage().groupby(["jour", "cl_age90"]).sum().reset_index()
df_hosp = df_hosp[df_hosp.cl_age90 == 79].reset_index()

df_tests_viro = data.import_data_tests_sexe()
df_tests_viro = df_tests_viro[df_tests_viro.cl_age90 == 79].reset_index()


# In[107]:


df = df_tests_viro.merge(df_hosp, left_on="jour", right_on="jour")

df = df.reset_index()
df["hosp_cas_ratio"] = (df.hosp / df.P.rolling(window=7).mean())


# In[108]:


fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=df.hosp_cas_ratio))


# In[101]:


df


# In[109]:


fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(
    x=df.jour,
    y=df.hosp,
    name="Hosp 70-79",),
    secondary_y=False)
fig.add_trace(go.Scatter(
    x=df.jour,
    y=df.P.rolling(window=7).mean(),
    name="cas positifs 70-79",),
    secondary_y=True)

