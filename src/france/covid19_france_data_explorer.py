#!/usr/bin/env python
# coding: utf-8

# In[97]:


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


# In[98]:


import pandas as pd
import json
import france_data_management as data
import math

show_charts = False
PATH_STATS = "../../data/france/stats/"


# In[99]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[100]:


df_tests_viros_enrichi = data.import_data_tests_viros()
df_tests_viros_enrichi = df_tests_viros_enrichi.drop("regionName_y", axis=1).rename({"regionName_x": "regionName"}, axis=1)


# In[101]:


df_incid_clage = df_incid.copy()

df_incid_fra_clage = data.import_data_tests_sexe()
df_incid_fra = df_incid_fra_clage[df_incid_fra_clage["cl_age90"]==0]
df_france = df.groupby(["jour"]).sum().reset_index()
df_incid = df_incid[df_incid.cl_age90 == 0]

df_sursaud_france = df_sursaud.groupby(["date_de_passage"]).sum().reset_index()
df_sursaud_regions = df_sursaud.groupby(["date_de_passage", "regionName"]).sum().reset_index()

df_new_france = df_new.groupby(["jour"]).sum().reset_index()
df_new_regions = df_new.groupby(["jour", "regionName"]).sum().reset_index()


# In[102]:


df_incid_clage_regions = df_incid_clage.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()


# In[103]:


df_tests_viros_regions = df_tests_viros_enrichi.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()
df_tests_viros_france = df_tests_viros_enrichi.groupby(["jour", "cl_age90"]).sum().reset_index()


# In[104]:


df_hosp_clage = data.import_data_hosp_clage()
df_hosp_clage_france = df_hosp_clage.groupby(["jour", "cl_age90"]).sum().reset_index()
df_hosp_clage_regions = df_hosp_clage.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()


# In[105]:


departements = list(dict.fromkeys(list(df_incid['dep'].values))) 
regions = list(dict.fromkeys(list(df_incid['regionName'].dropna().values))) 
clage_list = list(dict.fromkeys(list(df_incid_fra_clage['cl_age90'].dropna().values))) 

df_regions = df.groupby(["jour", "regionName"]).sum().reset_index()
df_incid_regions = df_incid.groupby(["jour", "regionName"]).sum().reset_index()


