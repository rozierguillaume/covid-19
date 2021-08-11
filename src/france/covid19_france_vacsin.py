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


# In[50]:


import pandas as pd
import numpy as np
import cv2
import plotly.graph_objects as go
import france_data_management as data
import plotly
PATH = '../../'
from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


# In[3]:


data.download_data()
data.download_data_hosp_fra_clage()


# In[4]:


df_ameli = pd.read_csv("https://datavaccin-covid.ameli.fr/explore/dataset/donnees-vaccination-par-tranche-dage-type-de-vaccin-et-departement/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")


# In[5]:


df_ameli_filtre = df_ameli[df_ameli["classe_age"]=="TOUT_AGE"]
df_ameli_filtre = df_ameli_filtre[df_ameli_filtre["date"]==df_ameli_filtre["date"].max()]
df_ameli_filtre = df_ameli_filtre[df_ameli_filtre["libelle_departement"] != "FRANCE"]
df_ameli_filtre = df_ameli_filtre[df_ameli_filtre["type_vaccin"] == "Tout vaccin"]


# In[6]:


df_a_vacsi_a_france = data.import_data_vacsi_a_fra()
df_hosp_fra_clage = data.import_data_hosp_fra_clage()
clage_spf = pd.read_csv(PATH+"data/france/clage_spf.csv", sep=";")
#df_a_vacsi_a_france = df_a_vacsi_a_france.merge(clage_spf, left_on="clage_vacsi", right_on="code_spf")


# In[20]:


df_new = data.import_data_new()


# In[7]:


df_tests_viros = data.import_data_tests_viros()
df_tests_viros = df_tests_viros[df_tests_viros["cl_age90"] == 0]
#df_tests_viros["taux_incid"] = df_tests_viros["P"].rolling(window=7).sum()
#df_tests_viros = df_tests_viros[df_tests_viros["jour"] == df_tests_viros["jour"].max()]
df_tests_viros


# In[29]:


df_new_dep


# In[127]:


from sklearn import datasets, linear_model

fig = go.Figure()

xes = []
yes = []
for dep in df_ameli_filtre["departement_residence"]:
    if dep in df_tests_viros["dep"].values:
        
        df_tests_viros_dep = df_tests_viros[df_tests_viros["dep"] == dep]
        df_tests_viros_dep["taux_incid"] = df_tests_viros_dep["P"].rolling(window=7).sum() / df_tests_viros_dep["pop"] * 100000
        
        df_new_dep = df_new[df_new["dep"] == dep]
        df_new_dep["incid_dc"] = df_new_dep["incid_dc"].rolling(window=7).sum() / df_tests_viros_dep["pop"].values[-1] * 100000

        #yes.append(df_new_dep["incid_hosp"].values[-1])
        yes.append(df_new_dep["incid_dc"].values[-1])

        #xes.append(df_tests_viros_dep["taux_incid"].values[-10])
        xes.append(df_ameli_filtre[df_ameli_filtre["departement_residence"]==dep]["taux_cumu_1_inj"].values[-1]*100)

        fig.add_trace(go.Scatter(
            y=[yes[-1]],
            x=[xes[-1]], #[df_tests_viros_dep["taux_incid"].values[-1]], #
            showlegend=False,
            text=dep,
            line=dict(color="red", width=4)
        ))

# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(np.array(xes).reshape(-1, 1), np.array(yes).reshape(-1, 1))

y_pred = regr.predict(np.array([0, 70]).reshape(-1, 1))

score = regr.score(np.array(xes).reshape(-1, 1), np.array(yes).reshape(-1, 1))
a = regr.coef_[0][0]
b = regr.intercept_[0]

"""fig.add_trace(go.Scatter(
    x=[0, 70],
    y=[y[0] for y in y_pred],
    mode="lines",
    marker_color="black",
    line=dict(dash="dot"),
    opacity=0.5,
    text="Corrélation",
    showlegend=False
))"""


