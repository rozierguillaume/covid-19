#!/usr/bin/env python
# coding: utf-8

# In[29]:


import math

T = 10
RH = 50

AH_num = 6.112 * math.exp(17.67 * T / (T+243.5)) * RH * 2.1674 
AH_den = 273.15 + T
AH = AH_num / AH_den

contenu_exp = (T-7.5)**2/196 + (RH-75)**2/625 + (AH-6)**2/2.89
IPTCC = 100 * math.exp(-0.5 * contenu_exp)

IPTCC


# In[9]:


math.exp(-0.5 * contenu_exp)

