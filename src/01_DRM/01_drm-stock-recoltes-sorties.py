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
path = str(path).replace("/src","").replace("/01_DRM","")
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
drm = pd.read_csv(csv, sep=";",encoding="iso8859_15",index_col=False)
drm = drm[drm['genres'] != 'VCI']
lastcampagnes = drm['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-10:]

if(id_operateur):
    drm = drm.query("identifiant == @id_operateur").reset_index()

drm = drm.query('campagne in @lastcampagnes')


# In[ ]:


#pour les volumes récoltés :

csv_mouvements = path+"/data/drm/export_bi_mouvements.csv"  #il manque un ; à la fin du header.
mouvements = pd.read_csv(csv_mouvements, sep=";",encoding="iso8859_15",index_col=False)

mouvements.rename(columns = {'identifiant declarant':'identifiant','type de mouvement':'type_de_mouvement','certification':'certifications','genre':'genres','appellation':'appellations','mention':'mentions','lieu':'lieux','couleur':'couleurs'}, inplace = True)

if(id_operateur):
    mouvements = mouvements.query("identifiant == @id_operateur").reset_index()

mouvements = mouvements.query('campagne in @lastcampagnes')
mouvements = mouvements[mouvements['periode'] > '2013-12']
mouvements = mouvements[mouvements['genres'] != 'VCI']
mouvements = mouvements[mouvements['libelle type'] == 'Suspendu']

#mouvements


# In[ ]:


drm['filtre_produit'] = drm['appellations'] + "-" + drm['lieux'] + "-" +drm['certifications']+ "-" +drm['genres']+ "-" +drm['mentions']
mouvements['filtre_produit'] = mouvements['appellations'] + "-" + mouvements['lieux'] + "-" +mouvements['certifications']+ "-" +mouvements['genres']+ "-" +mouvements['mentions']


# In[ ]:


# PAR APPELLATION ET COULEUR

#SOMME RECOLTE DEPUIS LES MOUVEMENTS : RECOLTES
drm_recolte = mouvements.query("type_de_mouvement == 'entrees/recolte'")
drm_recolte = drm_recolte.groupby(["identifiant", "campagne","filtre_produit", "couleurs"]).sum(["volume mouvement"])[["volume mouvement"]]

#SOMME SORTIES
typedemouvementssorties = ['sorties/vrac','sorties/crd', 'sorties/factures', 'sorties/export','sorties/consommation']
drm_sortie = mouvements.query("type_de_mouvement in @typedemouvementssorties").reset_index()
drm_sortie = drm_sortie.groupby(["identifiant", "campagne","filtre_produit", "couleurs"]).sum(["volume mouvement"])[["volume mouvement"]]


#drm_sortie = drm.groupby(["identifiant", "campagne","filtre_produit", "couleurs"]).sum(["sortie"])[["sortie"]]

#SOMME STOCK DEBUT DE CAMPAGNE
drm_stock_debut = drm
drm_stock_debut['debut_campagne'] = drm["date"].str.lower().str.endswith("08")
drm_stock_debut = drm_stock_debut.query("debut_campagne == True")
drm_stock_debut = drm_stock_debut.groupby(["identifiant", "campagne","filtre_produit", "couleurs"]).first(["stock debut"])[["stock debut"]]

df_final = pd.merge(drm_recolte, drm_sortie,how='outer', on=["identifiant", "campagne","filtre_produit", "couleurs"])
df_final = pd.merge(df_final, drm_stock_debut ,how='outer', on=["identifiant", "campagne","filtre_produit", "couleurs"])


drm_stock_sortie = drm.groupby(["identifiant", "campagne","filtre_produit", "couleurs"]).sum(["sortie"])[["sortie"]]
df_final = pd.merge(df_final, drm_stock_sortie, how='outer', on=["identifiant", "campagne","filtre_produit", "couleurs"])

df_final = df_final.reset_index()

df_final['couleurs'] = df_final['couleurs'].str.upper()

df_final.index = [df_final['identifiant'],df_final['filtre_produit'],df_final['couleurs'],df_final['campagne']]
df_final = df_final[['stock debut', 'volume mouvement_x', 'volume mouvement_y', 'sortie']]
df_final.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','volume mouvement_x' : 'Récoltes (hl)', 'volume mouvement_y' : 'Sorties de chais (hl)'}, inplace = True)

#df_final


# In[ ]:


couleur_group = df_final.groupby(["identifiant","campagne","filtre_produit"]).sum(['Récoltes (hl)','Sorties de chais (hl)','Stock physique en début de camp production (hl)','sortie'])
couleur_group['couleurs'] = 'TOUT'

produit_group = couleur_group.groupby(["identifiant","campagne"]).sum(['Récoltes (hl)','Sorties de chais (hl)','Stock physique en début de camp production (hl)','sortie']).reset_index()
produit_group['filtre_produit'] = 'TOUT'
produit_group['couleurs'] = 'TOUT'

df_final = pd.concat([df_final.reset_index(), couleur_group.reset_index(), produit_group.reset_index()], ignore_index=True)
df_final.set_index(['identifiant', 'filtre_produit', 'couleurs'], inplace=True)


# In[ ]:


df_final.fillna(0, inplace=True)
df_final = df_final.round({'Récoltes (hl)': 0, 'Sorties de chais (hl)': 0, "Stock physique en début de camp production (hl)":0, 'sortie': 0})

df_final = df_final[['campagne', 'Stock physique en début de camp production (hl)','Récoltes (hl)','Sorties de chais (hl)']] #, 'sortie'
#df_final


# In[ ]:


def create_graphique(data,graph_filename):

    # CREATION DU GRAPHE
    fig = px.line(data, x="campagne", y=data.columns, color='variable', markers=True, symbol="variable",color_discrete_sequence=["blue","green","#ea4f57"],
                  title="Ma cave",height=650)
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(title={
                        'text': "<b>MA CAVE</b>",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                      title_font_size=24,
                      title_font_color='#f7bb58',
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="white",
                      plot_bgcolor = "white",
                      legend=dict(orientation="h",xanchor = "center",x = 0.5),
                      legend_itemdoubleclick=False,
                      legend_font_size=15
                     )

    fig.update_yaxes(tickformat=",")
    fig.update_layout(separators="* .*")

    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True,showline=True, linewidth=1, linecolor='Lightgrey')
    fig.update_yaxes(fixedrange=True,rangemode="tozero")
    fig.update_traces(
        hovertemplate="<br>".join([
            "%{y} hl",
        ])
    )
    #fig.show()
    fig.write_html(graph_filename,include_plotlyjs=False)

    return


# In[ ]:


for indexes in df_final.index.unique():
    df = df_final.loc[[indexes]]
    
    cols = df.columns
    data = df.reset_index()[cols]
    data.sort_values(by='campagne')
    
    
    [identifiant, appellation, couleur] = indexes
    dossier = dossier_graphes+"/"+identifiant+"/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()
    
    create_graphique(data,dossier+"/drm-stock-recoltes-sorties.html")


# In[ ]:




