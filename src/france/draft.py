#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[4]:


PATH = '../../'
df = pd.read_csv(PATH+'data/france/synthese-fra.csv')
df['deces'] = df['total_deces_hopital'] + df['total_deces_ehpad']
df['deces_nouveaux'] = df['deces'].diff()


# In[5]:


df

