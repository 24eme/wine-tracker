#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse


# In[ ]:


dossier_graphes="graphes/"
csv = "data/drm/export_bi_mouvements.csv"
source = "DRM Inter-Rhône"


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
    
    mouvements = mouvements.query("identifiant_declarant == @id_operateur").reset_index()
    #applications des filtres
    mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)
    mouvements['sorties'] = mouvements["type_de_mouvement"].str.lower().str.startswith("sorties/")
    mouvements = mouvements.query("sorties == True")
    mouvements = mouvements.groupby(['campagne','type_de_mouvement'])["volume mouvement"].sum().reset_index()
    mouvements = mouvements.sort_values(by=['campagne']).reset_index()

    #SUR LES 10 dernières années :
    first_campagne = mouvements['campagne'][0][0 : 4]
    last_campagne = mouvements['campagne'][len(mouvements)-1][0 :4]
    limit_start_with = int(last_campagne)-10

    if(int(first_campagne) < limit_start_with):
        #il faut couper le tableau final et prendre seulement les derniers.
        limit_start_with = str(limit_start_with)+"-"+str(limit_start_with+1)
        index_where_slice = mouvements.index[final['campagne'] == limit_start_with].tolist()[0]
        mouvements = (mouvements.iloc[index_where_slice:len(mouvements)-1]).reset_index()


    # CREATION DU GRAPHE
    fig = px.bar(mouvements, x="campagne", y="volume mouvement", color="type_de_mouvement",
                 text_auto=True,
                 title="Evolution de MES sorties de Chais Vrac/Conditionné <br>(en hl, Sources "+source+")")
    fig.update_layout(xaxis_title=None, 
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="#b7e1e5",
                      plot_bgcolor = "white",
                      hovermode = False,
                      yaxis=dict(tickformat=".0f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5)
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    #fig.show()


    fig.write_html(dossier_graphes+id_operateur+"_graphe2bis.html")
    return


# In[ ]:


if(id_operateur):
    create_graph(id_operateur,mouvements)
else :
    for identifiant in mouvements.identifiant_declarant.unique():
        create_graph(identifiant,mouvements)