zone_a = ["zone_a", "01", "03", "07", "15", "16", "17", "19", "21", "23", "24", "25", "26", "33", "38", "39", "40", "42", "43", "47", "58", "63", "64", "69", "70", "71", "73", "74", "79", "86", "90"]
zone_b = ["zone_b", "02", "04", "05", "06", "08", "10", "13", "14", "18", "22", "27", "28", "29", "35", "36", "37", "41", "44", "45", "49", "50", "51", "52", "53", "54", "55", "56", "57", "59", "60", "61", "62", "67", "68", "72", "76", "80", "83", "84", "85", "88"]
zone_c = ["zone_c", "09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "75", "77", "78", "81", "82", "91", "92", "93", "94", "95"]


# In[106]:


def generate_data(data_incid, data_hosp, data_sursaud, data_new, export_jour=False):## Incidence
        
    dict_data = {}
    
    if export_jour:
        dict_data["jour_incid"] = list(data_incid.jour)
        dict_data["jour_hosp"] = list(data_hosp.jour)
        dict_data["jour_new"] = list(data_new.jour)
        dict_data["jour_sursaud"] = list(data_sursaud.date_de_passage)
    
    taux_incidence = data_incid["P"].rolling(window=7).sum().fillna(0) * 100000 / data_incid["pop"].values[0]
    dict_data["incidence"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_incidence,2))}
    
    taux_positivite = (data_incid["P"].rolling(window=7).sum() * 100 / data_incid["T"].rolling(window=7).sum()).fillna(0)
    dict_data["taux_positivite"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_positivite,2))}

    cas = data_incid["P"].rolling(window=7).mean().fillna(0)
    dict_data["cas"] = {"jour_nom": "jour_incid", "valeur": list(round(cas,2))}
    
    tests = data_incid["T"].rolling(window=7).mean().fillna(0)
    dict_data["tests"] = {"jour_nom": "jour_incid", "valeur": list(round(tests,2))}

    hospitalisations = data_hosp.hosp.fillna(0)
    dict_data["hospitalisations"] = {"jour_nom": "jour_hosp", "valeur": list(hospitalisations)}

    reanimations = data_hosp.rea.fillna(0)
    dict_data["reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(reanimations)}
    
    incid_hospitalisations = data_new.incid_hosp.rolling(window=7).mean().fillna(0)
    dict_data["incid_hospitalisations"] = {"jour_nom": "jour_new", "valeur": list(round(incid_hospitalisations, 2))}
    
    incid_reanimations = data_new.incid_rea.rolling(window=7).mean().fillna(0)
    dict_data["incid_reanimations"] = {"jour_nom": "jour_new", "valeur": list(round(incid_reanimations,2))}
    
    nbre_acte_corona = data_sursaud.nbre_acte_corona.rolling(window=7).mean().fillna(0)
    dict_data["nbre_acte_corona"] = {"jour_nom": "jour_sursaud", "valeur": list(round(nbre_acte_corona, 2))}
    
    nbre_pass_corona = data_sursaud.nbre_pass_corona.rolling(window=7).mean().fillna(0)
    dict_data["nbre_pass_corona"] = {"jour_nom": "jour_sursaud", "valeur": list(round(nbre_pass_corona, 2))}

    deces_hospitaliers = data_hosp.dc.diff().rolling(window=7).mean().fillna(0)
    dict_data["deces_hospitaliers"] = {"jour_nom": "jour_hosp", "valeur": list(round(deces_hospitaliers,2))}
    
    population = data_incid["pop"].values[0]
    dict_data["population"] = population

    return dict_data
 


# In[107]:


def generate_data_age(data_incid, data_hosp, export_jour=False):## Incidence
    clage_tranches = [[0], [9, 19], [29, 39], [49, 59], [69, 79], [89, 90]]
    clage_noms = ["tous", "19", "39", "59", "79", "90"]
    clage_noms_disp = ["Tous âges", "0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "Plus de 80 ans"]
    
    dict_data = {}
    
    for (idx, clage) in enumerate(clage_tranches):
        clage_nom = clage_noms[idx]
        
        data_incid_clage = data_incid[data_incid.cl_age90.isin(clage)].groupby("jour").sum().reset_index()

        dict_data[clage_nom] = {}

        taux_incidence = data_incid_clage["P"].rolling(window=7).sum().fillna(0) * 100000 / data_incid_clage["pop"].values[0]
        dict_data[clage_nom]["incidence"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_incidence,2))}

        taux_positivite = (data_incid_clage["P"].rolling(window=7).sum() * 100 / data_incid_clage["T"].rolling(window=7).sum()).fillna(0)
        dict_data[clage_nom]["taux_positivite"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_positivite,2))}

        cas = data_incid_clage["P"].rolling(window=7).mean().fillna(0)
        dict_data[clage_nom]["cas"] = {"jour_nom": "jour_incid", "valeur": list(round(cas,2))}

        tests = data_incid_clage["T"].rolling(window=7).mean().fillna(0)
        dict_data[clage_nom]["tests"] = {"jour_nom": "jour_incid", "valeur": list(round(tests,2))}
        
        population = data_incid_clage["pop"].values[0]
        dict_data[clage_nom]["population"] = population
        
        if (len(data_hosp)):
            
            data_hosp_clage = data_hosp[data_hosp.cl_age90.isin(clage)].groupby("jour").sum().reset_index()
            hospitalisations = data_hosp_clage.hosp.fillna(0)
            dict_data[clage_nom]["hospitalisations"] = {"jour_nom": "jour_hosp", "valeur": list(hospitalisations)}

            reanimations = data_hosp_clage.rea.fillna(0)
            dict_data[clage_nom]["reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(reanimations)}

            deces_hospitaliers = data_hosp_clage.dc.diff().rolling(window=7).mean().fillna(0)
            dict_data[clage_nom]["deces_hospitaliers"] = {"jour_nom": "jour_hosp", "valeur": list(round(deces_hospitaliers,2))}
        
    if export_jour:
            dict_data["jour_incid"] = list(data_incid.jour.unique())
            dict_data["jour_hosp"] = list(data_hosp.jour.unique())
            dict_data["tranches"] = clage_tranches
            dict_data["tranches_noms"] = clage_noms
            dict_data["tranches_noms_affichage"] = clage_noms_disp

    return dict_data
 


# In[108]:


def export_data(data, suffix=""):
    with open(PATH_STATS + 'dataexplorer{}.json'.format(suffix), 'w') as outfile:
        json.dump(data, outfile)


# In[109]:


def dataexplorer():
    dict_data = {}
    
    dict_data["regions"] = sorted(regions)
    dict_data["departements"] = departements
    dict_data["france"] = generate_data(df_incid_fra, df_france, df_sursaud_france, df_new_france, export_jour=True)
    
    noms_departements={}
    
    for reg in regions:
        
        dict_data[reg] = generate_data(df_incid_regions[df_incid_regions.regionName==reg],                                        df_regions[df_regions.regionName==reg],                                       df_sursaud_regions[df_sursaud_regions.regionName==reg],
                                       df_new_regions[df_new_regions.regionName==reg])
    
    for dep in departements:
        df_incid_dep = df_incid[df_incid.dep==dep]
        dict_data[dep] = generate_data(df_incid_dep, df[df.dep==dep], df_sursaud[df_sursaud.dep==dep], df_new[df_new.dep==dep])
        
        noms_departements[dep] = df_incid_dep["departmentName"].values[0]
    dict_data["departements_noms"] = noms_departements
    
    for zone in [zone_a, zone_b, zone_c]:
        df_incid_zone = df_incid[df_incid.dep.isin(zone)].groupby("jour").sum().reset_index()
        df_zone = df[df.dep.isin(zone)].groupby("jour").sum().reset_index()
        df_sursaud_zone = df_sursaud[df_sursaud.dep.isin(zone)].groupby("date_de_passage").sum().reset_index()
        df_new_zone = df_new[df_new.dep.isin(zone)].groupby("jour").sum().reset_index()
        dict_data[zone[0]] = generate_data(df_incid_zone, df_zone, df_sursaud_zone, df_new_zone)
        
    dict_data["zones_vacances"] = ["zone_a", "zone_b", "zone_c"]
    
    export_data(dict_data, suffix="_compr")


# In[ ]:





# In[110]:


import math
def dataexplorer_age():
    dict_data = {}
    regions_tests_viros = list(dict.fromkeys(list(df_tests_viros_enrichi['regionName'].dropna().values))) 
    departements_tests_viros = list(dict.fromkeys(list(df_tests_viros_enrichi['dep'].dropna().values))) 
    dict_data["regions"] = sorted(regions_tests_viros)
    dict_data["departements"] = sorted(departements_tests_viros)
    
    dict_data["france"] = generate_data_age(df_tests_viros_france, df_hosp_clage_france, export_jour=True)
    
    for reg in regions_tests_viros:
        dict_data[reg] = generate_data_age(df_tests_viros_regions[df_tests_viros_regions.regionName == reg],                                           df_hosp_clage_regions[df_hosp_clage_regions.regionName == reg])
    noms_departements={}
    for dep in departements_tests_viros:
        df_tests_viros_enrichi_temp = df_tests_viros_enrichi[df_tests_viros_enrichi.dep == dep]
        dict_data[dep] = generate_data_age(df_tests_viros_enrichi_temp,                                           pd.DataFrame())
        
        nom_dep = df_tests_viros_enrichi_temp["departmentName"].values[0]
        
        if(type(nom_dep) is float): #Pas de nom, nom_dep == NaN
            print(dep)
            nom_dep = "--"
        
        noms_departements[dep] = nom_dep
        
    dict_data["departements_noms"] = noms_departements
    
    export_data(dict_data, suffix="_compr_age")
    return dict_data


# In[111]:


dataexplorer()


# In[112]:


dict_data = dataexplorer_age()

