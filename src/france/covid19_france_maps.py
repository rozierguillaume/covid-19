#!/usr/bin/env python
# coding: utf-8

# # COVID-19 French Maps
# Guillaume Rozier, 2020

# In[1]:


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


# In[2]:


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
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


# ## Data import

# In[3]:


# Import data from Santé publique France
df, df_confirmed, dates, _, _, df_deconf, df_sursaud, df_incid, _ = data.import_data()
df_incid = df_incid[df_incid["cl_age90"] == 0]


# In[4]:


#df_incid["incidence"] = df_incid["P"]/df_incid["pop"]*100
#df_incid.loc[:,"incidence_color"] = ["white"] * len(df_incid)
for dep in pd.unique(df_incid["dep"].values):
    df_incid.loc[df_incid["dep"] == dep,"incidence"] = df_incid["P"].rolling(window=7).sum()/df_incid["pop"]*100000
df_incid.loc[:,"incidence_color"] = ['Rouge (>50)' if x >= 50 else 'Orange (25-50)' if x >= 25 else 'Vert (<25)' for x in df_incid['incidence']]


# In[5]:


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


# In[6]:


"""df_insee_france = df_insee.groupby('jour').sum().reset_index()
df_insee_france["surmortalite20"] = (df_insee_france["dc20"] - df_insee_france["moy1819"])/df_insee_france["moy1819"]"""


# <br>
# <br>
# 
# ## Function definition

# In[7]:


with open('data/france/dep.geojson') as response:
    depa = json.load(response)


# In[8]:



def map_gif(dates, imgs_folder, df, type_ppl, legend_title, min_scale, max_scale, colorscale, subtitle):
    try:
        shutil.rmtree(imgs_folder)
    except:
        print("folder not removed")
    os.mkdir(imgs_folder)
    i=1
    
    df = df[df['jour'].isin(dates)]
    
    for date in tqdm(dates):
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
                    text = progressbar,
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
        fig.write_image((imgs_folder+"/{}.jpeg").format(date), scale=1, width=900, height=700)
        
        if date==max(dates):
            fig.write_image((imgs_folder+"/latest.jpeg"), scale=2, width=900, height=700)
            
    return max_scale

def build_gif(file_gif, imgs_folder, dates):
    i=0
    with imageio.get_writer(file_gif, mode='I', duration=0.3) as writer: 
        for date in tqdm(dates):
            print((imgs_folder+"/{}.jpeg").format(date))
            image = imageio.imread((imgs_folder+"/{}.jpeg").format(date))
            writer.append_data(image)
            i+=1
            if i==len(dates):
                for k in range(8):
                    writer.append_data(image)


# In[9]:


#build_map(df_deconf, img_folder="images/charts/france/deconf_synthese/{}.png", title="Départements déconfinés le 11/05")


# In[10]:


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
    


# In[11]:


"""df_sursaud = df_sursaud[df_sursaud["sursaud_cl_age_corona"] == "0"]
df_sursaud_gb = df_sursaud.groupby(["dep", "date_de_passage"]).rolling(window=7).sum().reset_index()

df_sursaud["taux_corona"] = df_sursaud["nbre_pass_corona"]/df_sursaud["nbre_pass_tot"]
df_sursaud["taux_corona"] = df_sursaud["taux_corona"].rolling(window=7).sum()

df_sursaud_gb["taux_corona"] = df_sursaud_gb["nbre_pass_corona"]/df_sursaud_gb["nbre_pass_tot"]
"""
#build_map_indic1(df_sursaud_gb, img_folder="images/charts/france/deconf_indic1/{}.png", title="Indic 1")


# In[12]:


#df_sursaud_gb = df_sursaud.groupby(["dep"]).rolling(window=7, on="date_de_passage").mean().reset_index()
#df_sursaud_gb["date_de_passage"] = df_sursaud["date_de_passage"].values
#df_sursaud_gb[df_sursaud_gb["dep"]=="01"]
#df_sursaud_gb


# <br>
# 
# <br>
# 
# <br>
# 
# <br>
# 
# ## Function calls

# In[13]:


def dep_map():
    # GIF carte nb réanimations par habitant
    imgs_folder = "images/charts/france/dep-map-img"
    sub = 'Nombre de <b>personnes en réanimation</b> <br>par habitant de chaque département.'
    map_gif(dates[-30:], imgs_folder, df = df, type_ppl = "rea_deppop", legend_title="réan./100k hab", min_scale = 0, max_scale=-1, colorscale ="Reds", subtitle=sub)
    build_gif(file_gif = "images/charts/france/dep-map.gif", imgs_folder = "images/charts/france/dep-map-img", dates=dates[-30:])


# In[14]:


def dep_map_dc_cum():
    # GIF carte décès cumulés par habitant
    imgs_folder = "images/charts/france/dep-map-img-dc-cum"
    sub = 'Nombre de <b>décès cumulés</b> <br>par habitant de chaque département.'
    map_gif(dates[-30:], imgs_folder, df = df, type_ppl = "dc_deppop", legend_title="décès/100k hab", min_scale = 0, max_scale=-1, colorscale ="Reds", subtitle=sub)
    build_gif(file_gif = "images/charts/france/dep-map-dc-cum.gif", imgs_folder = "images/charts/france/dep-map-img-dc-cum", dates=dates[-30:])


# In[15]:


def dep_map_dc_journ():
    # GIF carte décès quotidiens 
    imgs_folder = "images/charts/france/dep-map-img-dc-journ"
    sub = 'Nombre de <b>décès quotidien</b> <br>par habitant de chaque département.'
    map_gif(dates[-30:], imgs_folder, df = df, type_ppl = "dc_new_deppop", legend_title="décès/100k hab", min_scale = 0, max_scale=-1, colorscale ="Reds", subtitle=sub)
    build_gif(file_gif = "images/charts/france/dep-map-dc-journ.gif", imgs_folder = "images/charts/france/dep-map-img-dc-journ", dates=dates[-30:])


# In[16]:


def dep_map_incidence():
    # GIF carte décès quotidiens 
    imgs_folder = "images/charts/france/dep-map-incid"
    dates_incid = list(dict.fromkeys(list(df_incid.dropna()['jour'].values)))
    dates_incid.sort()
    
    sub = '<b>Incidence</b> : nombre de cas hebdomadaires <br>pour 100 000 habitants'
    map_gif(dates_incid[-30:], imgs_folder, df = df_incid, type_ppl = "incidence", legend_title="cas sur 7j/100k hab", min_scale = 0, max_scale=-1,                                     colorscale = "Reds", subtitle=sub)
    build_gif(file_gif = "images/charts/france/dep-map-incid.gif", imgs_folder = "images/charts/france/dep-map-incid", dates=dates_incid[-30:])


# In[17]:


dep_map_incidence()
dep_map()
#dep_map_dc_cum()
dep_map_dc_journ()


# In[18]:


"""
# INSEE
# GIF mortalité par rapport à 2018 et 2019
imgs_folder = "images/charts/france/dep-map-surmortalite-img/{}.png"
ppl = "surmortalite20"
sub = 'Comparaison de la <b>mortalité journalière</b> entre 2020 <br>et les deux années précédentes.'
map_gif(dates_insee, imgs_folder, df = df_insee.dropna(), type_ppl = ppl, legend_title="Sur-mortalité (%)", min_scale=-50, max_scale=50, colorscale = ["green", "white", "red"], subtitle = sub)
build_gif(file_gif = "images/charts/france/dep-map-surmortalite.gif", imgs_folder = imgs_folder, dates=dates_insee)"""


# In[19]:


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

