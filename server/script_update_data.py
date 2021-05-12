#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.guillaumerozier.fr
Mail : guillaume.rozier@telecomnancy.net

README:
This file contains a script that automatically update data. In the morning it update World data, and it updates French data as soon as they are released by Santé publique France.
"""


# In[1]:


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

def try_update_france():
    datetime_spf = get_datetime_spf()
    print("try update, now: "+ str(dt.datetime.now()))
    print("datetime_spf: " + str(datetime_spf))
    
    t1 = dt.datetime.now()
    t2 = datetime_spf
    print("diff t1 t2: {}".format(max(t1, t2) - min(t1, t2)) )
    print("(max(t1, t2) - min(t1, t2)).total_seconds()/3600 = {}".format((max(t1, t2) - min(t1, t2)).total_seconds()/3600) )
    if ( (max(t1, t2) - min(t1, t2)).total_seconds()/3600 <= 2 ): # Si le fichier SPF date d'il y à moins de 2h
        metadata = requests.get(url_metadata)
        content = str(metadata.content)
        
        print("starting France update: {}:{}".format(str(now.hour), str(now.minute)))
        update_repo()
        
        os.chdir(PATH_FRANCE)
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_charts_fastlane.py"])
        push("France fastlane")
        print("update France charts fastlane: " + str(now.hour) + ":" + str(now.minute))
        
        try:
            subprocess.run(["sudo", "python3", PATH_FRANCE+"tweetbot_france.py"])
            print("data tweeted")
        except:
            pass
        
        # Mise à jour des graphiques
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_charts.py"])
        push("France")
        print("update France charts: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_map_incid.py"])
        push("France map incid")
        print("update France local: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_data_explorer.py"])
        push("Data Explorer")
        print("update data explorer: " + str(now.hour) + ":" + str(now.minute))
        
        subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_charts_fastlane.py"])
        push("France fastlane")
        print("update France charts fastlane: " + str(now.hour) + ":" + str(now.minute))
        
        try:
            subprocess.run(["sudo", "python3", PATH_FRANCE+"tweetbot_france_maps.py"])
            print("map tweeted")
        except:
            pass
        
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
        
        os.chdir(BASE_CWD)
        
    return datetime_spf

    
### MAIN FUNCTION ###
datetime_spf = get_datetime_spf()
world_update = dt.datetime.now()

k = 1
l = 0
print("will enter loop")

tweet_world_data = False

while True:
    now = dt.datetime.now() 
    if l%100 == 0:
        print("+100 itérations " + str(now))
    l+=1
    
    if (now.hour >= 7) & (now.hour <= 12) & (world_update.day != now.day):
        print("starting world update: {}:{}".format(str(now.hour), str(now.minute)))
        # S'il est 05h05
        
        world_update = now
        
        # mise à jour des graphiques world
        update_repo()
        
        os.chdir(PATH_WORLD)
        subprocess.run(["sudo", "python3", PATH_WORLD+"covid19_world_charts.py"])
        os.chdir(BASE_CWD)
        
        push("World")
        print("update World pushed: " + str(now.hour) + ":" + str(now.minute))
        
        # ... et France (certains en dépendent)
        #subprocess.run(["sudo", "python3", PATH_FRANCE+"covid19_france_charts.py"])
        #push("France")
        #print("update France pushed: " + str(now.hour) + ":" + str(now.minute))
        
        try:
            tweet_world_data = True
        except:
            pass
        
        time.sleep(30)
        
    print(str(now.hour))
    
    if tweet_world_data and (now.hour == 8):
        subprocess.run(["sudo", "python3", PATH_WORLD+"tweetbot_world.py"])
        tweet_world_data = False
        print("world tweet: done")
        
    if ( (now.hour == 19) & (now.minute >= 21) & (now.minute <= 30)): #(((now.hour == 18) & (now.minute >= 58)) or ((now.hour >= 19) & (now.hour<= 20)))
        print("if condition - now: {}, datetimes_spf: {}".format(now, datetime_spf))
        while ( (((now.hour == 18) & (now.minute >= 59)) or ((now.hour >= 19) & (now.minute >= 16) & (now.hour<= 20))) & ( (now - datetime_spf).total_seconds()/3600 > 2.5 ) ):
            print("while loop - now: {}, datetimes_spf: {}".format(now, datetime_spf))            # Si l'heure comprise entre 18h59 et 21h59, ET les données PAS à jour depuis plus de 2h30
            now = dt.datetime.now()
            
            try:
                datetime_spf = try_update_france()
            except:
                print("error update SPF")
            
            time.sleep(20)
            
    else: # S'il n'est pas entre 18h59 et 21h59
        if( (now - datetime_spf).total_seconds()/3600 > 20 ): # S'il s'est écoulé plus de 20h depuis la dernière update
            if (k%10 == 0): #Check 1 fois toutes les 100 sec * 30 (environ 50 min)
                try:
                    if (now.hour != 19):
                        datetime_spf = try_update_france()
                except:
                    print("error update SPF")
            k += 1
            
    time.sleep(120)


# In[5]:


(dt.datetime.now() - get_datetime_spf()).total_seconds()/3600

