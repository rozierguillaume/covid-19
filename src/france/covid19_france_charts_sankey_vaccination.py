#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np

import holoviews as hv
import plotly.graph_objects as go
import plotly.express as pex
hv.extension('bokeh')


# In[56]:



data = pd.DataFrame()
data["source"] = ["vacciné", "Non vacciné"]
data["destination"] = ["Positif vacciné", "Positif non vacciné"]
data["value"] = [6, ,94]
data


# In[57]:


hv.Sankey(data)


# In[89]:


import plotly.express as px
import pandas as pd
stages = ["<b>Population générale</b>", "<b>Cas positifs symptomatiques</b>"]
df_mtl = pd.DataFrame(dict(number=[32, 4], stage=stages))
df_mtl['État vaccinal'] = 'Complètement vacciné (%)'
df_toronto = pd.DataFrame(dict(number=[68, 96], stage=stages))
df_toronto['État vaccinal'] = 'Non vacciné (%)'
df = pd.concat([df_mtl, df_toronto], axis=0)
fig = px.funnel(df, y='number', x='stage', color='État vaccinal', height=700, width=700, orientation="v", title="<b>Efficacité vaccinale</b><br><span style='font-size: 10px;'>Données DREES - Guillaume Rozier</span>")
fig.show()


# In[118]:


import plotly.express as px
import pandas as pd
stages = ["<b><br><span style='font-size:15px;'>Non vacciné</b></span>", "<b><br><span style='font-size:15px;'>Vacciné</span></b>"]
df_mtl = pd.DataFrame(dict(number=[8.4, 1.8], stage=stages))
df_mtl['Résultat'] = '<b>Positif</b> (%)'
df_toronto = pd.DataFrame(dict(number=[91.6, 98.2], stage=stages))
df_toronto['Résultat'] = '<b>Négatif</b> (%)'
df = pd.concat([df_toronto, df_mtl], axis=0)
fig = px.funnel(df, y='number', x='stage', color='Résultat', height=700, width=600, orientation="v", title="<b>Résultat des tests des personnes symptomatiques</b><br><span style='font-size: 10px;'>Données DREES - Guillaume Rozier</span>")
fig.show()