"""fig.add_trace(go.Scatter(
    x=[0, 500],
    y=[0, 50],
    mode="lines",
    marker_color="red",
    line=dict(dash="dot"),
    opacity=0.5,
    text="Corrélation",
    showlegend=False
))

fig.add_trace(go.Scatter(
    x=[0, 500],
    y=[0, 25],
    mode="lines",
    marker_color="orange",
    line=dict(dash="dot"),
    opacity=0.5,
    text="Corrélation",
    showlegend=False
))

fig.add_trace(go.Scatter(
    x=[0, 500],
    y=[0, 12,5],
    mode="lines",
    marker_color="green",
    line=dict(dash="dot"),
    opacity=0.5,
    text="Corrélation",
    showlegend=False
))"""

        
fig.update_layout(
    title=dict(
        y=0.92, x=0.5,
        font = dict(
                size=20, color="black"),
        text="Admissions à l'hôpital en fonction de la couverture vaccinale"),
    xaxis=dict(
        title="<b>Taux de vaccination</b> (au moins une dose)",
        ticksuffix=" %"
    ),
    yaxis=dict(
        title="<b>Admissions à l'hôpital</b> pour 100k hab.",
        ticksuffix=""
    ),

    annotations = [
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    font=dict(color="black"),
                    text='Par département de résidence. Date : {}. Données : Améli - Santé publique France. Auteur : @guillaumerozier covidtracker.fr.'.format("02 août", ""),
                    showarrow = False
                )]
)

fig.add_annotation(x=4, y=0.1,
            text="y = {} x + {} ; R2 = {}".format(round(a, 2), round(b, 2), round(score, 2)),
            font=dict(size=8),
            showarrow=False,
            yshift=10)

fig.write_image(PATH + "images/charts/france/cas_vaccination_dep_comp.jpeg", scale=2, width=900, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/cas_vaccination_dep_comp.html', auto_open=False)


# In[ ]:





# In[ ]:





# In[9]:


df_a_vacsi_a_france_80 = df_a_vacsi_a_france[df_a_vacsi_a_france.clage_vacsi==80]
df_hosp_fra_clage_80 = df_hosp_fra_clage[df_hosp_fra_clage.cl_age90 >= 89].groupby(["jour"]).sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_hosp_fra_clage_80.jour,
    y=df_hosp_fra_clage_80.hosp.rolling(window=7).mean(),
    showlegend=False,
    line=dict(color="red", width=4)
))

fig.add_trace(go.Scatter(
    x=df_a_vacsi_a_france_80.jour,
    y=df_a_vacsi_a_france_80.n_cum_complet/4156974*100,
    line=dict(width=4, color="#1f77b4"),
    showlegend=False,
    yaxis="y2"
))

fig.update_layout(
    title=dict(
        y=0.90, x=0.5,
        font = dict(
                size=20, color="black"),
        text="<b>[+ de 80 ans] <span style='color:red;'>personnes hospitalisées</span> et <span style='color:#1f77b4;'>vaccinées</span></b>"),
    
    yaxis=dict(
        title="<b>Personnes hospitalisées</b>",
        titlefont=dict(
            color="red"
        ),
        tickfont=dict(
            color="red"
        )
    ),
    yaxis2=dict(
            range=[0, 100],
            title="<b>% vaccinés</b> (2 doses)",
            titlefont=dict(
                color="#1f77b4"
            ),
            ticksuffix=" %",
            tickfont=dict(
                color="#1f77b4"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=1
        ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    font=dict(color="black"),
                    text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier covidtracker.fr.'.format(datetime.strptime(max(df_hosp_fra_clage_80.jour), '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)
fig.write_image(PATH + "images/charts/france/hosp_vacsi_p80.jpeg", scale=2, width=800, height=500)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/dc_vacsi_p80.html', auto_open=False)


# In[10]:


df_a_vacsi_a_france_80 = df_a_vacsi_a_france[df_a_vacsi_a_france.clage_vacsi!=80].groupby(["jour"]).sum().reset_index()
df_hosp_fra_clage_80 = df_hosp_fra_clage[df_hosp_fra_clage.cl_age90 < 89].groupby(["jour"]).sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_hosp_fra_clage_80.jour,
    y=df_hosp_fra_clage_80.hosp.rolling(window=7).mean(),
    showlegend=False,
    line=dict(color="red", width=4)
))

fig.add_trace(go.Scatter(
    x=df_a_vacsi_a_france_80.jour,
    y=df_a_vacsi_a_france_80.n_cum_complet/(66990000-4156974)*100,
    line=dict(width=4, color="#1f77b4"),
    showlegend=False,
    yaxis="y2"
))

