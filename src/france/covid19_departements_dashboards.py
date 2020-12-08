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
import json
PATH = "../../"


# In[3]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[4]:


#df = df.groupby(["dep", "jour"]).first().reset_index()


# In[5]:


df_departements = df.groupby(["jour", "departmentName"]).sum().reset_index()
df_incid_departements = df_incid[df_incid["cl_age90"]==0].groupby(["jour", "departmentName", "dep"]).sum().reset_index()

df_new_departements = df_new.groupby(["jour", "departmentName"]).sum().reset_index()

departements = list(dict.fromkeys(list(df_departements['departmentName'].values))) 

dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 
last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")

departements_nb = list(dict.fromkeys(list(df_tests_viros['dep'].values))) 


# In[6]:


lits_reas = pd.read_csv(PATH+'data/france/lits_rea.csv', sep=",")

df_departements_lits = df_departements.merge(lits_reas, left_on="departmentName", right_on="nom_dpt")


# In[43]:


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
            ax=-250,
            ay=-70,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)


# In[88]:


def incid_dep(departement):
        
    df_incid_dep = df_incid_departements[df_incid_departements["departmentName"] == departement]
    df_incid_dep_rolling = df_incid_dep["P"].rolling(window=7, center=True).sum()/df_incid_dep["pop"] * 100000
    dep_nb = df_incid_dep["dep"].values[0]
    
    range_x, name_fig, range_y = ["2020-09-29", last_day_plot], "incid_"+departement, [0, df_incid_dep_rolling.max()]
    title = "<b>" + departement + " (" + dep_nb + ")" + "</b>"

    fig = go.Figure()
    
    fig.add_shape(type="line",
    x0="2019-03-17", y0=50, x1="2021-03-17", y1=50,
        line=dict(color="Red",width=1.5, dash="dot")
    )
    
    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"][:len(df_incid_dep["jour"])-13],
        y = df_incid_dep_rolling[:len(df_incid_dep_rolling)-13],
        name = "",
        marker_color='rgb(8, 115, 191)',
        line_width=0.5,
        mode="lines",
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.2)",
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_incid_dep["jour"][len(df_incid_dep["jour"])-14:],
        y = df_incid_dep_rolling[len(df_incid_dep_rolling)-14:],
        name = "",
        marker_color='rgb(8, 115, 191)',
        mode="lines",
        line_width=2,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.4)",
        showlegend=False
    ))


    fig.add_trace(go.Scatter(
        x = [dates_incid[-4]],
        y = [df_incid_dep_rolling.values[-4]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        marker_size=30,
        opacity=1,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), visible=False)
    fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
                    size=50),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

    
                     )

    fig['layout']['annotations'] += (dict(
            x = dates_incid[-4], y = df_incid_dep_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_incid_dep_rolling.values[-4], "".format()),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=50
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=1,
            ax=-40,
            ay=-50,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)
    
    incid_j0 = df_incid_dep_rolling.dropna().values[-1]
    incid_j7 = df_incid_dep_rolling.dropna().values[-8]
    
    if incid_j0 > 50:
        if (incid_j0 - incid_j7) < 0:
            class_dep = "higher_low"
        else:
            class_dep = "higher_high"   
    else:
        if (incid_j0 - incid_j7) < 0:
            class_dep = "lower_low"
        else:
            class_dep = "lower_high" 
            
    folder = "covidep/"+class_dep
    
    fig.write_image(PATH+"images/charts/france/{}/{}.svg".format(folder, name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    
    return class_dep
#incid_dep("Savoie")
    


# In[44]:


def hosp_journ(departement):   
    df_dep = df_departements[df_departements["departmentName"] == departement]
    df_new_dep = df_new_departements[df_new_departements["departmentName"] == departement]
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
    
    fig.add_trace(go.Bar(
        x = df_new_dep["jour"],
        y = df_new_dep["incid_hosp"],
        name = "Admissions hosp.",
        marker_color='rgb(209, 102, 21)',
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_dep["jour"],
        y = df_new_dep["incid_hosp"].rolling(window=7).mean(),
        name = "Admissions hosp.",
        marker_color='rgb(209, 102, 21)',
        #mode="lines"
        line_width=2,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
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
            ax=-250,
            ay=-90,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
            dict(
            x = df_new_dep["jour"].values[-1], y = (df_new_dep["incid_hosp"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_dep["incid_hosp"].values[-1], "<br>admissions"),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=10
                ),
            opacity=0.8,
            ax=-20,
            ay=-40,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)


# In[45]:


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

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=1000, height=700)

    print("> " + name_fig)
    
#hosp_comparaison_vagues("Savoie")


# In[46]:


def rea_journ(departement):
    df_dep = df_departements[df_departements["departmentName"] == departement]
    df_new_dep = df_new_departements[df_new_departements["departmentName"] == departement]
    
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
    
    fig.add_trace(go.Bar(
        x = df_new_dep["jour"],
        y = df_new_dep["incid_rea"],
        name = "Admissions",
        marker_color='rgb(201, 4, 4)',
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_dep["jour"],
        y = df_new_dep["incid_rea"].rolling(window=7).mean(),
        name = "Admissions",
        marker_color='rgb(201, 4, 4)',
        marker_size=2,
        opacity=0.8,
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
            ax=-250,
            ay=-90,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
           dict(
            x = df_new_dep["jour"].values[-1], y = (df_new_dep["incid_rea"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_dep["incid_rea"].values[-1], "<br>admissions"),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color='rgb(201, 4, 4)',
                size=10
                ),
            opacity=0.8,
            ax=-20,
            ay=-40,
            arrowcolor='rgb(201, 4, 4)',
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    
#rea_journ("Isère")


# In[47]:


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
            ax=-250,
            ay=-90,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)
    
#dc_journ("Paris")


# In[48]:



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
            ax=-250,
            ay=-70,
            arrowcolor=colors_sat[-1],
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=1.5, width=750, height=500)

    print("> " + name_fig)


# In[89]:


import cv2
import shutil

shutil.rmtree(PATH+"images/charts/france/covidep")
os.mkdir(PATH+"images/charts/france/covidep")
os.mkdir(PATH+"images/charts/france/covidep/lower_low")
os.mkdir(PATH+"images/charts/france/covidep/higher_low")
os.mkdir(PATH+"images/charts/france/covidep/lower_high")
os.mkdir(PATH+"images/charts/france/covidep/higher_high")
stats = {"higher_low": [], "higher_high": [], "lower_low": [], "lower_high": [], "update": dates[-1][-2:] + "/" + dates[-1][-5:-3]}

for dep in departements:
    #GOTO
             
    class_dep = incid_dep(dep)
    stats[class_dep] += [dep]
    
    cas_journ(dep)
    hosp_journ(dep)
    rea_journ(dep)
    dc_journ(dep)
    hosp_comparaison_vagues(dep)
    saturation_rea_journ(dep)
    
    im1 = cv2.imread(PATH+'images/charts/france/departements_dashboards/cas_journ_{}.jpeg'.format(dep))
    im2 = cv2.imread(PATH+'images/charts/france/departements_dashboards/hosp_journ_{}.jpeg'.format(dep))
    im3 = cv2.imread(PATH+'images/charts/france/departements_dashboards/rea_journ_{}.jpeg'.format(dep))
    im4 = cv2.imread(PATH+'images/charts/france/departements_dashboards/dc_journ_{}.jpeg'.format(dep))

    im_haut = cv2.hconcat([im1, im2])
    #cv2.imwrite('images/charts/france/tests_combinaison.jpeg', im_h)
    im_bas = cv2.hconcat([im3, im4])

    im_totale = cv2.vconcat([im_haut, im_bas])
    cv2.imwrite(PATH+'images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg'.format(dep), im_totale)
    
    os.remove(PATH+'images/charts/france/departements_dashboards/cas_journ_{}.jpeg'.format(dep))
    #os.remove('images/charts/france/departements_dashboards/hosp_journ_{}.jpeg'.format(dep))
    os.remove(PATH+'images/charts/france/departements_dashboards/rea_journ_{}.jpeg'.format(dep))
    os.remove(PATH+'images/charts/france/departements_dashboards/dc_journ_{}.jpeg'.format(dep))
    
with open(PATH + 'images/charts/france/covidep/stats.json', 'w') as outfile:
    json.dump(stats, outfile)


# In[50]:


for dep in departements:
    saturation_rea_journ(dep)


# In[63]:


n_tot=4
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

for i in range(0, n_tot):
    evol_tests_deps, evol_hosp_deps = [], []

    fig = go.Figure()

    fig.add_shape(type="rect",
            x0=-1000, y0=0, x1=0, y1=1000,
            line=dict(color="orange",width=0.5, dash="dot"), fillcolor="orange", opacity=0.2,
            layer="below"
        )
    fig.add_shape(type="rect",
            x0=0, y0=-1000, x1=1000, y1=0,
            line=dict(color="orange",width=0.5, dash="dot"), fillcolor="orange", opacity=0.2,
            layer="below"
        )

    fig.add_shape(type="rect",
            x0=0, y0=0, x1=1000, y1=1000,
            line=dict(color="Red",width=0.5, dash="dot"), fillcolor="red", opacity=0.2,
            layer="below"
        )

    fig.add_shape(type="rect",
            x0=-1000, y0=-1000, x1=0, y1=0,
            line=dict(color="red",width=0.5, dash="dot"), fillcolor="green", opacity=0.2,
            layer="below"
        )

    deps_vert, deps_orange, deps_rouge = "", "", ""
    nb_vert, nb_orange, nb_rouge = 0, 0, 0
    for dep in departements:
        df_incid_dep = df_incid_departements[df_incid_departements["departmentName"]==dep]
        tests_dep_rolling = df_incid_dep["P"].rolling(window=7).mean().values
        evol_tests_dep = (tests_dep_rolling[-1-i] - tests_dep_rolling[-8-i]) / tests_dep_rolling[-8] * 100
        evol_tests_deps += [evol_tests_dep]

        hosp_dep_rolling = df_new_departements[df_new_departements["departmentName"]==dep]["incid_hosp"].rolling(window=7).mean().values
        evol_hosp_dep = ( hosp_dep_rolling[-1-i] - hosp_dep_rolling[-8-i]) / hosp_dep_rolling[-8] * 100
        evol_hosp_deps += [evol_hosp_dep]

        if (evol_tests_dep < 0) & (evol_hosp_dep<0):
            color = "green"
            deps_vert += df_incid_dep["dep"].values[0] + ", "
            nb_vert += 1

        elif (evol_tests_dep > 0) & (evol_hosp_dep > 0):
            color = "red"
            deps_rouge += df_incid_dep["dep"].values[0] + ", "
            nb_rouge += 1

        else:
            color = "orange"
            deps_orange += df_incid_dep["dep"].values[0] + ", "
            nb_orange += 1

        fig.add_trace(go.Scatter(
            x = [evol_tests_dep],
            y = [evol_hosp_dep],
            name = dep,
            text=[df_incid_dep["dep"].values[0]],
            marker_color=color,
            marker_size=20,
            line_width=8,
            opacity=0.8,
            fill='tozeroy',
            mode='markers+text',
            fillcolor="rgba(8, 115, 191, 0.3)",
            textfont_color="white",
            showlegend=False,
            textposition="middle center"
        ))

    liste_deps_str = "{} en <b>vert</b> : {}<br><br>{} en <b>orange</b> : {}<br><br>{} en <b>rouge</b> : {}".format(nb_vert, deps_vert, nb_orange, deps_orange, nb_rouge, deps_rouge)

    fig['layout']['annotations'] += (dict(
            x = 50, y = 50, # annotation point
            xref='x1', yref='y1',
            text="Les cas augmentent.<br>Les admissions à l'hôpital augmentent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = -50, y = -50, # annotation point
            xref='x1', yref='y1',
            text="Les cas baissent.<br>Les admissions à l'hôpital baissent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = -50, y = 50, # annotation point
            xref='x1', yref='y1',
            text="Les cas baissent.<br>Les admissions à l'hôpital augmentent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = 50, y = -50, # annotation point
            xref='x1', yref='y1',
            text="Les cas augmentent.<br>Les admissions à l'hôpital baissent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
                x=0.5,
                y=1.05,
                xref='paper',
                yref='paper',
                font=dict(size=14),
                text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                        ),
            dict(
                x=-0.08,
                y=-0.3,
                xref='paper',
                yref='paper',
                font=dict(size=14),
                align="left",
                text=liste_deps_str[:160]+"<br>"+liste_deps_str[161:], showarrow = False
          ),)

    fig.update_xaxes(title="Évolution hebdomadaire des cas positifs", range=[-200, 200], ticksuffix="%")
    fig.update_yaxes(title="Évolution hedbomadaire des admissions à l'hôpital", range=[-200, 200], ticksuffix="%")
    fig.update_layout(
         title={
                        'text': "<b>Évolution des cas et hospitalisations dans les départements</b> • {}".format(datetime.strptime(dates[-i-1], '%Y-%m-%d').strftime('%d %b')),
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
        titlefont = dict(
                    size=20),
        margin=dict(
            b=200
        ),
        )
    fig.write_image(PATH+"images/charts/france/evolution_deps/{}_{}.jpeg".format("evolution_deps", i), scale=3, width=1000, height=900)


# In[52]:


"""#import glob
import cv2
for (folder, n, fps) in [("evolution_deps", n_tot, 3)]:
    img_array = []
    for i in range(n-1, 0-1, -1):
        print(i)
        img = cv2.imread((PATH + "images/charts/france/{}/evolution_deps_{}.jpeg").format(folder, i))
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)

        if i==-n:
            for k in range(4):
                img_array.append(img)

        if i==-1:
            for k in range(12):
                img_array.append(img)

    out = cv2.VideoWriter(PATH + 'images/charts/france/{}/evolution_deps.mp4'.format(folder),cv2.VideoWriter_fourcc(*'MP4V'), fps, size)

    for i in range(len(img_array)):
        out.write(img_array[i])

    out.release()
    
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-i", PATH + "images/charts/france/{}/evolution_deps.mp4".format(folder), PATH + "images/charts/france/{}/evolution_deps_opti.mp4".format(folder)])
        subprocess.run(["rm", PATH + "images/charts/france/{}/evolution_deps.mp4".format(folder)])   
    except:
        print("error conversion h265")"""


# In[53]:


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


# In[54]:


"""#print("<!-- wp:buttons --><div class=\"wp-block-buttons\">\n")
output = ""
for dep in departements:
    numero_dep = df[df["departmentName"] == dep]["dep"].values[-1]
    output+= "<a href=\"#{}\">{} ({})</a> • ".format(dep, dep, numero_dep)
#print(output[:-2])

"""
#print("<!-- /wp:buttons -->")

