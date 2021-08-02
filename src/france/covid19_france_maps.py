#!/usr/bin/env python
# coding: utf-8

# # COVID-19 French Maps
# Guillaume Rozier, 2020

# In[24]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.guillaumerozier.fr
Mail : guillaume.rozier@telecomnancy.net

README:s
This file contains script that generate France maps and GIFs. 
Single images are exported to folders in 'charts/image/france'. GIFs are exported to 'charts/image/france'.
I'm currently cleaning this file, please ask me is something is not clear enough!
Requirements: please see the imports below (use pip3 to install them).

"""


# In[25]:


import france_data_management as data
import pandas as pd
from tqdm import tqdm
import json
import plotly.express as px
from datetime import datetime
import imageio
import multiprocessing
import locale
import shutil
import os
from datetime import timedelta
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
PATH = "../../"
import subprocess


# ## Data import

# In[26]:


# Import data from Santé publique France
df, df_confirmed, dates, _, _, df_deconf, df_sursaud, df_incid, _ = data.import_data()
df_incid = df_incid[df_incid["cl_age90"] == 0]


# In[27]:


#df_incid["incidence"] = df_incid["P"]/df_incid["pop"]*100
#df_incid.loc[:,"incidence_color"] = ["white"] * len(df_incid)
for dep in pd.unique(df_incid["dep"].values):
    df_incid.loc[df_incid["dep"] == dep,"incidence"] = df_incid["P"].rolling(window=7).sum()/df_incid["pop"]*100000
df_incid.loc[:,"incidence_color"] = ['Rouge (>50)' if x >= 50 else 'Orange (25-50)' if x >= 25 else 'Vert (<25)' for x in df_incid['incidence']]


# In[28]:


"""# Download and import data from INSEE
dict_insee = pd.read_excel('data/france/deces_quotidiens_departement.xlsx', header=[3], index_col=None, sheet_name=None, usecols='A:H', nrows=44)
dict_insee.pop('France')
dict_insee.pop('Documentation')

for key in dict_insee:
    dict_insee[key]["dep"] = [key for i in range(len(dict_insee[key]))]
    
df_insee = pd.concat(dict_insee)
df_insee = df_insee.rename(columns={"Ensemble des communes": "dc20", "Ensemble des communes.1": "dc19", "Ensemble des communes.2": "dc18", "Date d'événement": "jour"})
df_insee = df_insee.drop(columns=['Communes à envoi dématérialisé au 1er avril 2020 (1)', 'Communes à envoi dématérialisé au 1er avril 2020 (1)', 'Communes à envoi dématérialisé au 1er avril 2020 (1)', 'Unnamed: 7'])
df_insee["moy1819"] = (df_insee["dc19"] + df_insee["dc20"])/2
df_insee["surmortalite20"] = (df_insee["dc20"] - df_insee["moy1819"])/df_insee["moy1819"]*100
df_insee['jour'] = pd.to_datetime(df_insee['jour'])
df_insee['jour'] = df_insee['jour'].dt.strftime('%Y-%m-%d')

