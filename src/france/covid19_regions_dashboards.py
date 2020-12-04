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


# In[1]:


import pandas as pd
import plotly.graph_objects as go
import france_data_management as data
from datetime import datetime
from datetime import timedelta
import plotly
import math
import os
PATH = "../../"


# In[2]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[3]:


df_regions = df.groupby(["jour", "regionName"]).sum().reset_index()
df_incid_regions = df_incid[df_incid["cl_age90"] == 0].groupby(["jour", "regionName"]).sum().reset_index()
regions = list(dict.fromkeys(list(df_regions['regionName'].values))) 
dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 
last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")

df_new_regions = df_new.groupby(["jour", "regionName"]).sum().reset_index()


# In[4]:


lits_reas = pd.read_csv(PATH+'data/france/lits_rea.csv', sep=",")


# In[5]:


regions_deps = df.groupby(["departmentName", "regionName"]).sum().reset_index().loc[:,["departmentName", "regionName"]]
lits_reas = lits_reas.merge(regions_deps, left_on="nom_dpt", right_on="departmentName").drop(["nom_dpt"], axis=1)
lits_reas_regs = lits_reas.groupby(["regionName"]).sum().reset_index()
df_regions = df_regions.merge(lits_reas_regs, left_on="regionName", right_on="regionName")


# In[6]:


def cas_journ(region):
        
    df_incid_reg = df_incid_regions[df_incid_regions["regionName"] == region]
    df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "cas_journ_"+region, [0, df_incid_reg["P"].max()]
    title = "<b>Cas positifs</b> au Covid19 - <b>" + region + "</b>"

    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x = df_incid_reg["jour"],
        y = df_incid_reg_rolling,
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
        y = [df_incid_reg_rolling.values[-4]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x = df_incid_reg["jour"],
        y = df_incid_reg["P"],
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
                    'y':0.93,
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
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates_incid[-4], y = df_incid_reg_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_incid_reg_rolling.values[-4], "cas quotidiens<br></b>en moyenne du {} au {}.".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=20
                ),
            opacity=1,
            ax=-40,
            ay=-70,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1, width=900, height=600)

    print("> " + name_fig)


# In[7]:


def hosp_journ(region):   
    df_reg = df_regions[df_regions["regionName"] == region]
    #df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "hosp_journ_"+region
    title = "<b>Personnes hospitalisées</b> pour Covid19 - <b>" + region + "</b>"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = df_reg["jour"],
        y = df_reg["hosp"],
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
        y = [df_reg["hosp"].values[-1]],
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
                    'y':0.93,
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
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_reg["hosp"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_reg["hosp"].values[-1], "personnes<br>hospitalisées</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=20
                ),
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1, width=900, height=600)

    print("> " + name_fig)


# In[8]:


def rea_journ(region):
    df_reg = df_regions[df_regions["regionName"] == region]
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "rea_journ_" + region
    title = "Personnes en <b>réanimation</b> pour Covid19 - <b>" + region + "</b>"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_reg["rea"],
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
        y = [df_reg["rea"].values[-1]],
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
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.93,
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
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_reg["rea"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_reg["rea"].values[-1], "personnes<br>en réanimation</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=20
                ),
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1, width=900, height=600)

    print("> " + name_fig)
#rea_journ("Auvergne-Rhône-Alpes")


# In[9]:


def dc_journ(region): 
    df_reg = df_new_regions[df_new_regions["regionName"] == region]
    dc_new_rolling = df_reg["incid_dc"].rolling(window=7).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "dc_journ_"+region, [0, df_reg["incid_dc"].max()]
    title = "<b>Décès hospitaliers quotidiens</b> du Covid19 - <b>" + region + "</b>"

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x = df_reg["jour"],
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
        x = df_reg["jour"],
        y = df_reg["incid_dc"],
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
                    'y':0.93,
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
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
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
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1, width=900, height=600)

    print("> " + name_fig)


# In[10]:



def saturation_rea_journ(region):
    df_reg = df_regions[df_regions["regionName"] == region]
    df_saturation = 100 * df_reg["rea"] / df_reg["LITS_y"]
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "saturation_rea_journ_"+region, [0, df_saturation.max()*1.2]
    title = "<b>Occupation des réa.</b> par les patients Covid19 - <b>" + region + "</b>"

    fig = go.Figure()

    colors_sat = ["green" if val < 60 else "red" if val > 100  else "orange" for val in df_saturation.values]
    fig.add_trace(go.Bar(
        x = dates,
        y = df_saturation,
        name = "Nouveaux décès hosp.",
        marker_color=colors_sat,
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_shape(
            type="line",
            x0="2019-03-15",
            y0=100,
            x1="2022-01-01",
            y1=100,
            opacity=1,
            fillcolor="orange",
            line=dict(
                color="red",
                width=1,
            )
        )

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-15", last_day_plot])

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
                    'y':0.93,
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
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
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
            ay=-20,
            arrowcolor=colors_sat[-1],
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1, width=900, height=600)

    print("> " + name_fig)


# In[11]:


import cv2

for reg in regions:
    saturation_rea_journ(reg)
    cas_journ(reg)
    hosp_journ(reg)
    rea_journ(reg)
    dc_journ(reg)
    saturation_rea_journ(reg)
    
    
    im1 = cv2.imread(PATH+'images/charts/france/regions_dashboards/cas_journ_{}.jpeg'.format(reg))
    im2 = cv2.imread(PATH+'images/charts/france/regions_dashboards/hosp_journ_{}.jpeg'.format(reg))
    im3 = cv2.imread(PATH+'images/charts/france/regions_dashboards/rea_journ_{}.jpeg'.format(reg))
    im4 = cv2.imread(PATH+'images/charts/france/regions_dashboards/dc_journ_{}.jpeg'.format(reg))

    im_haut = cv2.hconcat([im1, im2])
    im_bas = cv2.hconcat([im3, im4])

    im_totale = cv2.vconcat([im_haut, im_bas])
    cv2.imwrite(PATH+'images/charts/france/regions_dashboards/dashboard_jour_{}.jpeg'.format(reg), im_totale)
    
    os.remove(PATH+'images/charts/france/regions_dashboards/cas_journ_{}.jpeg'.format(reg))
    os.remove(PATH+'images/charts/france/regions_dashboards/hosp_journ_{}.jpeg'.format(reg))
    os.remove(PATH+'images/charts/france/regions_dashboards/rea_journ_{}.jpeg'.format(reg))
    os.remove(PATH+'images/charts/france/regions_dashboards/dc_journ_{}.jpeg'.format(reg))


# In[13]:


"""for reg in regions:
    
    heading = "<!-- wp:heading --><h2 id=\"{}\">{}</h2><!-- /wp:heading -->\n".format(reg, reg)
    string = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/regions_dashboards/dashboard_jour_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/regions_dashboards/dashboard_jour_{}.jpeg\" width=\"100%\"> </a></p><br>\n".format(reg, reg)
    string2 = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/regions_dashboards/saturation_rea_journ_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/regions_dashboards/saturation_rea_journ_{}.jpeg\" width=\"70%\"> </a></p>\n".format(reg, reg)

    space = "<!-- wp:spacer {\"height\":50} --><div style=\"height:50px\" aria-hidden=\"true\" class=\"wp-block-spacer\"></div><!-- /wp:spacer -->"
    retourmenu="<a href=\"#Menu\">Retour au menu</a>"
    print(space+retourmenu+heading+string+string2)
"""


# In[14]:


"""print("<!-- wp:buttons --><div class=\"wp-block-buttons\">\n")
#for reg in regions:
    print("""#<!-- wp:button {"className":"is-style-outline"} -->
    #<div class="wp-block-button is-style-outline">""")
    
    #print("<a class=\"wp-block-button__link\" href=\"#{}\">".format(reg))
    
    #print("{}</a></div><!-- /wp:button --></div>\n".format(reg))
#print("<!-- /wp:buttons -->")"""

