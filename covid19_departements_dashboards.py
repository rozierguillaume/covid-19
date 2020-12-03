#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""

LICENSE MIT
2020
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
import plotly.graph_objects as go
import france_data_management as data
from datetime import datetime
from datetime import timedelta
import plotly
import math
import os


# In[3]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[4]:


#df = df.groupby(["dep", "jour"]).first().reset_index()


# In[5]:


df_departements = df.groupby(["jour", "departmentName"]).sum().reset_index()
df_incid_departements = df_incid[df_incid["cl_age90"]==0].groupby(["jour", "departmentName"]).sum().reset_index()

df_new_departements = df_new.groupby(["jour", "departmentName"]).sum().reset_index()

departements = list(dict.fromkeys(list(df_departements['departmentName'].values))) 

dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 
last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")

departements_nb = list(dict.fromkeys(list(df_tests_viros['dep'].values))) 


# In[6]:


lits_reas = pd.read_csv('data/france/lits_rea.csv', sep=",")

df_departements_lits = df_departements.merge(lits_reas, left_on="departmentName", right_on="nom_dpt")


# In[7]:


def cas_journ(departement):
        
    df_incid_dep = df_incid_departements[df_incid_departements["departmentName"] == departement]
    df_incid_dep_rolling = df_incid_dep["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "cas_journ_"+departement, [0, df_incid_dep["P"].max()]
    title = "<b>Cas positifs</b> au Covid19 - <b>" + departement + "</b>"

    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"],
        y = df_incid_dep_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='rgb(8, 115, 191)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates_incid[-4]],
        y = [df_incid_dep_rolling.values[-4]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"],
        y = df_incid_dep["P"],
        name = "",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates_incid[-4], y = df_incid_dep_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_incid_dep_rolling.values[-4], "cas quotidiens<br></b>en moyenne du {} au {}.".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=1,
            ax=-40,
            ay=-70,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)


# In[8]:


def hosp_journ(departement):   
    df_dep = df_departements[df_departements["departmentName"] == departement]
    #df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "hosp_journ_"+departement
    title = "Personnes <b>hospitalisées</b> pour Covid19 - <b>" + departement +"</b>"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = df_dep["jour"],
        y = df_dep["hosp"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(209, 102, 21)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_dep["hosp"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(209, 102, 21)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_dep["hosp"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_dep["hosp"].values[-1], "personnes<br>hospitalisées</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)


# In[9]:


def hosp_comparaison_vagues(departement):   
    df_dep = df_departements[df_departements["departmentName"] == departement]
    #df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "hosp_comp_vagues_"+departement
    title = ""#"<b>Personnes hospitalisées</b> pour Covid19 - " + departement

    fig = go.Figure()
    
    premiere_vague = df_dep[ df_dep["jour"] < "2020-08"]["hosp"].max()
    premiere_vague_date = df_dep[ df_dep["hosp"] == premiere_vague]["jour"].min()
    
    deuxieme_vague = df_dep[ df_dep["jour"] > "2020-09"]["hosp"].max()
    deuxieme_vague_date = df_dep[ (df_dep["hosp"] == deuxieme_vague) & (df_dep["jour"] > "2020-09")]["jour"].min()
    
    color_deuxieme_vague = "green"
    if deuxieme_vague > premiere_vague:
        color_deuxieme_vague = "red"
    
    hosp_values = df_dep["hosp"].values
    trace_to_add = [max(0, hosp - premiere_vague) for hosp in hosp_values]
    
    
    #deuxieme_vague += [df_dep[ df_dep["jour"] > "2020-09"]["hosp"].max()]
    color = ["red" if hosp > premiere_vague else "rgb(209, 102, 21)" for hosp in df_dep["hosp"].values]
    fig.add_trace(go.Bar(
        x = df_dep["jour"],
        y = df_dep["hosp"].values - trace_to_add,
        name = "Nouveaux décès hosp.",
        marker_color="orange",
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    fig.add_trace(go.Bar(
        x = df_dep["jour"],
        y = trace_to_add,
        name = "Nouveaux décès hosp.",
        marker_color="red",
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    fig.add_shape(
            type="line",
            x0="2000-01-01",
            y0=premiere_vague,
            x1="2030-01-01",
            y1=premiere_vague,
            opacity=1,
            #fillcolor="orange",
            line=dict(
                dash="dash",
                color="black",
                width=1,
            )
        )

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18),  range=["2020-03-15", last_day_plot])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,1)',
        bargap=0,
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='stack',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=-0.08,
                        xref='paper',
                        yref='paper',
                        text="Date : {}. Source : Santé publique France. Auteur : Guillaume Rozier - covidtracker.fr - nombre d'hospitalisations".format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = deuxieme_vague_date, y = deuxieme_vague, # annotation point
            xref='x1', 
            yref='y1',
            text="Deuxième vague",
            xshift=-5,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color=color_deuxieme_vague,
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-150,
            ay=-50,
            arrowcolor=color_deuxieme_vague,
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),dict(
            x = premiere_vague_date, y = premiere_vague, # annotation point
            xref='x1', 
            yref='y1',
            text="Première vague",
            xshift=0,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=0,
            ay=-50,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ))

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=1000, height=700)

    print("> " + name_fig)
    
#hosp_comparaison_vagues("Savoie")


# In[10]:


def rea_journ(departement):
    df_dep = df_departements[df_departements["departmentName"] == departement]
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "rea_journ_" + departement
    title = "Personnes en <b>réanimation</b> pour Covid19 - <b>" + departement + "</b>"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_dep["rea"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(201, 4, 4)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(201, 4, 4,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_dep["rea"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(201, 4, 4)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_dep["rea"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_dep["rea"].values[-1], "personnes<br>en réanimation</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    
#rea_journ("Isère")


# In[11]:


def dc_journ(departement): 
    df_dep = df_new_departements[df_new_departements["departmentName"] == departement]
    dc_new_rolling = df_dep["incid_dc"].rolling(window=7).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "dc_journ_"+departement, [0, df_dep["incid_dc"].max()]
    title = "Décès <b>hospitaliers quotidiens</b> du Covid19 - <b>" + departement + "</b>"

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x = df_dep["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(0,0,0,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [dc_new_rolling.values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    #
    fig.add_trace(go.Scatter(
        x = df_dep["jour"],
        y = df_dep["incid_dc"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1.07,
                        xref='paper',
                        yref='paper',
                         font=dict(size=14),
                        text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = dc_new_rolling.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % math.trunc(round(dc_new_rolling.values[-1], 2)), "décès quotidiens</b><br>en moyenne<br>du {} au {}.".format(datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    
#dc_journ("Paris")


# In[12]:



def saturation_rea_journ(dep):
    df_dep = df_departements_lits[df_departements_lits["departmentName"] == dep]
    df_saturation = 100 * df_dep["rea"] / df_dep["LITS_y"]
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "saturation_rea_journ_"+dep, [0, df_saturation.max()]
    title = "<b>Occupation des réa.</b> par les patients Covid19 - " + dep

    fig = go.Figure()

    colors_sat = ["green" if val < 40 else "red" if val > 80  else "orange" for val in df_saturation.values]
    fig.add_trace(go.Bar(
        x = df_dep["jour"],
        y = df_saturation,
        name = "Saturation",
        marker_color=colors_sat,
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(8, 115, 191, 0.3)",
        showlegend=False
    ))

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_saturation.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_saturation.values[-1], " %</b> des lits de réa. occupés par<br>des patients Covid19 le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color=colors_sat[-1],
                size=20
                ),
            opacity=1,
            ax=-70,
            ay=-70,
            arrowcolor=colors_sat[-1],
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)


# In[13]:


import cv2

for dep in departements:
    cas_journ(dep)
    hosp_journ(dep)
    rea_journ(dep)
    dc_journ(dep)
    hosp_comparaison_vagues(dep)
    saturation_rea_journ(dep)
    
    im1 = cv2.imread('images/charts/france/departements_dashboards/cas_journ_{}.jpeg'.format(dep))
    im2 = cv2.imread('images/charts/france/departements_dashboards/hosp_journ_{}.jpeg'.format(dep))
    im3 = cv2.imread('images/charts/france/departements_dashboards/rea_journ_{}.jpeg'.format(dep))
    im4 = cv2.imread('images/charts/france/departements_dashboards/dc_journ_{}.jpeg'.format(dep))

    im_haut = cv2.hconcat([im1, im2])
    #cv2.imwrite('images/charts/france/tests_combinaison.jpeg', im_h)
    im_bas = cv2.hconcat([im3, im4])

    im_totale = cv2.vconcat([im_haut, im_bas])
    cv2.imwrite('images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg'.format(dep), im_totale)
    
    os.remove('images/charts/france/departements_dashboards/cas_journ_{}.jpeg'.format(dep))
    #os.remove('images/charts/france/departements_dashboards/hosp_journ_{}.jpeg'.format(dep))
    os.remove('images/charts/france/departements_dashboards/rea_journ_{}.jpeg'.format(dep))
    os.remove('images/charts/france/departements_dashboards/dc_journ_{}.jpeg'.format(dep))


# In[14]:


for dep in departements:
    saturation_rea_journ(dep)


# In[15]:


"""for idx,dep in enumerate(departements):
    numero_dep = df[df["departmentName"] == dep]["dep"].values[-1]
    
    heading = "<!-- wp:heading --><h2 id=\"{}\">{}</h2><!-- /wp:heading -->\n".format(dep, dep + " (" + numero_dep + ")")
    string = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg\" width=\"75%\"> </a></p>\n".format(dep, dep)
    string2 = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/heatmaps_deps/heatmap_taux_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/heatmaps_deps/heatmap_taux_{}.jpeg\" width=\"60%\"> </a></p>\n".format(numero_dep, numero_dep)
    string_saturation = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/saturation_rea_journ_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/saturation_rea_journ_{}.jpeg\" width=\"60%\"> </a></p>\n".format(dep, dep)
    space = "<!-- wp:spacer {\"height\":50} --><div style=\"height:50px\" aria-hidden=\"true\" class=\"wp-block-spacer\"></div><!-- /wp:spacer -->"
    retourmenu="<a href=\"#Menu\">Retour au menu</a>"
    print(space+retourmenu+heading+string+string2+string_saturation)
"""


# In[16]:


"""#print("<!-- wp:buttons --><div class=\"wp-block-buttons\">\n")
output = ""
for dep in departements:
    numero_dep = df[df["departmentName"] == dep]["dep"].values[-1]
    output+= "<a href=\"#{}\">{} ({})</a> • ".format(dep, dep, numero_dep)
#print(output[:-2])

"""
#print("<!-- /wp:buttons -->")