dates_insee = list(dict.fromkeys(list(df_insee.dropna()['jour'].values))) """


# In[29]:


"""df_insee_france = df_insee.groupby('jour').sum().reset_index()
df_insee_france["surmortalite20"] = (df_insee_france["dc20"] - df_insee_france["moy1819"])/df_insee_france["moy1819"]"""


# <br>
# <br>
# 
# ## Function definition

# In[30]:


with open(PATH+'data/france/dep.geojson') as response:
    depa = json.load(response)


# In[31]:


def map_gif(dates, imgs_folder, df, type_ppl, legend_title, min_scale, max_scale, colorscale, subtitle, clean_before=True, clean_after=False):
    try:
        if(clean_before):
            shutil.rmtree(imgs_folder)
            os.mkdir(imgs_folder)
    except:
        print("folder not removed")
    
    i=1
    
    df = df[df['jour'].isin(dates)]
    files = os.listdir(imgs_folder)
    
    for date in tqdm(dates):
        if "{}.jpeg".format(date) in files:
            print("map already generated", (imgs_folder+"/{}.jpeg").format(date))
            continue
        
        if max_scale == -1:
            max_scale = df[type_ppl].max()
        df_map = pd.melt(df, id_vars=['jour','dep'], value_vars=[type_ppl])
        df_map = df_map[df_map["jour"] == date]

        fig = px.choropleth(geojson=depa, 
                            locations=df_map['dep'], 
                            color=df_map['value'],
                            color_continuous_scale = colorscale,
                            range_color=(min_scale, max_scale),
                            featureidkey="properties.code",
                            scope='europe',
                            labels={'color':legend_title}
                                  )
        date_title = datetime.strptime(date, '%Y-%m-%d').strftime('%d %B')
        
        fig.update_geos(fitbounds="locations", visible=False)
        
        var_hab = 'pour 100k. hab.'
        pourcent = ''
        
        val_mean = round(df_map['value'].mean(), 1)
        
        n = len(dates)
        progression = round((i / n) * 50)
        progressbar = progression * '█' + (50 - progression) * '░'
        i += 1
        
        if type_ppl == 'surmortalite20':
            var_hab = ''
            pourcent = " %"
            if val_mean < 0:
                val_mean = "– " + str(abs(val_mean))
            else:
                val_mean = "+ " + str(val_mean)
                
        val_mean = str(val_mean).replace(".", ",")
        
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            title={
            'text': "{}".format(date_title),
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
            size=30),
            annotations = [
                dict(
                    x=0.54,
                    y=0.08,
                    xref='paper',
                    yref='paper',
                    xanchor = 'center',
                    text='Source : Santé publique France. Auteur : @guillaumerozier - CovidTracker.fr',
                    showarrow = False
                ),
                dict(
                    x=0.54,
                    y=0.03,
                    xref = 'paper',
                    yref = 'paper',
                    text = "", #progressbar,
                    xanchor = 'center',
                    showarrow = False,
                    font=dict(
                        size=9
                            )
                ),
                dict(
                    x=0.07,
                    y=0.47,
                    xref='paper',
                    yref='paper',
                    xanchor='left',
                    text='Moyenne France',
                    showarrow = False,
                    font=dict(
                        size=14
                            )
                ),
                dict(
                    x=0.07,
                    y=0.50,
                    xref='paper',
                    yref='paper',
                    xanchor='left',
                    text='{}{}'.format(val_mean, pourcent),
                    showarrow = False,
                    font=dict(
                        size=25
                            )
                ),
                
                dict(
                    x=0.07,
                    y=0.45,
                    xref='paper',
                    yref='paper',
                    xanchor='left',
                    text = var_hab,
                    showarrow = False,
                    font=dict(
                        size=14
                            )
                ),
                dict(
                    x=0.55,
                    y=0.9,
                    xref='paper',
                    yref='paper',
                    text=subtitle,
                    showarrow = False,
                    font=dict(
                        size=20
                            )
                )]
             ) 
        
        fig.update_geos(
            #center=dict(lon=-30, lat=-30),
            projection_rotation=dict(lon=12, lat=30, roll=8),
            #lataxis_range=[-50,20], lonaxis_range=[0, 200]
        )
        fig.write_image((imgs_folder+"/{}.jpeg").format(date), scale=2, width=900, height=700)
        
        if date==max(dates):
            fig.write_image((imgs_folder+"/latest.jpeg"), scale=2, width=900, height=700)
            
    if clean_after:
        for file in files:
            if file[:-5] < min(dates):
                os.remove(imgs_folder+"/"+file)
        
    return max_scale

def build_gif(file_gif, imgs_folder, dates):
    print(sorted(dates))
    i=0
    with imageio.get_writer(file_gif, mode='I', duration=0.3) as writer: 
        for idx,date in enumerate(dates):
            image = imageio.imread((imgs_folder+"/{}.jpeg").format(date))
            print("appending", date)
            writer.append_data(image)
            i+=1
            
            if idx==len(dates)-1:
                for _ in range(10):
                    image_last = imageio.imread((imgs_folder+"/{}.jpeg").format(date))
                    writer.append_data(image_last)
                    print("appending (last)", date)
                    
    subprocess.run(["gifsicle", "-i", file_gif, "--optimize=1", "--scale=0.6", "--colors=180", "-o", file_gif[:-4]+"_opti.gif"])
    os.remove(file_gif)


# In[32]:


#build_map(df_deconf, img_folder="images/charts/france/deconf_synthese/{}.png", title="Départements déconfinés le 11/05")


# In[33]:


def build_map_indic1(data_df, img_folder, legend_title="legend_title", title="title"):
    dates_deconf = list(dict.fromkeys(list(data_df['date_de_passage'].values))) 
    date = dates_deconf[-1]
    
    data_df = data_df[data_df["date_de_passage"] == date]
    
    fig = px.choropleth(geojson = depa, 
                        locations = data_df['dep'], 
                        featureidkey="properties.code",
                        color = data_df['taux_corona'],
                        scope='europe',
                        range_color=(0, 0.1),
                        #labels={'red':"Couleur", 'orange':'bla', 'green':'lol'},
                        #color_discrete_sequence = ["green", "orange", "red"],
                        #color_discrete_map = {"vert":"green", "orange":"orange", "rouge":"red"}
                        #category_orders = {"indic_synthese" :["vert", "orange", "rouge"]}
                              )
    date_title = datetime.strptime(dates_deconf[-1], '%Y-%m-%d').strftime('%d %B')

    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(
        margin={"r":0,"t":20,"l":0,"b":0},
        title={
            'text': title,
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        
        titlefont = dict(
            size=30),
        
        annotations = [
            dict(
                x=0.54,
                y=0.03,
                xref='paper',
                yref='paper',
                xanchor = 'center',
                text='Source : Ministère de la Santé. Auteur : @guillaumerozier.',
                showarrow = False
            ),

            dict(
                x=0.55,
                y=0.94,
                xref='paper',
                yref='paper',
                text= "Mis à jour le {}".format(date_title),
                showarrow = False,
                font=dict(
                    size=20
                        )
            )]
         ) 

    fig.update_geos(
        #center=dict(lon=-30, lat=-30),
        projection_rotation=dict(lon=12, lat=30, roll=8),
        #lataxis_range=[-50,20], lonaxis_range=[0, 200]
    )
    #fig.show()
    if date == dates_deconf[-1]:
        fig.write_image(img_folder.format("latest"), scale=2, width=1200, height=800)
    fig.write_image(img_folder.format(date), scale=2, width=1200, height=800)
    


# <br>
# 
# <br>
# 
# <br>
# 
# <br>
# 
# ## Function calls

# In[34]:


def dep_map():
    # GIF carte nb réanimations par habitant
    imgs_folder = PATH+"images/charts/france/dep-map-img"
    sub = 'Nombre de <b>personnes en réanimation</b> <br>par habitant de chaque département.'
    map_gif(dates[-30:], imgs_folder, df = df, type_ppl = "rea_deppop", legend_title="réan./100k hab", min_scale = 0, max_scale=23,             colorscale = [[0, "green"], [0.04, "#ffcc66"], [0.6, "#f50000"], [0.8, "#b30000"], [1, "#3d0000"]], subtitle=sub, clean_before=False, clean_after=False)
    build_gif(file_gif = PATH+"images/charts/france/dep-map.gif", imgs_folder = PATH+"images/charts/france/dep-map-img", dates=dates[-30:])
#dep_map()


# In[35]:


def dep_map_dc_cum():
    # GIF carte décès cumulés par habitant
    imgs_folder = PATH+"images/charts/france/dep-map-img-dc-cum"
    sub = 'Nombre de <b>décès cumulés</b> <br>par habitant de chaque département.'
    map_gif(dates[-30:], imgs_folder, df = df, type_ppl = "dc_deppop", legend_title="décès/100k hab", min_scale = 0, max_scale=-1, colorscale ="Reds", subtitle=sub)
    build_gif(file_gif = PATH+"images/charts/france/dep-map-dc-cum.gif", imgs_folder = PATH+"images/charts/france/dep-map-img-dc-cum", dates=dates[-30:])


# In[36]:


def dep_map_dc_journ():
    # GIF carte décès quotidiens 
    imgs_folder = PATH+"images/charts/france/dep-map-img-dc-journ"
    sub = 'Nombre de <b>décès quotidien</b> <br>par habitant de chaque département.'
    map_gif(dates[-30:], imgs_folder, df = df, type_ppl = "dc_new_deppop", legend_title="décès/100k hab", min_scale = 0, max_scale=-1, colorscale ="Reds", subtitle=sub)
    build_gif(file_gif = PATH+"images/charts/france/dep-map-dc-journ.gif", imgs_folder = PATH+"images/charts/france/dep-map-img-dc-journ", dates=dates[-30:])


# In[37]:


def dep_map_incidence():
    # GIF carte décès quotidiens 
    imgs_folder = PATH+"images/charts/france/dep-map-incid"
    dates_incid = sorted(list(dict.fromkeys(list(df_incid.dropna()['jour'].values))))
    
    sub = '<b>Incidence</b> : nombre de cas hebdomadaires <br>pour 100 000 habitants'
    map_gif(dates_incid[-50:], imgs_folder, df = df_incid, type_ppl = "incidence", legend_title="cas sur 7j/100k hab", min_scale = 0, max_scale=800,                                     colorscale = [[0, "green"], [0.08, "#ffcc66"], [0.25, "#f50000"], [0.5, "#b30000"], [1, "#3d0000"]], subtitle=sub, clean_before=False, clean_after=True)
    build_gif(file_gif = PATH+"images/charts/france/dep-map-incid.gif", imgs_folder = PATH+"images/charts/france/dep-map-incid", dates=dates_incid[-50:])

#dep_map_incidence()


# In[38]:


dep_map_incidence()
dep_map()
#dep_map_dc_cum()
dep_map_dc_journ()


# In[39]:


df_incid_departements = df_incid[df_incid["cl_age90"]==0].groupby(["jour", "departmentName", "dep"]).sum().reset_index()
departements = list(dict.fromkeys(list(df_incid_departements['departmentName'].values))) 


# In[40]:


dep = "Savoie"
df_incid_pred = pd.DataFrame()
dates_dataframe, incid_dataframe, dep_dataframe = [], [], []
dict_json={}
import numpy as np

for dep in departements:
    df_dep = df_incid_departements[df_incid_departements["departmentName"] == dep]
    incidence_dep = df_dep["incidence"].values

    taux_incid = []

    for i in range(1, 6):
        try:
            taux_incid += [1+(incidence_dep[-i] - incidence_dep[-1-i])/incidence_dep[-1-i]]

        except Exception as e:
            print("exception")
            taux_incid += [0]

    pred_incid = []
    for i in range(1, 8):
        
        pred_incid += [incidence_dep[-1] * (sum(taux_incid)/len(taux_incid))**i]

    date_deb = (datetime.strptime(max(df_dep["jour"]), '%Y-%m-%d'))
    x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(1, len(pred_incid)+1)]

    ## creation dataframe
    dates_dataframe += x_pred_dates
    incid_dataframe += pred_incid
    dep_dataframe += [dep] * len(x_pred_dates)
    
    ## export json
    dict_json[dep] = {}
    dict_json[dep]["incidence"] = list(np.nan_to_num(incidence_dep[-60:]))
    dict_json[dep]["pred_incidence"] = list(np.nan_to_num(pred_incid))
    
dict_json["dates"] = list(df_dep["jour"].values[-60:]) + x_pred_dates

df_incid_pred["departementName"] = dep_dataframe
df_incid_pred["pred_incidence"] = incid_dataframe
df_incid_pred["jour"] = dates_dataframe


# In[41]:


with open(PATH + 'data/france/stats/pred_dep_incid.json', 'w') as outfile:
    json.dump(dict_json, outfile)


# In[42]:


"""import plotly.graph_objects as go
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_incid_pred[df_incid_pred["departementName"]=="Paris"]["jour"],
    y=df_incid_pred[df_incid_pred["departementName"]=="Paris"]["pred_incidence"] ))

