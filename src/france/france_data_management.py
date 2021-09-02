#!/usr/bin/env python
# coding: utf-8

# In[3]:


import requests
import pandas as pd
import json
from tqdm import tqdm
PATH = '../../'
PATH_STATS = "../../data/france/stats/"


# In[5]:


# Download data from Santé publique France and export it to local files
def download_data_hosp_fra_clage():
    data = requests.get("https://www.data.gouv.fr/fr/datasets/r/08c18e08-6780-452d-9b8c-ae244ad529b3")
    with open(PATH + 'data/france/donnees-hosp-fra-clage.csv', 'wb') as f:
        f.write(data.content)

def download_data_opencovid():
    data = requests.get("https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv")
    with open(PATH + 'data/france/donnees-opencovid.csv', 'wb') as f:
        f.write(data.content)
        
def download_data_vue_ensemble():
    data = requests.get("https://www.data.gouv.fr/fr/datasets/r/d3a98a30-893f-47f7-96c5-2f4bcaaa0d71")        
    with open(PATH + 'data/france/synthese-fra.csv', 'wb') as f:
        f.write(data.content)

def download_data_variants():
    data = requests.get("https://www.data.gouv.fr/fr/datasets/r/848debc4-0e42-4e3b-a176-afc285ed5401") #https://www.data.gouv.fr/fr/datasets/r/c43d7f3f-c9f5-436b-9b26-728f80e0fd52
    data_reg = requests.get("https://www.data.gouv.fr/fr/datasets/r/5ff0cad6-f150-47ea-a4e0-57e354c1b2a4") #https://www.data.gouv.fr/fr/datasets/r/73e8851a-d851-43f8-89e4-6178b35b7127
    with open(PATH + 'data/france/donnees-variants.csv', 'wb') as f:
        f.write(data.content)
    with open(PATH + 'data/france/donnees-variants-reg.csv', 'wb') as f:
        f.write(data.content)
        
def download_data_variants_deps():
    data = requests.get("https://www.data.gouv.fr/fr/datasets/r/4d3e5a8b-9649-4c41-86ec-5420eb6b530c") #https://www.data.gouv.fr/fr/datasets/r/16f4fd03-797f-4616-bca9-78ff212d06e8        
    with open(PATH + 'data/france/donnees-variants-deps.csv', 'wb') as f:
        f.write(data.content)

def download_data_vacsi_fra():
    data = requests.get("https://www.data.gouv.fr/fr/datasets/r/efe23314-67c4-45d3-89a2-3faef82fae90")        
    with open(PATH + 'data/france/donnees-vacsi-fra.csv', 'wb') as f:
        f.write(data.content)
        
def download_data_vacsi_reg():
    data = requests.get("https://www.data.gouv.fr/fr/datasets/r/735b0df8-51b4-4dd2-8a2d-8e46d77d60d8")        
    with open(PATH + 'data/france/donnees-vacsi-reg.csv', 'wb') as f:
        f.write(data.content)
        
def download_data_vacsi_dep():
    data = requests.get("https://www.data.gouv.fr/fr/datasets/r/4f39ec91-80d7-4602-befb-4b522804c0af")        
    with open(PATH + 'data/france/donnees-vacsi-dep.csv', 'wb') as f:
        f.write(data.content)

def download_data_obepine():
    data = requests.get("https://www.data.gouv.fr/fr/datasets/r/031b79a4-5ee1-4f40-a804-b8abec3e99a6") #https://www.data.gouv.fr/fr/datasets/r/ba71be57-5932-4298-81ea-aff3a12a440c        
    with open(PATH + 'data/france/donnees_obepine_regions.csv', 'wb') as f:
        f.write(data.content)
        
def download_data_donnees_vaccination_par_pathologie():
    data = requests.get("https://datavaccin-covid.ameli.fr/explore/dataset/donnees-vaccination-par-pathologie/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B")
    with open(PATH + 'data/france/donnees-vaccination-par-pathologie.csv', 'wb') as f:
        f.write(data.content)
        
def import_data_donnees_vaccination_par_pathologie():
    df = pd.read_csv(PATH + 'data/france/donnees-vaccination-par-pathologie.csv', sep=None)
    return df

def download_donnees_vaccination_par_tranche_dage_type_de_vaccin_et_departement():
    data = requests.get("https://datavaccin-covid.ameli.fr/explore/dataset/donnees-vaccination-par-tranche-dage-type-de-vaccin-et-departement/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B")
    with open(PATH + 'data/france/donnees-tranche-dage-departement.csv', 'wb') as f:
        f.write(data.content)
        
def import_donnees_vaccination_par_tranche_dage_type_de_vaccin_et_departement():
    df = pd.read_csv(PATH + 'data/france/donnees-tranche-dage-departement.csv', sep=None)
    return df

def import_data_obepine():
    df = pd.read_csv(PATH + 'data/france/donnees_obepine_regions.csv', sep=None)
    df_reg_pop = pd.read_csv(PATH + 'data/france/population_grandes_regions.csv', sep=",")
    df = df.merge(right=df_reg_pop, left_on="Code_Region", right_on="code")
    return df

def import_data_metropoles():
    df_metro = pd.read_csv(PATH + 'data/france/donnes-incidence-metropoles.csv', sep=",")
    epci = pd.read_csv(PATH + 'data/france/metropole-epci.csv', sep=";", encoding="'windows-1252'")
    
    df_metro = df_metro.merge(epci, left_on='epci2020', right_on='EPCI').drop(['EPCI'], axis=1)
    
    return df_metro

def import_data_hosp_clage():
    df_hosp = pd.read_csv(PATH + 'data/france/donnes-hospitalieres-clage-covid19.csv', sep=";")
    df_hosp = df_hosp.groupby(["reg", "jour", "cl_age90"]).first().reset_index()
    df_reg_pop = pd.read_csv(PATH + 'data/france/population_grandes_regions.csv', sep=",")
    df_hosp = df_hosp.merge(df_reg_pop, left_on="reg", right_on="code")
    
    return df_hosp

def import_data_tests_viros():
    df = pd.read_csv(PATH + 'data/france/tests_viro-dep-quot.csv', sep=";")

    df_reg_pop = pd.read_csv(PATH + 'data/france/population_grandes_regions.csv', sep=",")
    df_dep_reg = pd.read_csv(PATH + 'data/france/departments_regions_france_2016.csv', sep=",")
    
    df["dep"] = df["dep"].astype(str)
    df["dep"] = df["dep"].astype('str').str.replace(r"^([1-9])$", lambda m: "0"+m.group(0), regex=True)
    df_dep_reg["departmentCode.astype"] = df_dep_reg.departmentCode.astype(str)
    
    df = df.merge(df_dep_reg, left_on="dep", right_on="departmentCode", how="left")
    df = df.merge(df_reg_pop, left_on="regionCode", right_on="code", how="left")
    
    return df

def import_data_hosp_ad_age():
    df = pd.read_csv('https://www.data.gouv.fr/fr/datasets/r/dc7663c7-5da9-4765-a98b-ba4bc9de9079', sep=";")
    return df
    
def import_data_new():
    df_new = pd.read_csv(PATH + 'data/france/donnes-hospitalieres-covid19-nouveaux.csv', sep=";")
    return df_new

def import_data_df():
    df = pd.read_csv(PATH + 'data/france/donnes-hospitalieres-covid19.csv', sep=";")
    return df

def import_data_variants():
    df_variants = pd.read_csv(PATH + 'data/france/donnees-variants.csv', sep=";")
    df_variants["jour"] = df_variants.semaine.apply(lambda x: x[11:]) 
    #df_variants = df_variants[df_variants.cl_age90==0]
    return df_variants

def import_data_variants_deps():
    df_variants = pd.read_csv(PATH + 'data/france/donnees-variants-deps.csv', sep=";")
    df_variants["jour"] = df_variants.semaine.apply(lambda x: x[11:]) 
    #df_variants = df_variants[df_variants.cl_age90==0]
    return df_variants

def import_data_variants_regs():
    df_variants = pd.read_csv(PATH + 'data/france/donnees-variants-regs.csv', sep=";")
    df_variants["jour"] = df_variants.semaine.apply(lambda x: x[11:]) 
    df_variants = df_variants[df_variants.cl_age90==0]
    df_reg_pop = pd.read_csv(PATH + 'data/france/population_grandes_regions.csv', sep=",")
    df_variants = df_variants.merge(df_reg_pop, left_on="reg", right_on="code")
    return df_variants

