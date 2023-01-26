#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse


# In[ ]:


dossier_graphes="graphes/"
csv = "data/drm/export_bi_drm_stock.csv"  #il manque un ; à la fin du header.
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
drm = pd.read_csv(csv, sep=";",encoding="iso8859_15")


# In[ ]:


def create_graph(id_operateur,drm):
    drm = drm.query("identifiant == @id_operateur").reset_index()

    #SOMME STOCK DEBUT DE CAMPAGNE
    stock_physique_debut_campagne = drm
    stock_physique_debut_campagne['debut_campagne'] = stock_physique_debut_campagne["date"].str.lower().str.endswith("08")
    stock_physique_debut_campagne = stock_physique_debut_campagne.query("debut_campagne == True")
    stock_physique_debut_campagne = stock_physique_debut_campagne["stock debut"].groupby(stock_physique_debut_campagne['campagne']).agg('sum').reset_index()


    #SOMME PRODUCTION
    production = drm["entree revendiquee"].groupby(drm['campagne']).agg('sum').reset_index()


    #SOMME SORTIES
    sorties = drm["sortie revendiquee"].groupby(drm['campagne']).agg('sum').reset_index()


    #MERGE
    final = pd.merge(production, sorties,how='outer', on=['campagne'])
    final = pd.merge(final, stock_physique_debut_campagne ,how='outer', on=['campagne'])

    #RENOMMAGE DES COLONNES
    final.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','entree revendiquee' : 'Production (hl)', 'sortie revendiquee' : 'Sorties de chais (hl)'}, inplace = True)

    #FORMATTAGE DU TABLEAU
    final = pd.melt(final, id_vars=['campagne'], value_vars=['Stock physique en début de camp production (hl)','Production (hl)','Sorties de chais (hl)'])
    final.rename(columns = {'value':'volume'}, inplace = True)

    #final.loc[:, "volume"] = final["volume"].map('{:.f}'.format)

    final = final.sort_values(by=['campagne']).reset_index()

    #SUR LES 10 dernières années :
    first_campagne = final['campagne'][0][0 : 4]
    last_campagne = final['campagne'][len(final)-1][0 :4]
    limit_start_with = int(last_campagne)-10

    if(int(first_campagne) < limit_start_with):
        #il faut couper le tableau final et prendre seulement les derniers.
        limit_start_with = str(limit_start_with)+"-"+str(limit_start_with+1)
        index_where_slice = final.index[final['campagne'] == limit_start_with].tolist()[0]
        final = (final.iloc[index_where_slice:len(final)-1]).reset_index()

    # CREATION DU GRAPHE
    fig = px.line(final, x="campagne", y="volume", color='variable', markers=True, symbol="variable",color_discrete_sequence=["blue", "green", "red"],
                  title="Evolution des MES stocks, récoltes et sorties<br>(en hl. Sorties hors replis, hors déclassements, Sources "+source+")")
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="#fff6ad",
                      plot_bgcolor = "white",
                      yaxis=dict(tickformat=".f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5)
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    #fig.show()

    #IL FAUT AJOUTER DES ESPACES DANS POUR LES MILLIERS.

    # GRAPHE DANS UN FICHIER HTML
    fig.write_html(dossier_graphes+id_operateur+"_graphe1.html")
    return


# In[ ]:


if(id_operateur):
    create_graph(id_operateur,drm)
else :
    for identifiant in drm.identifiant.unique():
        create_graph(identifiant,drm)

