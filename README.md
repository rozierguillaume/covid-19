# CovidTracker [data and charts]
In this repository, you'll find many charts and data about the Coronavirus (COVID-19) disease, especially in Europe. Most of the data comes from the [CSSE](https://systems.jhu.edu) (Johns Hopkins Center for Systems Science and Engineering), but I also add some of my own to keep it up-to-date.

French data comes from [INSEE](https://insee.fr/fr/accueil) (Institut National des Statistiques et des Études Économiques) and [Santé Publique France](https://www.santepubliquefrance.fr).

For more information and comments in French, follow me on Twitter: [@guillaumerozier](http://twitter.com/guillaumerozier).

# [CovidTracker](http://www.guillaumerozier.fr): Covid19 Dashboard
**This dashboard contains many detailed graphs, comments and articles about France and the World! 
Check it out now: [CovidTracker (covidtracker.fr)](http://www.covidtracker.fr)!**

<a href="http://www.guillaumerozier.fr"><p align="center" ><img width="70%" src="images/covidtracker.svg"></p></a>

# Website sources
You can find the sources of some of CovidTracker's webpages here: [covidtracker-tools](https://github.com/rozierguillaume/covidtracker-tools).

# Requirements
Refer to the imports in each Jupyter Notebook. Nothing crazy.\
The main requirements are: Python3, Plotly, Orca, Pandas, requests, imageio, json... (all of them can be installed through `pip3`)

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
└───server -> scripts that update data
|
└───data  ->  datasets from CSSE, WHO, INSEE, and more.
│   │   total_cases_csse.csv  ->  CSV file containing total confirmed cases from CSSE.
│   │   total_deaths_csse.csv  ->  CSV file containing total deaths from CSSE.
│   │   total_cases_perso.csv  ->  my own data containing latest confirmed cases (to update charts earlier).
|   |   total_deaths_perso.csv  ->  my own data containing latest deaths (to update charts earlier).
|   |   data_confirmed.csv  ->  exported cases dataset after merging other datasets.
|   |   data_deaths.csv  ->  exported deaths dataset after merging other datasets.
|   |   info_countries.json  ->  information about countries (e.g. population).
|   |   Please ignore everything else
│   
└───images
    └───charts  ->  world charts (linear axis).
        |
        |   * Lots of charts! *
        |
        └───logy_axis  ->  world charts (log axis).
        |
        |   * Exactly the same charts, but with a log y axis *
        |
        └───france  ->  french charts.
            |
            |  * Lot of charts and gifs! * 
            |
        
```



# Data Sources
You can find 2 datasets:
- Data downloaded from [CSSE](https://github.com/CSSEGISandData/COVID-19). Data comes from WHO (World Health Organization),
- [INSEE](https://insee.fr/fr/accueil) (Institut National des Statistiques et des Études Économiques),
- [Santé Publique France](https://www.santepubliquefrance.fr),
- Personal data (added manually).


If you have any questions or feedback please tell me by email or on Twitter.

# LICENSE
License MIT. Please see [LICENSE.md](https://github.com/rozierguillaume/covid-19/blob/master/LICENSE)

[![HitCount](http://hits.dwyl.com/rozierguillaume/covid-19.svg)](http://hits.dwyl.com/rozierguillaume/covid-19)
since 03/04/2020