def import_data_tests_sexe():
    df = pd.read_csv(PATH + 'data/france/tests_viro-fra-covid19.csv', sep=";")
    return df

def import_data_vue_ensemble():
    df = pd.read_csv(PATH + 'data/france/synthese-fra.csv', sep=",")
    df = df.sort_values(["date"])
    
    with open(PATH_STATS + 'vue-ensemble.json', 'w') as outfile:
        dict_data = {"cas":  int(df["total_cas_confirmes"].diff().values[-1]), "update": df.date.values[-1][-2:] + "/" + df.date.values[-1][-5:-3]}
        json.dump(dict_data, outfile)
        
    return df

def import_data_opencovid():
    df = pd.read_csv(PATH + 'data/france/donnees-opencovid.csv', sep=",")
    
    """with open(PATH_STATS + 'opencovid.json', 'w') as outfile:
        dict_data = {"cas":  int(df["cas_confirmes"].values[-1]), "update": df.index.values[-1][-2:] + "/" + df.index.values[-1][-5:-3]}
        json.dump(dict_data, outfile)"""
    return df

def import_data_vacsi_a_fra():
    df = pd.read_csv(PATH + 'data/france/donnees-vacsi-a-fra.csv', sep=";")
    df = df[df.clage_vacsi != 0]
    return df

def import_data_vacsi_reg():
    df = pd.read_csv(PATH + 'data/france/donnees-vacsi-reg.csv', sep=";")
    return df

def import_data_vacsi_dep():
    df = pd.read_csv(PATH + 'data/france/donnees-vacsi-dep.csv', sep=";")
    return df

def import_data_vacsi_fra():
    df = pd.read_csv(PATH + 'data/france/donnees-vacsi-fra.csv', sep=";")
    return df
    
def import_data_vacsi_a_reg():
    df = pd.read_csv(PATH + 'data/france/donnees-vacsi-a-reg.csv', sep=";")
    df = df[df.clage_vacsi != 0]
    return df

def import_data_vacsi_a_dep():
    df = pd.read_csv(PATH + 'data/france/donnees-vacsi-a-dep.csv', sep=";")
    df = df[df.clage_vacsi != 0]
    return df

def import_data_hosp_fra_clage():
    df = pd.read_csv(PATH + 'data/france/donnees-hosp-fra-clage.csv', sep=";").groupby(["cl_age90", "jour"]).sum().reset_index()
    df = df[df.cl_age90 != 0]
    return df