fig.add_trace(go.Scatter(
    x=df_incid_departements[df_incid_departements["departmentName"]=="Paris"]["jour"],
    y=df_incid_departements[df_incid_departements["departmentName"]=="Paris"]["incidence"] ))

fig.show()"""


# In[43]:


"""import plotly.graph_objects as go
from plotly.subplots import make_subplots
temperatures=pd.read_csv(PATH+"data/france/temperature-quotidienne-departementale.csv", sep=";")

fig = make_subplots(specs=[[{"secondary_y": True}]])
dep="Paris"
dep_num = df_incid_departements[df_incid_departements["departmentName"]=="Paris"]["dep"].values[0]

fig.add_trace(go.Scatter(
    x=df_incid_pred[df_incid_pred["departementName"]==dep]["jour"],
    y=df_incid_pred[df_incid_pred["departementName"]==dep]["pred_incidence"] ))

fig.add_trace(go.Scatter(
    x=df_incid_departements[df_incid_departements["departmentName"]==dep]["jour"],
    y=df_incid_departements[df_incid_departements["departmentName"]==dep]["incidence"] ))

fig.add_trace(go.Scatter(
    x=temperatures[temperatures["code_insee_departement"]==dep_num].sort_values(["date_obs"])["date_obs"],
    y=temperatures[temperatures["code_insee_departement"]==dep_num].sort_values(["date_obs"])["tmoy"].rolling(window=14, center=True).mean().shift(10) ), secondary_y=True)
