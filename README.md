# CovidTracker [data and charts]
You can find on this repository many charts and data about Coronavirus (COVID-19) disease, especially in Europe. Most of data come from [CSSE](https://systems.jhu.edu) (Johns Hopkins Center for Systems Science and Engineering), but I also add data of my own to have up-to-date data.

French data come frome [INSEE](https://insee.fr/fr/accueil) (Institut National des Statistiques et des Études Économiques) and [Santé Publique France](https://www.santepubliquefrance.fr).

For more information and comments in French, you can follow me on Twitter: [@guillaumerozier](http://twitter.com/guillaumerozier).

# [CovidTracker](http://www.guillaumerozier.fr): Covid19 Dashboard
**This dashboard ontains many and detailed graphs, comments and articles about France and the World! 
Check it out now: [CovidTracker (covidtracker.fr)](http://www.covidtracker.fr)!**

<a href="http://www.guillaumerozier.fr"><p align="center" ><img width="70%" src="images/covidtracker.svg"></p></a>

# Website sources
You can find sources of some of the CovidTracker's webpages here: [covidtracker-tools](https://github.com/rozierguillaume/covidtracker-tools).

# Requirements
Please see the imports in each Jupyter Notebook. Nothing crazy.\
Here are the main requirements: Python3, Plotly, Orca, Pandas, requests, imageio, json... (you can install all of them with `pip3`)

# Repository structure

```
covid-19
└─── README.md
|
└───src
    └───france  ->  Jupyter Notebooks and their corresponding .py files generating france charts
    |
    └───world  ->  Jupyter Notebooks and their corresponding .py files generating world charts
|
└───server -> scripts that updates data
|
└───data  ->  datasets from CSSE, WHO, INSEE, and more.
│   │   total_cases_csse.csv  ->  CSV file containing total confirmed cases from CSSE.
│   │   total_deaths_csse.csv  ->  CSV file containing total deaths from CSSE.
│   │   total_cases_perso.csv  ->  my own data containing latests confirmed cases (to update charts earlier).
|   |   total_deaths_perso.csv  ->  my own data containing latests deaths (to update charts earlier).
|   |   data_confirmed.csv  ->  exported cases dataset after merging other datasets.
|   |   data_deaths.csv  ->  exported deaths dataset after merging other datasets.
|   |   info_countries.json  ->  information about countries (e.g. population).
|   |   Please ignore everything else
│   
└───images
    └───charts  ->  world charts (linear axis).
        |
        |   * Lot of charts! *
        |
        └───logy_axis  ->  world charts (log axis).
        |
        |   * Exactly the same charts, but whith a log y axis *
        |
        └───france  ->  french charts.
            |
            |  * Lot of charts and gifs! * 
            |
        
```



# Data Sources
You can find 2 datasets:
- Data downloaded from [CSSE](https://github.com/CSSEGISandData/COVID-19). Data come from WHO (World Health Organization).
- [INSEE](https://insee.fr/fr/accueil) (Institut National des Statistiques et des Études Économiques)
- [Santé Publique France](https://www.santepubliquefrance.fr).
- Personal data (added manually).


If you have any question or feedback please ask me by email or on Twitter.

# LICENSE
License MIT. Please see [LICENSE.md](https://github.com/rozierguillaume/covid-19/blob/master/LICENSE)

[![HitCount](http://hits.dwyl.com/rozierguillaume/covid-19.svg)](http://hits.dwyl.com/rozierguillaume/covid-19)
since 03/04/2020