fig.update_layout(
    title=dict(
        y=0.90, x=0.5,
        font = dict(
                size=20, color="black"),
        text="<b>[0 - 79 ans] <span style='color:red;'>personnes hospitalisées</span> et <span style='color:#1f77b4;'>vaccinées</span></b>"),
    
    yaxis=dict(
        title="<b>Personnes hospitalisées</b>",
        titlefont=dict(
            color="red"
        ),
        tickfont=dict(
            color="red"
        )
    ),
    yaxis2=dict(
            range=[0, 100],
            title="<b>% vaccinés</b> (2 doses)",
            titlefont=dict(
                color="#1f77b4"
            ),
            ticksuffix=" %",
            tickfont=dict(
                color="#1f77b4"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=1
        ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    font=dict(color="black"),
                    text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier covidtracker.fr.'.format(datetime.strptime(max(df_hosp_fra_clage_80.jour), '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)
fig.write_image(PATH + "images/charts/france/hosp_vacsi_m80.jpeg", scale=2, width=800, height=500)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/dc_vacsi_m80.html', auto_open=False)


# In[11]:


df_a_vacsi_a_france_80 = df_a_vacsi_a_france[df_a_vacsi_a_france.clage_vacsi==80]
df_hosp_fra_clage_80 = df_hosp_fra_clage[df_hosp_fra_clage.cl_age90 >= 89].groupby(["jour"]).sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_hosp_fra_clage_80.jour,
    y=df_hosp_fra_clage_80.dc.diff().rolling(window=7).mean(),
    showlegend=False,
    line=dict(color="red", width=4)
))

fig.add_trace(go.Scatter(
    x=df_a_vacsi_a_france_80.jour,
    y=df_a_vacsi_a_france_80.n_cum_dose1/4156974*100,
    line=dict(width=4, color="#1f77b4"),
    showlegend=False,
    yaxis="y2"
))

fig.update_layout(
    title=dict(
        y=0.90, x=0.5,
        font = dict(
                size=20, color="black"),
        text="<b>[+ de 80 ans] <span style='color:red;'>décès hospitaliers</span> et <span style='color:#1f77b4;'>vaccinations</span></b>"),
    
    yaxis=dict(
        title="<b>Décès hospitaliers</b>",
        titlefont=dict(
            color="red"
        ),
        tickfont=dict(
            color="red"
        )
    ),
    yaxis2=dict(
            range=[0, 100],
            title="<b>% vaccinés</b> (au moins 1 dose)",
            titlefont=dict(
                color="#1f77b4"
            ),
            ticksuffix=" %",
            tickfont=dict(
                color="#1f77b4"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=1
        ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    font=dict(color="black"),
                    text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier covidtracker.fr.'.format(datetime.strptime(max(df_hosp_fra_clage_80.jour), '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)
fig.write_image(PATH + "images/charts/france/dc_vacsi_p80.jpeg", scale=2, width=800, height=500)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/dc_vacsi_p80.html', auto_open=False)


# In[12]:


df_a_vacsi_a_france_80 = df_a_vacsi_a_france[df_a_vacsi_a_france.clage_vacsi!=80].groupby(["jour"]).sum().reset_index()
df_hosp_fra_clage_80 = df_hosp_fra_clage[df_hosp_fra_clage.cl_age90 < 89].groupby(["jour"]).sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_hosp_fra_clage_80.jour,
    y=df_hosp_fra_clage_80.dc.diff().rolling(window=7).mean(),
    showlegend=False,
    line=dict(color="red", width=4)
))

fig.add_trace(go.Scatter(
    x=df_a_vacsi_a_france_80.jour,
    y=df_a_vacsi_a_france_80.n_cum_dose1/(66990000-4156974)*100,
    line=dict(width=4, color="#1f77b4"),
    showlegend=False,
    yaxis="y2"
))

fig.update_layout(
    title=dict(
        y=0.90, x=0.5,
        font = dict(
                size=20, color="black"),
        text="<b>[0 - 79 ans] <span style='color:red;'>décès hospitaliers</span> et <span style='color:#1f77b4;'>vaccinations</span></b>"),
    
    yaxis=dict(
        title="<b>Décès hospitaliers</b>",
        titlefont=dict(
            color="red"
        ),
        tickfont=dict(
            color="red"
        )
    ),
    yaxis2=dict(
            range=[0, 100],
            title="<b>% vaccinés</b> (au moins 1 dose)",
            titlefont=dict(
                color="#1f77b4"
            ),
            ticksuffix=" %",
            tickfont=dict(
                color="#1f77b4"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=1
        ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    font=dict(color="black"),
                    text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier covidtracker.fr.'.format(datetime.strptime(max(df_hosp_fra_clage_80.jour), '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)
fig.write_image(PATH + "images/charts/france/dc_vacsi_m80.jpeg", scale=2, width=800, height=500)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/dc_vacsi_m80.html', auto_open=False)


# In[13]:


df_a_vacsi_a_france_80 = df_a_vacsi_a_france[df_a_vacsi_a_france.clage_vacsi!=80].groupby(["jour"]).sum().reset_index()
df_hosp_fra_clage_80 = df_hosp_fra_clage[df_hosp_fra_clage.cl_age90 < 89].groupby(["jour"]).sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_hosp_fra_clage_80.jour,
    y=df_hosp_fra_clage_80.dc.diff().rolling(window=7).mean(),
    showlegend=False,
    line=dict(color="red", width=4)
))