fig.update_xaxes(range=["2020-07-01", "2020-12-18"])
fig.show()"""


# In[44]:


import plotly.graph_objects as go
from plotly.subplots import make_subplots
temperatures=pd.read_csv(PATH+"data/france/temperature-quotidienne-departementale.csv", sep=";")
temperatures_france = temperatures.groupby(["date_obs"]).mean().reset_index()

fig = make_subplots(specs=[[{"secondary_y": True}]])
df_incid_france = df_incid.groupby(["jour"]).sum().reset_index()
fig.add_trace(go.Scatter(
    x=df_incid_france["jour"],
    y=(df_incid_france["P"].rolling(window=7, center=True).mean())/1000,
    name="cas (en milliers)"
))

fig.add_trace(go.Scatter(
    x=df_incid_france["jour"],
    y=((df_incid_france["P"].rolling(window=7, center=True).mean()-df_incid_france["P"].shift(7).rolling(window=7, center=True).mean())/df_incid_france["P"].shift(7).rolling(window=7, center=True).mean()*100 ),
    name="taux croissa hebdo cas"
))
fig.add_trace(go.Scatter(
    x=temperatures_france["date_obs"],
    y=temperatures_france["tmoy"].rolling(window=14, center=True).mean().shift(10),
    name="température<br>moyenne (+10 jours)"), secondary_y=True)
    
fig.update_xaxes(range=["2020-07-01", "2020-12-18"])
fig.update_layout(title="Nombre de cas et des températures")
fig.show()


# In[45]:


"""
# INSEE
# GIF mortalité par rapport à 2018 et 2019
imgs_folder = "images/charts/france/dep-map-surmortalite-img/{}.png"
ppl = "surmortalite20"
sub = 'Comparaison de la <b>mortalité journalière</b> entre 2020 <br>et les deux années précédentes.'
map_gif(dates_insee, imgs_folder, df = df_insee.dropna(), type_ppl = ppl, legend_title="Sur-mortalité (%)", min_scale=-50, max_scale=50, colorscale = ["green", "white", "red"], subtitle = sub)
build_gif(file_gif = "images/charts/france/dep-map-surmortalite.gif", imgs_folder = imgs_folder, dates=dates_insee)"""


# In[46]:


"""# Line chart évolution de la mortalité

import plotly.graph_objects as go
import plotly
fig = go.Figure()

fig.add_trace(go.Scatter(
    x = df_insee_france["jour"],
    y = df_insee_france["surmortalite20"],
    name = "Bilan autre hosp",
    marker_color='black',
    mode="lines+markers",
    opacity=1
))


# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    legend_orientation="v",
    barmode='relative',
    title={
                'text': "Variation de la <b>mortalité en mars 2020</b> par rapport à 2018 et 2019",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis=dict(
        title='',
        tickformat='%d/%m'),
    yaxis_title="Surmortalité (%)",
    
    annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

fig.update_layout(
    yaxis = go.layout.YAxis(
        tickformat = '%'
    ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='',
                    showarrow = False
                )]
                 )

name_fig = "insee_surmortalite"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=2, width=1200, height=800)
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)

fig.show()"""