def download_data():
    pbar = tqdm(total=8)
    download_data_vacsi_fra()
    download_data_vacsi_reg()
    download_data_vacsi_dep()
    
    url_metadata = "https://www.data.gouv.fr/fr/organizations/sante-publique-france/datasets-resources.csv"
    url_geojson = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
    url_deconf = "https://www.data.gouv.fr/fr/datasets/r/f2d0f955-f9c4-43a8-b588-a03733a38921"
    url_opencovid = "https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv"
    url_vacsi_a_fra = "https://www.data.gouv.fr/fr/datasets/r/54dd5f8d-1e2e-4ccb-8fb8-eac68245befd"
    url_vacsi_a_reg = "https://www.data.gouv.fr/fr/datasets/r/c3ccc72a-a945-494b-b98d-09f48aa25337"
    url_vacsi_a_dep = "https://www.data.gouv.fr/fr/datasets/r/83cbbdb9-23cb-455e-8231-69fc25d58111"
    
    pbar.update(1)
    metadata = requests.get(url_metadata)
    pbar.update(2)
    geojson = requests.get(url_geojson)
    pbar.update(3)
    
    with open(PATH + 'data/france/metadata.csv', 'wb') as f:
        f.write(metadata.content)
    pbar.update(4)
    
    with open(PATH + 'data/france/dep.geojson', 'wb') as f:
        f.write(geojson.content)
        
    pbar.update(5)
    df_metadata = pd.read_csv(PATH + 'data/france/metadata.csv', sep=";")
    
    url_data = "https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7" #df_metadata[df_metadata['url'].str.contains("/donnees-hospitalieres-covid19")]["url"].values[0] #donnees-hospitalieres-classe-age-covid19-2020-10-14-19h00.csv 
    url_data_new = "https://www.data.gouv.fr/fr/datasets/r/6fadff46-9efd-4c53-942a-54aca783c30c" #df_metadata[df_metadata['url'].str.contains("/donnees-hospitalieres-nouveaux")]["url"].values[0]
    url_tests = df_metadata[df_metadata['url'].str.contains("/donnees-tests-covid19-labo-quotidien")]["url"].values[0]
    url_metropoles = "https://www.data.gouv.fr/fr/datasets/r/61533034-0f2f-4b16-9a6d-28ffabb33a02" #df_metadata[df_metadata['url'].str.contains("/sg-metro-opendata")]["url"].max()
    url_incidence = df_metadata[df_metadata['url'].str.contains("/sp-pe-tb-quot")]["url"].values[0]
    
    url_tests_viro = df_metadata[df_metadata['url'].str.contains("/sp-pos-quot-dep")]["url"].values[0]
    
    url_sursaud = df_metadata[df_metadata['url'].str.contains("sursaud.*quot.*dep")]["url"].values[0]
    url_data_clage = df_metadata[df_metadata['url'].str.contains("/donnees-hospitalieres-classe-age-covid19")]["url"].values[0]
    url_data_sexe = "https://www.data.gouv.fr/fr/datasets/r/dd0de5d9-b5a5-4503-930a-7b08dc0adc7c" #df_metadata[df_metadata['url'].str.contains("/sp-pos-quot-fra")]["url"].values[0]

        
    pbar.update(6)
    data = requests.get(url_data)
    data_new = requests.get(url_data_new)
    data_tests = requests.get(url_tests)
    data_metropoles = requests.get(url_metropoles)
    data_deconf = requests.get(url_deconf)
    data_sursaud = requests.get(url_sursaud)
    data_incidence = requests.get(url_incidence)
    data_opencovid = requests.get(url_opencovid)
    data_vacsi_a_fra = requests.get(url_vacsi_a_fra)
    data_vacsi_a_reg = requests.get(url_vacsi_a_reg)
    data_vacsi_a_dep = requests.get(url_vacsi_a_dep)
    
    data_tests_viro = requests.get(url_tests_viro)
    data_clage = requests.get(url_data_clage)
    data_sexe = requests.get(url_data_sexe)
    
    pbar.update(7)
    with open(PATH + 'data/france/donnes-hospitalieres-covid19.csv', 'wb') as f:
        f.write(data.content)
        
    with open(PATH + 'data/france/donnes-hospitalieres-covid19-nouveaux.csv', 'wb') as f:
        f.write(data_new.content)
        
    with open(PATH + 'data/france/donnes-tests-covid19-quotidien.csv', 'wb') as f:
        f.write(data_tests.content)
        
    with open(PATH + 'data/france/donnes-incidence-metropoles.csv', 'wb') as f:
        f.write(data_metropoles.content)
        
    with open(PATH + 'data/france/indicateurs-deconf.csv', 'wb') as f:
        f.write(data_deconf.content)
    
    with open(PATH + 'data/france/sursaud-covid19-departement.csv', 'wb') as f:
        f.write(data_sursaud.content)
        
    with open(PATH + 'data/france/taux-incidence-dep-quot.csv', 'wb') as f:
        f.write(data_incidence.content)
        
    with open(PATH + 'data/france/tests_viro-dep-quot.csv', 'wb') as f:
        f.write(data_tests_viro.content)
        
    with open(PATH + 'data/france/donnes-hospitalieres-clage-covid19.csv', 'wb') as f:
        f.write(data_clage.content)
        
    with open(PATH + 'data/france/tests_viro-fra-covid19.csv', 'wb') as f:
        f.write(data_sexe.content)
        
    with open(PATH + 'data/france/donnees-opencovid.csv', 'wb') as f:
        f.write(data_opencovid.content)
        
    with open(PATH + 'data/france/donnees-vacsi-a-fra.csv', 'wb') as f:
        f.write(data_vacsi_a_fra.content)
        
    with open(PATH + 'data/france/donnees-vacsi-a-reg.csv', 'wb') as f:
        f.write(data_vacsi_a_reg.content)
        
    with open(PATH + 'data/france/donnees-vacsi-a-dep.csv', 'wb') as f:
        f.write(data_vacsi_a_dep.content)
        
    pbar.update(8)

