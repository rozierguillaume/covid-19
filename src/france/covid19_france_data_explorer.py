#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


import pandas as pd
import json
import france_data_management as data
import math

show_charts = False
PATH_STATS = "../../data/france/stats/"
PATH = "../../"


# In[3]:


df_regions_meta = pd.read_csv(PATH+"data/france/population_grandes_regions.csv")


# In[4]:


data.download_data_obepine()
df_obepine = data.import_data_obepine()
df_obepine_france = df_obepine.groupby("Date").mean().reset_index()


# In[5]:


data.download_data()
df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[6]:


data.download_data_vue_ensemble()
df_vue_ensemble = data.import_data_vue_ensemble()


# In[7]:


#df_vacsi_a = data.import_data_vacsi_a_fra()
#df_vacsi_a_reg = data.import_data_vacsi_a_reg()
#df_vacsi_a_dep = data.import_data_vacsi_a_dep()

df_vacsi = data.import_data_vacsi_fra() #df_vacsi_a.groupby("jour").sum().reset_index()
df_vacsi_reg = data.import_data_vacsi_reg() #df_vacsi_a_reg.groupby(["jour", "reg"]).sum().reset_index()
df_vacsi_reg = df_vacsi_reg.merge(df_regions_meta, left_on="reg", right_on="code").rename({"n_tot_dose1": "n_cum_dose1"}, axis=1)

df_vacsi_dep = data.import_data_vacsi_dep().rename({"n_tot_dose1": "n_cum_dose1"}, axis=1)
#df_vacsi_a_dep.groupby(["jour", "dep"]).sum().reset_index().rename({"n_tot_dose1": "n_cum_dose1"}, axis=1)


# In[8]:


df_metro = data.import_data_metropoles()
df_metro["jour"] = df_metro["semaine_glissante"].map(lambda x: x[11:])

df_metro_65 = df_metro[df_metro["clage_65"] == 65]
df_metro_0 = df_metro[df_metro["clage_65"] == 0]
metropoles = list(dict.fromkeys(list(df_metro['Metropole'].dropna().values))) 


# In[9]:


df_tests_viros_enrichi = data.import_data_tests_viros()
df_tests_viros_enrichi = df_tests_viros_enrichi.drop("regionName_y", axis=1).rename({"regionName_x": "regionName"}, axis=1)


# In[10]:


df_incid_clage = df_incid.copy()

df_incid_fra_clage = data.import_data_tests_sexe()
df_incid_fra = df_incid_fra_clage[df_incid_fra_clage["cl_age90"]==0]
df_france = df.groupby(["jour"]).sum().reset_index()
df_incid = df_incid[df_incid.cl_age90 == 0]

df_sursaud_france = df_sursaud.groupby(["date_de_passage"]).sum().reset_index()
df_sursaud_regions = df_sursaud.groupby(["date_de_passage", "regionName"]).sum().reset_index()

df_new_france = df_new.groupby(["jour"]).sum().reset_index()
df_new_regions = df_new.groupby(["jour", "regionName"]).sum().reset_index()


# In[11]:


df_incid_clage_regions = df_incid_clage.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()


# In[12]:


df_tests_viros_regions = df_tests_viros_enrichi.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()
df_tests_viros_france = df_tests_viros_enrichi.groupby(["jour", "cl_age90"]).sum().reset_index()


# In[13]:


df_hosp_clage = data.import_data_hosp_clage()
df_hosp_clage_france = df_hosp_clage.groupby(["jour", "cl_age90"]).sum().reset_index()
df_hosp_clage_regions = df_hosp_clage.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()


# In[14]:


departements = list(dict.fromkeys(list(df_incid['dep'].values))) 
regions = list(dict.fromkeys(list(df_incid['regionName'].dropna().values))) 
clage_list = list(dict.fromkeys(list(df_incid_fra_clage['cl_age90'].dropna().values))) 

df_regions = df.groupby(["jour", "regionName"]).sum().reset_index()
df_incid_regions = df_incid.groupby(["jour", "regionName"]).sum().reset_index()