df_a_vacsi_a_france_80 = df_a_vacsi_a_france[df_a_vacsi_a_france.clage_vacsi==80]
df_hosp_fra_clage_80 = df_hosp_fra_clage[df_hosp_fra_clage.cl_age90 >= 89].groupby(["jour"]).sum().reset_index()

fig.add_trace(go.Scatter(
    x=df_hosp_fra_clage_80.jour,
    y=df_hosp_fra_clage_80.dc.diff().rolling(window=7).mean(),
    showlegend=False,
    line=dict(color="#1f77b4", width=4)
))

fig.update_layout(
    title=dict(
        y=0.90, x=0.5,
        font = dict(
                size=20, color="black"),
        text="<b>Décès hospitaliers des <span style='color:#1f77b4;'>+ de 80 ans</span> et des <span style='color:red;'>- de 80 ans</span></b>"),
    
    yaxis=dict(
        title="<b>Décès hospitaliers</b>",
        titlefont=dict(
            color="red"
        ),
        tickfont=dict(
            color="red"
        )
    ),
    yaxis2=dict(
            range=[0, 100],
            title="<b>% vaccinés</b> (au moins 1 dose)",
            titlefont=dict(
                color="#1f77b4"
            ),
            ticksuffix=" %",
            tickfont=dict(
                color="#1f77b4"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=1
        ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.07,
                    xref='paper',
                    yref='paper',
                    font=dict(color="black"),
                    text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier covidtracker.fr.'.format(datetime.strptime(max(df_hosp_fra_clage_80.jour), '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)
fig.write_image(PATH + "images/charts/france/dc_vacsi_m80.jpeg", scale=2, width=800, height=500)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/dc_vacsi_m80_p80.html', auto_open=False)


# In[14]:


def dc_hosp_clage(df_hosp_fra_clage, lastday="", minday=""):    
    #lastday = df_hosp_fra_clage.jour.max()
    #lastday="2020-09-01"
    df_hosp_fra_clage_lastday = df_hosp_fra_clage[df_hosp_fra_clage.jour == lastday]
    df_hosp_fra_clage_minday = df_hosp_fra_clage[df_hosp_fra_clage.jour == minday]
    sum_hosp = df_hosp_fra_clage_lastday["hosp"].sum()

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=[str(age-9) + " - " + str(age) +" ans" for age in df_hosp_fra_clage_lastday["cl_age90"].values[:-1]] + ["+ 90 ans"],
        x=df_hosp_fra_clage_minday["hosp"]/df_hosp_fra_clage_minday["hosp"].sum()*100,
        marker_color='rgba(0,0,0,0)',
        marker_line_width=2,
        marker_line_color="black",
        orientation='h',
        name=minday,
        showlegend=False
    ))
    x=df_hosp_fra_clage_lastday["hosp"]/sum_hosp*100
    fig.add_trace(go.Bar(
        y=[str(age-9) + " - " + str(age) +" ans" for age in df_hosp_fra_clage_lastday["cl_age90"].values[:-1]] + ["+ 90 ans"],
        x=x,
        orientation='h',
        marker_line_width=1.5,
        marker_color="red",
        marker_line_color="red",
        text=[str(int(val)) + " %" for val in round(x)],
        textposition='auto',
        name=lastday
    ))
    value_90 = int(round((df_hosp_fra_clage_lastday["hosp"]/sum_hosp*100).values[-1]))
    
    fig.add_trace(go.Bar(
        y=[str(age-9) + " - " + str(age) +" ans" for age in df_hosp_fra_clage_lastday["cl_age90"].values[:-1]] + ["+ 90 ans"],
        x=df_hosp_fra_clage_minday["hosp"]/df_hosp_fra_clage_minday["hosp"].sum()*100,
        marker_color='rgba(0,0,0,0)',
        marker_line_width=2,
        marker_line_color="black",
        orientation='h',
        name=minday
    ))
    
    fig.update_layout(
        annotations=[
                    dict(
                        x=0.5,
                        y=1.12,
                        xref='paper',
                        yref='paper',
                        font=dict(size=11),
                        text="Lecture : les plus de 90 ans représentent {}% des personnes hospitalisées".format(value_90),
                        showarrow=False
                    ),
        ],
        legend_orientation="h",
        barmode='overlay',
        xaxis=dict(ticksuffix=" %"),
        title=dict(
            text="Part de chaque tranche d'âge dans les hospitalisations".format(lastday),
            x=0.5
        ),
        bargap=0.2
    )
    
    fig.write_image(PATH + "images/charts/france/dc_hosp_clage/{}.jpeg".format(lastday), scale=2, width=500, height=500)


