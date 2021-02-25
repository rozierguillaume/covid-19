#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
PATH = '../../'


# In[7]:



df = pd.read_csv(PATH+'data/france/synthese-fra.csv')
df['deces'] = df['total_deces_hopital'] + df['total_deces_ehpad']
df['deces_nouveaux'] = df['deces'].diff()


# In[10]:


df_epci = pd.read_csv(PATH+"data/france/sg-epci-opendata.csv")


# In[21]:


df_epci[df_epci.epci2020 == 200030658]


# In[ ]:




