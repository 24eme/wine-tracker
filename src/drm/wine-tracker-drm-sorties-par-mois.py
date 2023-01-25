#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse


# In[ ]:


dossier_graphes = "graphes/"
csv = "data/drm/export_bi_mouvements.csv"
source = "DRM Inter-Rhône"

mois = { "08" : "Août" , "09" : "Septembre", "10" : "Octobre", "11" : "Novembre" , "12" : "Décembre",
        "01" : "Janvier", "02" : "Février", "03" : "Mars", "04" : "Avril", "05" : "Mai", "06" : "Juin",
        "07" : "Juillet" }


# In[ ]:


#arguments
id_operateur=None

parser = argparse.ArgumentParser()
parser.add_argument("id_operateur", help="Identifiant opérateur", default=id_operateur, nargs='?')

try:
   args = parser.parse_args()
   id_operateur = args.id_operateur
except:
   print("Arguments pas défaut")


# In[ ]:


#préparations des données de l'opérateur sans filtres
mouvements = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False)
mouvements["volume mouvement"] = mouvements["volume mouvement"]*(-1)
mouvements.rename(columns = {'identifiant declarant':'identifiant_declarant'}, inplace = True)


# In[ ]:


def create_graph(id_operateur,mouvements):
    mouvements['sorties'] = mouvements["type de mouvement"].str.lower().str.startswith("sorties/")
    sorties = mouvements.query("sorties == True")

    sorties = sorties.groupby(['campagne', 'periode'])['volume mouvement'].sum().reset_index()
    sorties['mois'] = sorties["periode"].str.extract('.*(\d{2})', expand = False)
    sorties['mois'] = sorties['mois'].map(mois,na_action=None)

    sorties = sorties.sort_values(by=['mois','campagne'])

    # CREATION DU GRAPHE
    fig = px.histogram(sorties, x="mois", y="volume mouvement",
                 color='campagne', barmode='group',
                 height=500)
    fig.update_layout(xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="#b7e1e5",
                      plot_bgcolor = "white",
                      yaxis=dict(tickformat=".f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5)
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    #fig.show()

    # GRAPHE DANS UN FICHIER HTML
    fig.write_html(dossier_graphes+id_operateur+"_graphe3.html")
    return


# In[ ]:


if(id_operateur):
    create_graph(id_operateur,mouvements)
else :
    for identifiant in mouvements.identifiant_declarant.unique():
        create_graph(identifiant,mouvements)

