#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.guillaumerozier.fr
Mail : guillaume.rozier@telecomnancy.net

README:
This file contains a script that automatically update data. In the morning it update World data, and it updates French data as soon as they are released by Santé publique France.
"""


# In[ ]:


import datetime as dt
import time
import subprocess
import requests
import re
import os

#os.chdir("../")
BASE_CWD = os.getcwd()
PATH_WORLD = BASE_CWD + "/src/world/"
PATH_FRANCE = BASE_CWD + "/src/france/"

### FUNCTION DEFINITIONS ###
url_metadata = "https://www.data.gouv.fr/fr/organizations/sante-publique-france/datasets-resources.csv"
metadata = requests.get(url_metadata)
content = str(metadata.content)

def update_repo():
    os.chdir(BASE_CWD)
    subprocess.run(["sudo", "git", "fetch", "--all"])
    subprocess.run(["sudo", "git", "reset", "--hard", "origin/master"])
    subprocess.run(["sudo", "jupyter", "nbconvert", "--to", "script", "server/*.ipynb", "src/france/*.ipynb", "src/world/*.ipynb"])
    
def push(type_data):
    os.chdir(BASE_CWD)
    subprocess.run(["sudo", "git", "add", "images/", "data/"])
    subprocess.run(["sudo", "git", "commit", "-m", "[auto] data update: {}".format(type_data)])
    subprocess.run(["git", "push"])
    print("pushed")
    os.chdir(PATH_FRANCE)
    
def get_datetime_spf():
    metadata = requests.get(url_metadata)
    content = str(metadata.content)
    re_result = re.search("donnees-hospitalieres-nouveaux-covid19-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}h[0-9]{2}.csv", content)
    re_date = re.match(".*covid19-([0-9]{4})-([0-9]{2})-([0-9]{2})-([0-9]{2})h([0-9]{2}).csv", re_result[0])
    datetime_object = dt.datetime.strptime(re_date[1] + re_date[2] + re_date[3] + re_date[4] + re_date[5], '%Y%m%d%H%M')
    return datetime_object

def update_france():
    now = dt.datetime.now()
    datetime_spf = get_datetime_spf()
    print("try update, now: "+ str(dt.datetime.now()))
    print("datetime_spf: " + str(datetime_spf))
    
    t1 = dt.datetime.now()
    t2 = datetime_spf
    print("diff t1 t2: {}".format(max(t1, t2) - min(t1, t2)) )
    print("(max(t1, t2) - min(t1, t2)).total_seconds()/3600 = {}".format((max(t1, t2) - min(t1, t2)).total_seconds()/3600) )
    if ( True ): # Si le fichier SPF date d'il y à moins de 2h
        metadata = requests.get(url_metadata)
        content = str(metadata.content)
        
        print("starting France update: {}:{}".format(str(now.hour), str(now.minute)))
        #update_repo()
        
        os.chdir(PATH_FRANCE)
        # Mise à jour des graphiques
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_charts_fastlane.py"])
        push("France fastlane")
        print("update France charts: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_data_explorer.py"])
        push("Data Explorer")
        print("update data explorer: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_charts.py"])
        push("France")
        print("update France charts: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_map_incid.py"])
        push("France map incid")
        print("update France local: " + str(now.hour) + ":" + str(now.minute))
    
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_variants.py"])
        push("France variants")
        print("update variants : " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_metropoles.py"])
        push("France metropoles")
        print("update France local: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_local_charts.py"])
        push("France local subplots")
        print("update France local: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_heatmaps.py"])
        push("Dep heatmaps")
        print("update France heatmaps: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_utils.py"])
        push("Utils")
        print("update France utils: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_maps.py"])
        push("France GIF")
        print("update France GIF: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_charts_cas_hospitalisations.py.py"])
        push("France Cas Hosp Comparaison")
        print("update France Cas Hosp Comparaison: " + str(now.hour) + ":" + str(now.minute))
        
        os.chdir(BASE_CWD)
        
    return datetime_spf

    
update_france()

