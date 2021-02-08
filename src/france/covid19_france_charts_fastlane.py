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


import time

success=False
tries = 0

while not success:
    try:
        data.download_data()
        success=True
    except Exception as e:
        print(e)
        time.sleep(20)
        print('retrying in 20s')
        tries += 1
        
        if tries >= 200:
            success=True
        continue


# In[3]:


suffixe=""
for (date_deb, date_fin) in [("2020-03-18", last_day_plot_dashboard), (dates[-60], last_day_plot)]:
    range_x, name_fig, range_y = [date_deb, date_fin], "cas_journ"+suffixe, [0, df_incid_fra["P"].max()*0.7]
    
    title = "<b>Cas positifs</b> au Covid19"

    #fig = go.Figure()
    for i in ("", "log"):
        if i=="log":
            title += " [log.]"
            range_y=[0, math.log(df_incid_fra["P"].max())/2]

        fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[""], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}]])

        df_incid_france_cas_rolling = df_incid_fra["P"].rolling(window=7, center=True).mean()#df_incid_france["P"].rolling(window=7, center=True).mean()
        df_incid_france_tests_rolling = df_incid_fra["T"].rolling(window=7, center=True).mean()

        fig.add_trace(go.Scatter(
            x = df_incid_fra["jour"],
            y = df_incid_france_cas_rolling,
            name = "Cas positifs (moyenne 7 j.)",
            marker_color='rgb(8, 115, 191)',
            line_width=8,
            opacity=0.8,
            fill='tozeroy',
            fillcolor="rgba(8, 115, 191, 0.3)",
            showlegend=True
        ), secondary_y=True)

        fig.add_trace(go.Bar(
            x = df_incid_fra["jour"],
            y = df_incid_france_tests_rolling,
            name = "Tests réalisés",
            marker_color='rgba(0, 0, 0, 0.2)',
            opacity=0.8,
            showlegend=True,

        ), secondary_y=False)

        """fig.add_shape(type="line",
        x0="2020-03-17", y0=0, x1="2020-03-17", y1=300000,
        line=dict(color="Red",width=0.5, dash="dot")
        )

        fig.add_shape(type="line",
        x0="2020-05-11", y0=0, x1="2020-05-11", y1=30000000,
        line=dict(color="Green",width=0.5, dash="dot")
        )

        fig.add_shape(type="line",
        x0="2020-10-30", y0=0, x1="2020-10-30", y1=30000000,
        line=dict(color="Red",width=0.5, dash="dot")
        )

        fig.add_shape(type="line",
        x0="2020-11-28", y0=0, x1="2020-11-28", y1=30000000,
        line=dict(color="Orange",width=0.5, dash="dot")
        )
        fig.add_shape(type="line",
        x0="2020-12-15", y0=0, x1="2020-12-15", y1=30000000,
        line=dict(color="green",width=0.5, dash="dot")
        )
        """

        fig.add_shape(type="line",
        x0="2019-12-15", y0=5000, x1="2021-12-15", y1=5000,
        line=dict(color="green",width=2, dash="dot"), xref='x1', yref='y2'
        )

        

        try:
            nope
            model = make_pipeline(PolynomialFeatures(2), Ridge())
            model.fit(df_incid_fra["jour"][-10:-4].index.values.reshape(-1, 1), df_incid_france_cas_rolling[-10:-4].fillna(method="bfill"))

            index_max = df_incid_fra["jour"].index.max()
            x_pred = np.array([x for x in range(index_max-4, index_max+3)]).reshape(-1, 1)

            date_deb = (datetime.strptime(max(df_incid_france["jour"]), '%Y-%m-%d') - timedelta(days=4))
            x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(x_pred))]

            y_plot = model.predict(x_pred)

            fig.add_trace(go.Scatter(
                x = x_pred_dates,
                y = y_plot,
                name = "pred",
                marker_color='rgba(8, 115, 191, 0.2)',
                line_width=5,
                opacity=0.8,
                mode="lines",
                #fill='tozeroy',
                #fillcolor="orange",
                showlegend=False
            ), secondary_y=True)

        except:
            pass

        fig.add_trace(go.Scatter(
            x = [dates_incid[-4]],
            y = [df_incid_france_cas_rolling.values[-4]],
            name = "",
            mode="markers",
            marker_color='rgba(255, 255, 255, 0.6)',
            marker_size=16,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x = [dates_incid[-4]],
            y = [df_incid_france_cas_rolling.values[-4]],
            name = "",
            mode="markers",
            marker_color='rgb(8, 115, 191)',
            marker_size=11,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        ###
        if i=="log":
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13), type="log", secondary_y=True)
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13), type="log", secondary_y=False)
        else:
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13, color="rgba(8, 115, 191, 1)"), secondary_y=True,)
            fig.update_yaxes(zerolinecolor='blue', tickfont=dict(size=13, color="Grey"), secondary_y=False)

        fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=16), range=range_x)

        # Here we modify the tickangle of the xaxis, resulting in rotated labels.
        fig.update_layout(
            bargap=0,
            margin=dict(
                    l=50,
                    r=0,
                    b=0,
                    t=70,
                    pad=10
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
                        size=30),
            xaxis=dict(
                    title='',
                    tickformat='%d/%m'),

            annotations = [
                        dict(
                            x=0.5,
                            y=0.99,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                         )

        croissance = math.trunc(round(((df_incid_france_cas_rolling.values[-4]-df_incid_france_cas_rolling.values[-4-7]) / df_incid_france_cas_rolling.values[-4-7])*100))
        if croissance >= 0:
            croissance="+"+str(abs(croissance))
            
        croissance_tests = math.trunc(round(((df_incid_france_tests_rolling.values[-4]-df_incid_france_tests_rolling.values[-4-7]) / df_incid_france_tests_rolling.values[-4-7])*100))
        if croissance_tests >= 0:
            croissance_tests="+"+str(abs(croissance_tests))

        if i=="log":
            y=math.log(df_incid_france_cas_rolling.values[-4])
        else:
            y=df_incid_france_cas_rolling.values[-4]
            
        ax=-400
        ax2=-400
        if(suffixe=="_recent"):
            ax=-100
            ax2=0
            
        fig['layout']['annotations'] += (dict(
                x = dates_incid[-4], y = y, # annotation point
                xref='x1', 
                yref='y2',
                text=" <b>{} {}".format('%d' % df_incid_france_cas_rolling.values[-4], "cas quotidiens<br></b>en moyenne du {} au {}.<br> {} % en 7 jours".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="rgb(8, 115, 191)",
                    size=20
                    ),
                opacity=1,
                ax=ax,
                ay=-100,
                arrowcolor="rgb(8, 115, 191)",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
            ),
              dict(
                x = dates_incid[-4], y = df_incid_france_tests_rolling.values[-4], # annotation point
                xref='x1', 
                yref='y1',
                text=" <b>{} {}".format('%d' % df_incid_france_tests_rolling.values[-4], "tests quotidiens<br></b>en moyenne du {} au {}.<br> {} % en 7 jours".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'), croissance_tests)),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="grey",
                    size=12
                    ),
                opacity=1,
                ax=ax2,
                ay=-100,
                arrowcolor="grey",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
            ),
              dict(
                x = dates_incid[-1], y = 5000, # annotation point
                xref='x1', 
                yref='y2',
                text="Objectif",
                xshift=0,
                yshift=0,
                xanchor="left",
                yanchor="top",
                align='center',
                font=dict(
                    color="green",
                    size=10
                    ),
                opacity=1,
                ax=0,
                ay=0,
                showarrow=False
            ),
                dict(
                x = "2020-10-30", y = 65000, # annotation point
                xref='x1', 
                yref='y2',
                text="Confinement",
                xanchor="left",
                yanchor="top",
                align='center',
                font=dict(
                    color="red",
                    size=8
                    ),
                showarrow=False
            ),
             dict(
                x=0.5,
                y=-0.1,
                font=dict(size=10),
                xref='paper',
                yref='paper',
                text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                showarrow=False
                        ))

        fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

        plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
        print("> " + name_fig)
        if show_charts:
            fig.show()
        suffixe="_recent"


# In[ ]:



    

range_x, name_fig, range_y = ["2020-03-10", last_day_plot], "cas_journ_croissance", [-50, 150]
title = "<b>Croissance des cas positifs</b> au Covid19"

fig = go.Figure()

df_incid_france_cas_rolling = df_incid_france["P"].rolling(window=7, center=True).mean()
df_incid_france_cas_rolling = (df_incid_france_cas_rolling-df_incid_france_cas_rolling.shift(7))/df_incid_france_cas_rolling.shift(7)*100

fig.add_trace(go.Bar(
    x = df_incid_france["jour"],
    y = df_incid_france_cas_rolling,
    name = "",
    marker_color='rgb(8, 115, 191)',
    #line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    showlegend=False
))

###

fig.update_yaxes(zerolinecolor='Grey', range=[-50, 300], tickfont=dict(size=18))
fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    bargap=0,
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
                size=30),
    xaxis=dict(
            title='',
            tickformat='%d/%m'),

    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),
                ]
                 )

croissance = math.trunc(((df_incid_france_cas_rolling.values[-4]-df_incid_france_cas_rolling.values[-4-7]) / df_incid_france_cas_rolling.values[-4-7])*100)

fig['layout']['annotations'] += (dict(
        x = dates_incid[-4], y = df_incid_france_cas_rolling.values[-4], # annotation point
        xref='x1', 
        yref='y1',
        text=" <b>{}% {}".format('%d' % df_incid_france_cas_rolling.values[-4], "de croissance<br>hebdomadaire"),
        xshift=-2,
        yshift=10,
        xanchor="center",
        align='center',
        font=dict(
            color="rgb(8, 115, 191)",
            size=20
            ),
        opacity=1,
        ax=-130,
        ay=-10,
        arrowcolor="rgb(8, 115, 191)",
        arrowsize=1.5,
        arrowwidth=1,
        arrowhead=0,
        showarrow=True
    ),)

fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()