zone_a = ["zone_a", "01", "03", "07", "15", "16", "17", "19", "21", "23", "24", "25", "26", "33", "38", "39", "40", "42", "43", "47", "58", "63", "64", "69", "70", "71", "73", "74", "79", "86", "90"]
zone_b = ["zone_b", "02", "04", "05", "06", "08", "10", "13", "14", "18", "22", "27", "28", "29", "35", "36", "37", "41", "44", "45", "49", "50", "51", "52", "53", "54", "55", "56", "57", "59", "60", "61", "62", "67", "68", "72", "76", "80", "83", "84", "85", "88"]
zone_c = ["zone_c", "09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "75", "77", "78", "81", "82", "91", "92", "93", "94", "95"]

confines_mars_2021 = ["confines_mars_2021", "02", "06", "27", "59", "60", "62", "75", "76", "77", "78", "80", "91", "92", "93", "94", "95"]


# In[15]:


def generate_data(data_incid=pd.DataFrame(), data_hosp=pd.DataFrame(), data_sursaud=pd.DataFrame(), data_new=pd.DataFrame(), data_vue_ensemble=pd.DataFrame(), data_metropole=pd.DataFrame(), data_vacsi=pd.DataFrame(), data_obepine=pd.DataFrame(), mode="", export_jour=False):## Incidence
        
    dict_data = {}
    
    if export_jour:
        dict_data["jour_incid"] = list(data_incid.jour)
        dict_data["jour_hosp"] = list(data_hosp.jour)
        dict_data["jour_new"] = list(data_new.jour)
        dict_data["jour_sursaud"] = list(data_sursaud.date_de_passage)
        dict_data["jour_metropoles"] = list(data_metropole.jour.unique())
        dict_data["jour_vacsi"] = list(data_vacsi.jour)
        dict_data["jour_obepine"] = list(data_obepine.Date)
        
    if(len(data_vacsi)>0):
        n_cum_dose1 = data_vacsi["n_cum_dose1"].fillna(0)
        dict_data["n_cum_dose1"] = {"jour_nom": "jour_vacsi", "valeur": list(n_cum_dose1)}
        
        n_dose1 = data_vacsi["n_dose1"].rolling(window=7).mean().fillna(0)
        dict_data["n_dose1"] = {"jour_nom": "jour_vacsi", "valeur": list(n_dose1)}
    
    if len(data_vue_ensemble)>0:
        dict_data["jour_ehpad"] = list(data_vue_ensemble.date)
        deces_ehpad = data_vue_ensemble["total_deces_ehpad"].diff().rolling(window=7).mean().fillna(0)
        dict_data["deces_ehpad"] = {"jour_nom": "jour_ehpad", "valeur": list(round(deces_ehpad,2))}
        
        cas_spf = data_vue_ensemble.total_cas_confirmes.diff().rolling(window=7).mean().fillna(0)
        dict_data["cas_spf"] = {"jour_nom": "jour_ehpad", "valeur": list(round(cas_spf, 2))}
        
    if len(data_obepine)>0:
        indicateur_obepine = data_obepine.Indicateur.fillna(0)
        
        dict_data["obepine"] = {"jour_nom": "jour_obepine", "jours":list(data_obepine.Date), "valeur": list(round(indicateur_obepine, 2))}
        
    if len(data_incid)>0:
        taux_incidence = data_incid["P"].rolling(window=7).sum().fillna(0) * 100000 / data_incid["pop"].values[0]
        dict_data["incidence"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_incidence,2))}

        taux_positivite = (data_incid["P"] / data_incid["T"] * 100).rolling(window=7).mean().fillna(0)
        dict_data["taux_positivite"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_positivite,2))}
        
        taux_positivite = (data_incid["P"].rolling(window=7).mean() / data_incid["T"].rolling(window=7).mean() * 100).fillna(0)
        dict_data["taux_positivite_rolling_before"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_positivite,2))}
    
        cas = data_incid["P"].rolling(window=7).mean().fillna(0)
        dict_data["cas"] = {"jour_nom": "jour_incid", "valeur": list(round(cas,2))}
    
        tests = data_incid["T"].rolling(window=7).mean().fillna(0)
        dict_data["tests"] = {"jour_nom": "jour_incid", "valeur": list(round(tests,2))}
        
    if (len(data_metropole)>0) & (mode=="metropoles"):
        taux_incidence = data_metropole["ti"].fillna(0)
        dict_data["incidence"] = {"jour_nom": "jour_metropoles", "valeur": list(round(taux_incidence, 2))}
        
    if len(data_hosp)>0:
        hospitalisations = data_hosp.hosp.fillna(0)
        dict_data["hospitalisations"] = {"jour_nom": "jour_hosp", "valeur": list(hospitalisations)}

        reanimations = data_hosp.rea.fillna(0)
        dict_data["reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(reanimations)}
        
        saturation_rea = round(data_hosp["rea"]/data_hosp["LITS"].fillna(0)*100, 2)
        dict_data["saturation_reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(saturation_rea)}
    
    if len(data_new)>0:
        incid_hospitalisations = data_new.incid_hosp.rolling(window=7).mean().fillna(0)
        dict_data["incid_hospitalisations"] = {"jour_nom": "jour_new", "valeur": list(round(incid_hospitalisations, 2))}

        incid_reanimations = data_new.incid_rea.rolling(window=7).mean().fillna(0)
        dict_data["incid_reanimations"] = {"jour_nom": "jour_new", "valeur": list(round(incid_reanimations,2))}
    
    if len(data_sursaud)>0:
        nbre_acte_corona = data_sursaud.nbre_acte_corona.rolling(window=7).mean().fillna(0)
        dict_data["nbre_acte_corona"] = {"jour_nom": "jour_sursaud", "valeur": list(round(nbre_acte_corona, 2))}

        nbre_pass_corona = data_sursaud.nbre_pass_corona.rolling(window=7).mean().fillna(0)
        dict_data["nbre_pass_corona"] = {"jour_nom": "jour_sursaud", "valeur": list(round(nbre_pass_corona, 2))}
    
    if len(data_hosp)>0:
        deces_hospitaliers = data_hosp.dc.diff().rolling(window=7).mean().fillna(0)
        dict_data["deces_hospitaliers"] = {"jour_nom": "jour_hosp", "valeur": list(round(deces_hospitaliers,2))}
    
    if len(data_incid)>0:
        population = data_incid["pop"].values[0]
        dict_data["population"] = population

    return dict_data
 


# In[16]:


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

        taux_positivite = (data_incid_clage["P"] / data_incid_clage["T"] * 100).rolling(window=7).mean().fillna(0)
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
 


# In[17]:


def export_data(data, suffix=""):
    with open(PATH_STATS + 'dataexplorer{}.json'.format(suffix), 'w') as outfile:
        json.dump(data, outfile)


# In[18]:


departements


# In[19]:


def dataexplorer():
    dict_data = {}
    
    dict_data["regions"] = sorted(regions)
    dict_data["metropoles"] = sorted(metropoles)
    dict_data["departements"] = departements
    dict_data["france"] = generate_data(df_incid_fra, df_france, df_sursaud_france, df_new_france, df_vue_ensemble, data_metropole=df_metro_0, data_vacsi=df_vacsi, data_obepine=df_obepine_france, mode="france", export_jour=True)
    
    noms_departements={}
    
    for reg in regions:
        
        dict_data[reg] = generate_data(df_incid_regions[df_incid_regions.regionName==reg],                                        df_regions[df_regions.regionName==reg],                                       df_sursaud_regions[df_sursaud_regions.regionName==reg],
                                       df_new_regions[df_new_regions.regionName==reg],
                                       data_vacsi=df_vacsi_reg[df_vacsi_reg.regionName==reg],\
                                       data_obepine=df_obepine[df_obepine.regionName==reg]
                                      )
        #print(df_vacsi_reg[df_vacsi_reg.regionName==reg])
    
    for dep in departements:
        df_incid_dep = df_incid[df_incid.dep==dep]
        dict_data[dep] = generate_data(df_incid_dep, df[df.dep==dep], df_sursaud[df_sursaud.dep==dep], df_new[df_new.dep==dep], data_vacsi=df_vacsi_dep[df_vacsi_dep.dep==dep])
        
        noms_departements[dep] = df_incid_dep["departmentName"].values[0]
    dict_data["departements_noms"] = noms_departements
    
    for zone in [zone_a, zone_b, zone_c]:
        df_incid_zone = df_incid[df_incid.dep.isin(zone)].groupby("jour").sum().reset_index()
        df_zone = df[df.dep.isin(zone)].groupby("jour").sum().reset_index()
        df_sursaud_zone = df_sursaud[df_sursaud.dep.isin(zone)].groupby("date_de_passage").sum().reset_index()
        df_new_zone = df_new[df_new.dep.isin(zone)].groupby("jour").sum().reset_index()
        df_vacsi_zone = df_vacsi_dep[df_vacsi_dep.dep.isin(zone)].groupby("jour").sum().reset_index()
        
        dict_data[zone[0]] = generate_data(df_incid_zone, df_zone, df_sursaud_zone, df_new_zone, data_vacsi=df_vacsi_zone)
    
    # Confinés mars 2021
    df_incid_zone = df_incid[df_incid.dep.isin(confines_mars_2021)].groupby("jour").sum().reset_index()
    df_zone = df[df.dep.isin(confines_mars_2021)].groupby("jour").sum().reset_index()
    df_sursaud_zone = df_sursaud[df_sursaud.dep.isin(confines_mars_2021)].groupby("date_de_passage").sum().reset_index()
    df_new_zone = df_new[df_new.dep.isin(confines_mars_2021)].groupby("jour").sum().reset_index()
    df_vacsi_zone = df_vacsi_dep[df_vacsi_dep.dep.isin(confines_mars_2021)].groupby("jour").sum().reset_index()
    
    dict_data["confines_mars_2021"] = generate_data(df_incid_zone, df_zone, df_sursaud_zone, df_new_zone, data_vacsi=df_vacsi_zone)
        
    for metropole in metropoles:
        print(metropole)
        dict_data[metropole] = generate_data(data_metropole=df_metro_0[df_metro_0.Metropole == metropole], mode="metropoles")
        #print(dict_data[metropole])
        
    dict_data["zones_vacances"] = ["zone_a", "zone_b", "zone_c"]
    
    export_data(dict_data, suffix="_compr")


# In[20]:


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
            #print(dep)
            nom_dep = "--"
        
        noms_departements[dep] = nom_dep
        
    dict_data["departements_noms"] = noms_departements
    
    export_data(dict_data, suffix="_compr_age")
    return dict_data


# In[21]:


dataexplorer()


# In[22]:


dict_data = dataexplorer_age()

