#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import plotly.express as px
import argparse
import pathlib


# In[ ]:


path = pathlib.Path().absolute()
path = str(path).replace("src/drm","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/drm/export_bi_drm_stock.csv"  #il manque un ; à la fin du header.
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
drm = pd.read_csv(csv, sep=";",encoding="latin1")

lastcampagnes = drm['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-10:]

if(id_operateur):
    drm = drm.query("identifiant == @id_operateur").reset_index()

drm = drm.query('campagne in @lastcampagnes')


# In[ ]:


#pour les volumes récoltés :

csv_mouvements = path+"/data/drm/export_bi_mouvements.csv"  #il manque un ; à la fin du header.
mouvements = pd.read_csv(csv_mouvements, sep=";",encoding="latin1")

mouvements.rename(columns = {'identifiant declarant':'identifiant','type de mouvement':'type_de_mouvement','certification':'certifications','genre':'genres','appellation':'appellations','mention':'mentions','lieu':'lieux','couleur':'couleurs'}, inplace = True)
mouvements = mouvements.query("type_de_mouvement == 'entrees/recolte'")

if(id_operateur):
    mouvements = mouvements.query("identifiant == @id_operateur").reset_index()

mouvements = mouvements.query('campagne in @lastcampagnes')

mouvements.rename(columns = {'volume mouvement':'entree'}, inplace = True)

#mouvements


# In[ ]:


drm['filtre_produit'] = drm['appellations'] + "-" + drm['lieux'] + "-" +drm['certifications']+ "-" +drm['genres']+ "-" +drm['mentions']
mouvements['filtre_produit'] = mouvements['appellations'] + "-" + mouvements['lieux'] + "-" +mouvements['certifications']+ "-" +mouvements['genres']+ "-" +mouvements['mentions']


# In[ ]:


# PAR APPELLATION ET COULEUR

#SOMME PRODUCTION DEPUIS LES MOUVEMENTS : RECOLTES
drm_production = mouvements.groupby(["identifiant", "campagne","filtre_produit", "couleurs"]).sum(["entree"])[["entree"]]

#SOMME SORTIES
drm_sortie = drm.groupby(["identifiant", "campagne","filtre_produit", "couleurs"]).sum(["sortie"])[["sortie"]]

#SOMME STOCK DEBUT DE CAMPAGNE
drm_stock_debut = drm
drm_stock_debut['debut_campagne'] = drm["date"].str.lower().str.endswith("08")
drm_stock_debut = drm_stock_debut.query("debut_campagne == True")
drm_stock_debut = drm_stock_debut.groupby(["identifiant", "campagne","filtre_produit", "couleurs"]).sum(["stock debut"])[["stock debut"]]

df_final = pd.merge(drm_production, drm_sortie,how='outer', on=["identifiant", "campagne","filtre_produit", "couleurs"])
df_final = pd.merge(df_final, drm_stock_debut ,how='outer', on=["identifiant", "campagne","filtre_produit", "couleurs"])

df_final = df_final.reset_index()

df_final['couleurs'] = df_final['couleurs'].str.upper()

df_final.index = [df_final['identifiant'],df_final['filtre_produit'],df_final['couleurs']]
df_final.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','entree' : 'Production (hl)', 'sortie' : 'Sorties de chais (hl)'}, inplace = True)


#df_final


# In[ ]:


# PAR APPELLATIONS

drm_production_spe_all = drm_production.groupby(["identifiant","campagne","filtre_produit"]).sum(["entree"])[["entree"]]
drm_sortie_spe_all = drm_sortie.groupby(["identifiant", "campagne","filtre_produit"]).sum(["sortie"])[["sortie"]]
drm_stock_debut_spe_all = drm_stock_debut.groupby(["identifiant", "campagne","filtre_produit"]).sum(["stock debut"])[["stock debut"]]

drm_merge_spe_all = pd.merge(drm_production_spe_all, drm_sortie_spe_all,how='outer', on=["identifiant", "campagne","filtre_produit"])
drm_merge_spe_all = pd.merge(drm_merge_spe_all, drm_stock_debut_spe_all ,how='outer', on=["identifiant", "campagne","filtre_produit"])

drm_merge_spe_all = drm_merge_spe_all.reset_index()

drm_merge_spe_all['couleurs'] = "TOUT"

drm_merge_spe_all.index = [drm_merge_spe_all['identifiant'],drm_merge_spe_all['filtre_produit'],drm_merge_spe_all['couleurs']]

drm_merge_spe_all.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','entree' : 'Production (hl)', 'sortie' : 'Sorties de chais (hl)'}, inplace = True)

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

#drm_merge_all_all


# In[ ]:


df_final = pd.concat([df_final, drm_merge_spe_all])

df_final = pd.concat([df_final, drm_merge_all_all])

df_final.drop(['identifiant','filtre_produit',"couleurs"], axis=1, inplace=True)

df_final = df_final.sort_values(by=['identifiant', 'filtre_produit','couleurs'])

df_final = df_final.fillna(0)

#df_final


# In[ ]:


def create_graphique(final,identifiant,appellation,couleur):

    # CREATION DU GRAPHE
    fig = px.line(final, x="campagne", y="value", color='variable', markers=True, symbol="variable",color_discrete_sequence=["blue","green","#d1342f"],
                  title="Ma cave")
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(title={
                        'text': "<b>MA CAVE</b>",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                      title_font_size=24,
                      title_font_color="rgb(231, 80, 71)",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="white",
                      plot_bgcolor = "white",
                      yaxis=dict(tickformat=".0f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5),
                      legend_itemdoubleclick=False
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True,showline=True, linewidth=1, linecolor='Lightgrey')
    fig.update_yaxes(fixedrange=True,rangemode="tozero")

    #fig.show()

    dossier = dossier_graphes+"/"+identifiant+"/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)

    fig.write_html(dossier+"/graphe1.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    df = df.reset_index()

    for campagne in lastcampagnes:
        if campagne not in df.campagne.unique()[::-1] :
            df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne, 0, 0, 0]
    
    df = df.sort_values(by=['campagne'])
    df = df.reset_index(drop=True)
    
    df = pd.melt(df, id_vars=['identifiant','filtre_produit','couleurs','campagne'], value_vars=['Stock physique en début de camp production (hl)','Production (hl)','Sorties de chais (hl)'])
    create_graphique(df,bloc[0],bloc[1],bloc[2])


# In[ ]:




