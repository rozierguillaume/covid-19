#!/usr/bin/env python
# coding: utf-8

# In[99]:


"""
LICENSE MIT
2021
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


# In[100]:


import pandas as pd
import json
import france_data_management as data
import math

show_charts = False
PATH_STATS = "../../data/france/stats/"


# In[101]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[102]:


df_incid_fra_clage = data.import_data_tests_sexe()
df_incid_fra = df_incid_fra_clage[df_incid_fra_clage["cl_age90"]==0]
df_france = df.groupby(["jour"]).sum().reset_index()
df_incid = df_incid[df_incid.cl_age90 == 0]

df_sursaud_france = df_sursaud.groupby(["date_de_passage"]).sum().reset_index()
df_sursaud_regions = df_sursaud.groupby(["date_de_passage", "regionName"]).sum().reset_index()


# In[103]:


departements = list(dict.fromkeys(list(df_incid['dep'].values))) 
regions = list(dict.fromkeys(list(df_incid['regionName'].dropna().values))) 

df_regions = df.groupby(["jour", "regionName"]).sum().reset_index()
df_incid_regions = df_incid.groupby(["jour", "regionName"]).sum().reset_index()


# In[104]:


def generate_data(data_incid, data_hosp, data_sursaud):## Incidence
    dict_data = {}

    taux_incidence = data_incid["P"].rolling(window=7).sum().fillna(0) * 100000 / data_incid["pop"].values[0]
    dict_data["incidence"] = {"jour": list(data_incid.jour), "valeur": list(round(taux_incidence,2))}
    
    taux_positivite = (data_incid["P"].rolling(window=7).sum() * 100 / data_incid["T"].rolling(window=7).sum()).fillna(0)
    dict_data["taux_positivite"] = {"jour": list(data_incid.jour), "valeur": list(round(taux_positivite,2))}

    cas = data_incid["P"].rolling(window=7).mean().fillna(0)
    dict_data["cas"] = {"jour": list(data_incid.jour), "valeur": list(round(cas,2))}
    
    tests = data_incid["T"].rolling(window=7).mean().fillna(0)
    dict_data["tests"] = {"jour": list(data_incid.jour), "valeur": list(round(tests,2))}

    hospitalisations = data_hosp.hosp.fillna(0)
    dict_data["hospitalisations"] = {"jour": list(data_hosp.jour), "valeur": list(hospitalisations)}

    reanimations = data_hosp.rea.fillna(0)
    dict_data["reanimations"] = {"jour": list(data_hosp.jour), "valeur": list(reanimations)}
    
    nbre_acte_corona = data_sursaud.nbre_acte_corona.rolling(window=7).mean().fillna(0)
    dict_data["nbre_acte_corona"] = {"jour": list(data_sursaud.date_de_passage), "valeur": list(round(nbre_acte_corona, 2))}
    
    nbre_pass_corona = data_sursaud.nbre_pass_corona.rolling(window=7).mean().fillna(0)
    dict_data["nbre_pass_corona"] = {"jour": list(data_sursaud.date_de_passage), "valeur": list(round(nbre_pass_corona, 2))}

    deces_hospitaliers = data_hosp.dc.diff().rolling(window=7).mean().fillna(0)
    dict_data["deces_hospitaliers"] = {"jour": list(data_hosp.jour), "valeur": list(round(deces_hospitaliers,2))}
    
    population = data_incid["pop"].values[0]
    dict_data["population"] = population
    
    return dict_data
 


# In[105]:


def export_data(data):
    with open(PATH_STATS + 'dataexplorer.json', 'w') as outfile:
        json.dump(data, outfile)


# In[106]:


def dataexplorer():
    dict_data = {}
    dict_data["regions"] = sorted(regions)
    dict_data["departements"] = departements
    dict_data["france"] = generate_data(df_incid_fra, df_france, df_sursaud_france)
    
    noms_departements={}
    
    for reg in regions:
        dict_data[reg] = generate_data(df_incid_regions[df_incid_regions.regionName==reg],                                        df_regions[df_regions.regionName==reg],                                       df_sursaud_regions[df_sursaud_regions.regionName==reg])
    
    for dep in departements:
        df_incid_dep = df_incid[df_incid.dep==dep]
        dict_data[dep] = generate_data(df_incid_dep, df[df.dep==dep], df_sursaud[df_sursaud.dep==dep])
        
        noms_departements[dep] = df_incid_dep["departmentName"].values[0]
    dict_data["departements_noms"] = noms_departements
    
    export_data(dict_data)


# In[107]:


dataexplorer()