# Import data from previously exported files to dataframes
def import_data():
    
    pbar = tqdm(total=8)
    pbar.update(1)
    df = pd.read_csv(PATH + 'data/france/donnes-hospitalieres-covid19.csv', sep=";")
    df.dep = df.dep.astype(str)
    df_sursaud = pd.read_csv(PATH + 'data/france/sursaud-covid19-departement.csv', sep=";")
    df_sursaud["dep"] = df_sursaud["dep"].astype('str').str.replace(r"^([1-9])$", lambda m: "0"+m.group(0), regex=True)
    
    df_new = pd.read_csv(PATH + 'data/france/donnes-hospitalieres-covid19-nouveaux.csv', sep=";")
    df_tests = pd.read_csv(PATH + 'data/france/donnes-tests-covid19-quotidien.csv', sep=";")
    df_deconf = pd.read_csv(PATH + 'data/france/indicateurs-deconf.csv', sep=",")
    df_incid = pd.read_csv(PATH + 'data/france/taux-incidence-dep-quot.csv', sep=";")
    df_incid["dep"] = df_incid["dep"].astype('str')
    df_incid["dep"] = df_incid["dep"].astype('str').str.replace(r"^([1-9])$", lambda m: "0"+m.group(0), regex=True)

    df_tests_viro = pd.read_csv(PATH + 'data/france/tests_viro-dep-quot.csv', sep=";")
    df_tests_viro["dep"] = df_tests_viro["dep"].astype('str').str.replace(r"^([1-9])$", lambda m: "0"+m.group(0), regex=True)
    
    pbar.update(2)
    
    df_tests_viro["dep"] = df_tests_viro["dep"].astype('str')
    
    pop_df_incid = df_incid["pop"]
    
    lits_reas = pd.read_csv(PATH + 'data/france/lits_rea.csv', sep=",")
    
    df_regions = pd.read_csv(PATH + 'data/france/departments_regions_france_2016.csv', sep=",")
    df_reg_pop = pd.read_csv(PATH + 'data/france/population_grandes_regions.csv', sep=",")
    df_dep_pop = pd.read_csv(PATH + 'data/france/dep-pop.csv', sep=";")
    ###
    df = df.merge(df_regions, left_on='dep', right_on='departmentCode')
    df = df.merge(df_reg_pop, left_on='regionName', right_on='regionName')
    df = df.merge(df_dep_pop, left_on='dep', right_on='dep')
    df = df[df["sexe"] == 0]
    df['hosp_nonrea'] = df['hosp'] - df['rea']
    df = df.merge(lits_reas, left_on="departmentName", right_on="nom_dpt")
    #df_tests_viro = df_tests_viro[df_tests_viro["cl_age90"] == 0]
    
    df_incid = df_incid.merge(df_regions, left_on='dep', right_on='departmentCode')
    
    if "pop" in df_tests_viro.columns:
        df_incid = df_incid.merge(df_tests_viro[df_tests_viro["cl_age90"] == 0].drop("pop", axis=1).drop("P", axis=1).drop("cl_age90", axis=1), left_on=['jour', 'dep'], right_on=['jour', 'dep'])
    else:
        df_incid = df_incid.merge(df_tests_viro[df_tests_viro["cl_age90"] == 0].drop("P", axis=1).drop("cl_age90", axis=1), left_on=['jour', 'dep'], right_on=['jour', 'dep'])
    
    df_new = df_new.merge(df_regions, left_on='dep', right_on='departmentCode')
    df_new = df_new.merge(df_reg_pop, left_on='regionName', right_on='regionName')
    df_new = df_new.merge(df_dep_pop, left_on='dep', right_on='dep')
    df_new['incid_hosp_nonrea'] = df_new['incid_hosp'] - df_new['incid_rea']
    
    df_sursaud = df_sursaud.merge(df_regions, left_on='dep', right_on='departmentCode')
    df_sursaud = df_sursaud.merge(df_reg_pop, left_on='regionName', right_on='regionName')
    df_sursaud = df_sursaud.merge(df_dep_pop, left_on='dep', right_on='dep')
    
    df_sursaud = df_sursaud[df_sursaud["sursaud_cl_age_corona"] == "0"]
    df_sursaud["taux_covid"] = df_sursaud["nbre_pass_corona"] / df_sursaud["nbre_pass_tot"]
    
    pbar.update(3)
    
    df['rea_pop'] = df['rea']/df['regionPopulation']*100000
    df['rea_deppop'] = df['rea']/df['departmentPopulation']*100000
    
    df['rad_pop'] = df['rad']/df['regionPopulation']*100000
    
    df['dc_pop'] = df['dc']/df['regionPopulation']*100000
    df['dc_deppop'] = df['dc']/df['departmentPopulation']*100000
    
    df['hosp_pop'] = df['hosp']/df['regionPopulation']*100000
    df['hosp_deppop'] = df['hosp']/df['departmentPopulation']*100000
    
    df['hosp_nonrea_pop'] = df['hosp_nonrea']/df['regionPopulation']*100000
    
    pbar.update(4)
    
    df_confirmed = pd.read_csv(PATH + 'data/data_confirmed.csv')
    
    pbar.update(5)
    
    deps = list(dict.fromkeys(list(df['departmentCode'].values))) 
    for d in deps:
        for col in ["dc", "rad", "rea", "hosp_nonrea", "hosp"]:
            vals = df[df["dep"] == d][col].diff()
            df.loc[vals.index,col+"_new"] = vals
            df.loc[vals.index,col+"_new_deppop"] = vals / df.loc[vals.index,"departmentPopulation"]*100000
    
    df_tests = df_tests.drop(['nb_test_h', 'nb_pos_h', 'nb_test_f', 'nb_pos_f'], axis=1)
    df_tests = df_tests[df_tests['clage_covid'] == "0"]
    
    pbar.update(6)
    
    # Correction du 14/05 (pas de données)
    #cols_to_change = df.select_dtypes(include=np.number).columns.tolist()
    #cols_to_change = [s for s in df.columns.tolist() if "new" in s]

    df['jour'] = df['jour'].str.replace(r'(.*)/(.*)/(.*)',r'\3-\2-\1')     
    dates = sorted(list(dict.fromkeys(list(df['jour'].values))))
    
    for dep in pd.unique(df_incid["dep"].values):
        for clage in [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 90]:
            df_incid.loc[(df_incid["dep"] == dep) & (df_incid["cl_age90"]==clage),"incidence"] = df_incid.loc[(df_incid["dep"] == dep) & (df_incid["cl_age90"]==clage)]["P"].rolling(window=7).sum()/df_incid.loc[(df_incid["dep"] == dep) & (df_incid["cl_age90"]==clage)]["pop"]*100000
    df_incid.loc[:,"incidence_color"] = ['Alerte Maximale' if x>= 250 else 'Alerte Renforcée' if x>=150 else 'Alerte' if x >= 50 else 'Risque Faible' for x in df_incid['incidence']]
    
    pbar.update(7)
    
    df_tests_viro["pop"] = pop_df_incid
    
    df = df.groupby(["dep", "jour"]).first().reset_index()
    df_new = df_new.groupby(["dep", "jour"]).first().reset_index()
    
    pbar.update(8)
    import_data_opencovid()
    return df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viro


# In[8]:


#import_data_opencovid()
#download_data()
#df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viro = import_data()


# In[11]:


#df = pd.read_csv(PATH + 'data/france/donnes-hospitalieres-covid19.csv', sep=";")
#df[df.dep=="59"]


# In[35]:


"""df = pd.read_csv(PATH + 'data/france/tests_viro-dep-quot.csv', sep=";")
    
df_reg_pop = pd.read_csv(PATH + 'data/france/population_grandes_regions.csv', sep=",")
df_dep_reg = pd.read_csv(PATH + 'data/france/departments_regions_france_2016.csv', sep=",")

df["dep"] = df["dep"].astype(str)
df_dep_reg["departmentCode.astype"] = df_dep_reg.departmentCode.astype(str)

df = df.merge(df_dep_reg, left_on="dep", right_on="departmentCode", how="left")
#df = df.merge(df_reg_pop, left_on="regionCode", right_on="code", how="left")
df[df.regionName.isna()].dep.unique()
"""