# In[15]:


def vacsi_clage(df_a_vacsi_a_france, lastday=""):
    #lastday = df_a_vacsi_a_france.jour.max()
    #lastday="2020-09-01"
    df_a_vacsi_a_france_lastday = df_a_vacsi_a_france[df_a_vacsi_a_france.jour == lastday].sort_values(["clage_vacsi"])
    sum_hosp = df_a_vacsi_a_france_lastday["n_cum_dose1"].sum()

    fig = go.Figure()
    x=df_a_vacsi_a_france_lastday["couv_dose1"]
    fig.add_trace(go.Bar(
        y=df_a_vacsi_a_france_lastday.clage_vacsi_text,
        x=x,
        text=[str(int(val)) + " %" for val in round(x)],
        textposition='auto',
        orientation='h',
    ))
    value_80 = int(round((x.values[-1])))
    fig.update_layout(
         annotations=[
                    dict(
                        x=0.5,
                        y=1.12,
                        xref='paper',
                        yref='paper',
                        font=dict(size=11),
                        text="Lecture : {}% des plus de 80 ans ont reçu une dose de vaccin".format(value_80),
                        showarrow=False
                    ),
        ],
        title=dict(
            text="Couverture vaccinale {}".format(lastday),
            x=0.5
        ),
        xaxis=dict(range=[0, 100], ticksuffix=" %"),
        bargap=0
    )
    fig.write_image(PATH + "images/charts/france/vacsi_clage/{}.jpeg".format(lastday), scale=2, width=500, height=500)


# In[16]:


def assemble_images(date):
    #Assemble images
    
    import numpy as np
    PATH = "../../"

    im1 = cv2.imread(PATH+'images/charts/france/vacsi_clage/{}.jpeg'.format(date))
    im2 = cv2.imread(PATH+'images/charts/france/dc_hosp_clage/{}.jpeg'.format(date))

    im_h = cv2.hconcat([im1, im2])
    cv2.imwrite(PATH+'images/charts/france/vacsi_hosp_comp/{}.jpeg'.format(date), im_h)


# In[17]:


def build_video(dates):
        #import glob
    for (folder, fps) in [("vacsi_hosp_comp", 6),]:
        img_array = []
        for i in range(len(dates)):
            img = cv2.imread((PATH + "images/charts/france/{}/{}.jpeg").format(folder, dates[i]))
            height, width, layers = img.shape
            size = (width,height)
            img_array.append(img)

            if i==len(dates)-1:
                for k in range(12):
                    img_array.append(img)

            if i==0:
                for k in range(6):
                    img_array.append(img)

        out = cv2.VideoWriter(PATH + 'images/charts/france/{}.mp4'.format(folder),cv2.VideoWriter_fourcc(*'MP4V'), fps, size)

        for i in range(len(img_array)):
            out.write(img_array[i])

        out.release()

        try:
            import subprocess
            subprocess.run(["ffmpeg", "-y", "-i", PATH + "images/charts/france/{}.mp4".format(folder), PATH + "images/charts/france/{}_opti.mp4".format(folder)])
            subprocess.run(["rm", PATH + "images/charts/france/{}.mp4".format(folder)])

        except:
            print("error conversion h265")


# In[18]:


dict_clage = {
    4:"0 - 4 ans",
    9:"5 - 9 ans",
    11:"10 - 11 ans",
    17:"12 - 17 ans",
    24:"18 - 24 ans",
    29:"25 - 29 ans",
    39:"30 - 39 ans",
    49:"40 - 49 ans",
    59:"50 - 59 ans",
    69:"60 - 69 ans",
    74:"70 - 74 ans",
    79:"75 - 79 ans",
    80:"> 80 ans"
}

df_a_vacsi_a_france["clage_vacsi_text"] = df_a_vacsi_a_france["clage_vacsi"].map(dict_clage)


# In[19]:


days = sorted(df_a_vacsi_a_france.jour.unique()) #[-100:]
for date in days:
    print(date)
    vacsi_clage(df_a_vacsi_a_france, date)
    dc_hosp_clage(df_hosp_fra_clage, date, minday=days[0])
    assemble_images(date)
build_video(days)


# In[ ]:




