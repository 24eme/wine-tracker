#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import plotly.express as px
import argparse


# In[ ]:


dossier_graphes="graphes/"
csv = "data/drm/export_bi_drm_stock.csv"  #il manque un ; à la fin du header.
source = "DRM Inter-Rhône"


# In[ ]:


#arguments
id_operateur= None

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
if(id_operateur):
    drm = drm.query("identifiant == @id_operateur").reset_index()


# In[ ]:


# PAR APPELLATION ET COULEUR

#SOMME PRODUCTION #A CHANGER
drm_production = drm.groupby(["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux", "couleurs"]).sum(["entree"])[["entree"]]

#SOMME SORTIES
drm_sortie = drm.groupby(["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux", "couleurs"]).sum(["sortie"])[["sortie"]]

#SOMME STOCK DEBUT DE CAMPAGNE
drm_stock_debut = drm
drm_stock_debut['debut_campagne'] = drm["date"].str.lower().str.endswith("08")
drm_stock_debut = drm_stock_debut.query("debut_campagne == True")
drm_stock_debut = drm_stock_debut.groupby(["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux", "couleurs"]).sum(["stock debut"])[["stock debut"]]

df_final = pd.merge(drm_production, drm_sortie,how='outer', on=["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux", "couleurs"])
df_final = pd.merge(df_final, drm_stock_debut ,how='outer', on=["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux", "couleurs"])

df_final = df_final.reset_index()

df_final['filtre_produit'] = df_final['appellations'] + "/" + df_final['lieux'] + "/" +df_final['certifications']+ "/" +df_final['genres']
df_final.index = [df_final['identifiant'],df_final['filtre_produit'],df_final['couleurs']]
df_final.drop(['certifications', 'genres','appellations','mentions','lieux'], axis=1, inplace=True)
df_final.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','entree' : 'Production (hl)', 'sortie' : 'Sorties de chais (hl)'}, inplace = True)


df_final['filtre'] = "SPE-SPE"

#df_final


# In[ ]:


# PAR COULEUR


drm_production_all_spe = drm_production.groupby(["identifiant","campagne","couleurs"]).sum(["entree"])[["entree"]]
drm_sortie_all_spe = drm_sortie.groupby(["identifiant", "campagne","couleurs"]).sum(["sortie"])[["sortie"]]
drm_stock_debut_all_spe = drm_stock_debut.groupby(["identifiant", "campagne","couleurs"]).sum(["stock debut"])[["stock debut"]]

drm_merge_all_spe = pd.merge(drm_production_all_spe, drm_sortie_all_spe,how='outer', on=["identifiant", "campagne","couleurs"])
drm_merge_all_spe = pd.merge(drm_merge_all_spe, drm_stock_debut_all_spe ,how='outer', on=["identifiant", "campagne","couleurs"])

drm_merge_all_spe = drm_merge_all_spe.reset_index()

drm_merge_all_spe['filtre_produit'] = "TOUT"

drm_merge_all_spe.index = [drm_merge_all_spe['identifiant'],drm_merge_all_spe['filtre_produit'],drm_merge_all_spe['couleurs']]

drm_merge_all_spe.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','entree' : 'Production (hl)', 'sortie' : 'Sorties de chais (hl)'}, inplace = True)

drm_merge_all_spe['filtre'] = "ALL-SPE"

#drm_merge_all_spe


# In[ ]:


# PAR APPELLATIONS

drm_production_spe_all = drm_production.groupby(["identifiant","campagne","certifications", "genres", "appellations", "mentions", "lieux"]).sum(["entree"])[["entree"]]
drm_sortie_spe_all = drm_sortie.groupby(["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux"]).sum(["sortie"])[["sortie"]]
drm_stock_debut_spe_all = drm_stock_debut.groupby(["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux"]).sum(["stock debut"])[["stock debut"]]

drm_merge_spe_all = pd.merge(drm_production_spe_all, drm_sortie_spe_all,how='outer', on=["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux"])
drm_merge_spe_all = pd.merge(drm_merge_spe_all, drm_stock_debut_spe_all ,how='outer', on=["identifiant", "campagne","certifications", "genres", "appellations", "mentions", "lieux"])

drm_merge_spe_all = drm_merge_spe_all.reset_index()

drm_merge_spe_all['filtre_produit'] = drm_merge_spe_all['appellations'] + "/" + drm_merge_spe_all['lieux'] + "/" +drm_merge_spe_all['certifications']+ "/" +drm_merge_spe_all['genres']
drm_merge_spe_all['couleurs'] = "TOUT"

drm_merge_spe_all.index = [drm_merge_spe_all['identifiant'],drm_merge_spe_all['filtre_produit'],drm_merge_spe_all['couleurs']]
drm_merge_spe_all.drop(['certifications', 'genres','appellations','mentions','lieux'], axis=1, inplace=True)


drm_merge_spe_all.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','entree' : 'Production (hl)', 'sortie' : 'Sorties de chais (hl)'}, inplace = True)

drm_merge_spe_all['filtre'] = "SPE-ALL"

#drm_merge_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

drm_production_all_all = drm_production_spe_all.groupby(["identifiant","campagne"]).sum(["entree"])[["entree"]]
drm_sortie_all_all = drm_sortie_spe_all.groupby(["identifiant", "campagne"]).sum(["sortie"])[["sortie"]]
drm_stock_debut_all_all = drm_stock_debut.groupby(["identifiant", "campagne"]).sum(["stock debut"])[["stock debut"]]


drm_merge_all_all = pd.merge(drm_production_all_all, drm_sortie_all_all,how='outer', on=["identifiant", "campagne"])
drm_merge_all_all = pd.merge(drm_merge_all_all, drm_stock_debut_all_all ,how='outer', on=["identifiant", "campagne"])

drm_merge_all_all = drm_merge_all_all.reset_index()

drm_merge_all_all['filtre_produit'] = "TOUT"
drm_merge_all_all['couleurs'] = "TOUT"

drm_merge_all_all.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','entree' : 'Production (hl)', 'sortie' : 'Sorties de chais (hl)'}, inplace = True)
drm_merge_all_all.index = [drm_merge_all_all['identifiant'],drm_merge_all_all['filtre_produit'],drm_merge_all_all['couleurs']]

drm_merge_all_all['filtre'] = "ALL-ALL"

#drm_merge_all_all


# In[ ]:


df_final = pd.concat([df_final, drm_merge_all_spe])

df_final = pd.concat([df_final, drm_merge_spe_all])

df_final = pd.concat([df_final, drm_merge_all_all])

df_final.drop(['identifiant','filtre_produit',"couleurs"], axis=1, inplace=True)

df_final = df_final.sort_values(by=['identifiant', 'filtre_produit','couleurs'])


# In[ ]:


def create_graphique(final,identifiant,appellation,couleur):

    # CREATION DU GRAPHE
    fig = px.line(final, x="campagne", y="value", color='variable', markers=True, symbol="variable",color_discrete_sequence=["blue", "green", "red"],
                  title="Evolution des MES stocks, récoltes et sorties<br>(en hl. Sorties hors replis, hors déclassements, Sources "+source+")")
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="#fff6ad",
                      plot_bgcolor = "white",
                      yaxis=dict(tickformat=".0f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5)
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    #fig.show()
    
    fig.write_html(dossier_graphes+identifiant+"_graphe1_"+appellation+"_"+couleur+".html",include_plotlyjs=False)
    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    df = df.reset_index()
    df = pd.melt(df, id_vars=['identifiant','filtre_produit','couleurs','campagne'], value_vars=['Stock physique en début de camp production (hl)','Production (hl)','Sorties de chais (hl)'])
    appellation = bloc[1].replace("/", "_")
    create_graphique(df,bloc[0],appellation,bloc[2])

