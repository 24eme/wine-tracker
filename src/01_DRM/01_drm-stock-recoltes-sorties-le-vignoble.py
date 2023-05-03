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
csv_etablissements = path+"/data/contrats/export_bi_etablissements.csv"
source = "DRM Inter-Rhône"


# In[ ]:


drm = pd.read_csv(csv, sep=";",encoding="iso8859_15",index_col=False)


# In[ ]:


lastcampagnes = drm['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-10:]
drm = drm.query('campagne in @lastcampagnes')


# In[ ]:


#SEULEMENT DONNEES SUR LES DRM PRODUCTEURS

etablissements = pd.read_csv(csv_etablissements, sep=";",encoding="iso8859_15",index_col=False)
familleproducteurs = ['producteur cave_cooperative','producteur cave_particuliere','producteur vendeur_raisin']
etablissements = etablissements.query("famille in @familleproducteurs")

identifiantsproducteurs = etablissements['identifiant'].unique()

drm = drm.query('identifiant in @identifiantsproducteurs')
drm = drm.loc[drm['appellations'] != "CDP"]


# In[ ]:


#pour les volumes récoltés :
csv_mouvements = path+"/data/drm/export_bi_mouvements.csv"  #il manque un ; à la fin du header.
mouvements = pd.read_csv(csv_mouvements, sep=";",encoding="iso8859_15",index_col=False)
mouvements.rename(columns = {'identifiant declarant':'identifiant','type de mouvement':'type_de_mouvement','certification':'certifications','genre':'genres','appellation':'appellations','mention':'mentions','lieu':'lieux','couleur':'couleurs'}, inplace = True)
mouvements = mouvements.query('identifiant in @identifiantsproducteurs')
mouvements = mouvements.query('campagne in @lastcampagnes')
mouvements = mouvements.query("appellations != 'CDP'")

#mouvements


# In[ ]:


drm['filtre_produit'] = drm['appellations'] + "-" + drm['lieux'] + "-" +drm['certifications']+ "-" +drm['genres']+ "-" +drm['mentions']
mouvements['filtre_produit'] = mouvements['appellations'] + "-" + mouvements['lieux'] + "-" +mouvements['certifications']+ "-" +mouvements['genres']+ "-" +mouvements['mentions']


# In[ ]:


# PAR APPELLATION ET COULEUR

#SOMME RECOLTES
drm_recolte = mouvements.query("type_de_mouvement == 'entrees/recolte'")
drm_recolte = drm_recolte.groupby(["campagne",'filtre_produit', "couleurs"]).sum(["volume mouvement"])[["volume mouvement"]]


#SOMME SORTIES
typedemouvementssorties = ['sorties/vrac','sorties/vrac_contrat','sorties/vrac_export','sorties/crd', 'sorties/factures', 'sorties/export', 'sorties/crd_acquittes', 'sorties/acq_crd','sorties/consommation']
drm_sortie = mouvements.query("type_de_mouvement in @typedemouvementssorties").reset_index()
drm_sortie = drm_sortie.groupby(["campagne","filtre_produit", "couleurs"]).sum(["volume mouvement"])[["volume mouvement"]]


#SOMME STOCK DEBUT DE CAMPAGNE
drm_stock_debut = drm
drm_stock_debut['debut_campagne'] = drm["date"].str.lower().str.endswith("08")
drm_stock_debut = drm_stock_debut.query("debut_campagne == True")
drm_stock_debut = drm_stock_debut.groupby(["campagne","filtre_produit", "couleurs"]).sum(["stock debut"])[["stock debut"]]


df_final_spe_spe = pd.merge(drm_recolte, drm_sortie,how='outer', on=["campagne","filtre_produit", "couleurs"])
df_final_spe_spe = pd.merge(df_final_spe_spe, drm_stock_debut ,how='outer', on=["campagne","filtre_produit", "couleurs"])

df_final_spe_spe = df_final_spe_spe.reset_index()

df_final_spe_spe['couleurs'] = df_final_spe_spe['couleurs'].str.upper()

df_final_spe_spe.index = [df_final_spe_spe['filtre_produit'],df_final_spe_spe['couleurs']]
df_final_spe_spe.drop(['filtre_produit','couleurs'], axis=1, inplace=True)

df_final_spe_spe.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','volume mouvement_x' : 'Récoltes (hl)', 'volume mouvement_y' : 'Sorties de chais (hl)'}, inplace = True)

#df_final_spe_spe


# In[ ]:


# PAR APPELLATIONS

drm_recolte_spe_all = drm_recolte.groupby(["campagne","filtre_produit"]).sum(["volume mouvement"])[["volume mouvement"]]
drm_sortie_spe_all = drm_sortie.groupby(["campagne","filtre_produit"]).sum(["volume mouvement"])[["volume mouvement"]]
drm_stock_debut_spe_all = drm_stock_debut.groupby(["campagne","filtre_produit"]).sum(["stock debut"])[["stock debut"]]


drm_merge_spe_all = pd.merge(drm_recolte_spe_all, drm_sortie_spe_all,how='outer', on=["campagne","filtre_produit"])
drm_merge_spe_all = pd.merge(drm_merge_spe_all, drm_stock_debut_spe_all ,how='outer', on=["campagne","filtre_produit"])

drm_merge_spe_all = drm_merge_spe_all.reset_index()

drm_merge_spe_all['couleurs'] = "TOUT"

drm_merge_spe_all.index = [drm_merge_spe_all['filtre_produit'],drm_merge_spe_all['couleurs']]
drm_merge_spe_all.drop(['filtre_produit','couleurs'], axis=1, inplace=True)

drm_merge_spe_all.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','volume mouvement_x' : 'Récoltes (hl)', 'volume mouvement_y' : 'Sorties de chais (hl)'}, inplace = True)


#drm_merge_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

drm_recolte_all_all = drm_recolte_spe_all.groupby(["campagne"]).sum(["volume mouvement"])[["volume mouvement"]]
drm_sortie_all_all = drm_sortie_spe_all.groupby(["campagne"]).sum(["volume mouvement"])[["volume mouvement"]]
drm_stock_debut_all_all = drm_stock_debut.groupby(["campagne"]).sum(["stock debut"])[["stock debut"]]


drm_merge_all_all = pd.merge(drm_recolte_all_all, drm_sortie_all_all,how='outer', on=["campagne"])
drm_merge_all_all = pd.merge(drm_merge_all_all, drm_stock_debut_all_all ,how='outer', on=["campagne"])

drm_merge_all_all = drm_merge_all_all.reset_index()

drm_merge_all_all['filtre_produit'] = "TOUT"
drm_merge_all_all['couleurs'] = "TOUT"

drm_merge_all_all.index = [drm_merge_all_all['filtre_produit'],drm_merge_all_all['couleurs']]
drm_merge_all_all.drop(['filtre_produit','couleurs'], axis=1, inplace=True)

drm_merge_all_all.rename(columns = {'stock debut': 'Stock physique en début de camp production (hl)','volume mouvement_x' : 'Récoltes (hl)', 'volume mouvement_y' : 'Sorties de chais (hl)'}, inplace = True)


#drm_merge_all_all


# In[ ]:


#MERGE DES 3 TABLEAUX : 
df_final = pd.concat([df_final_spe_spe, drm_merge_spe_all])
df_final = pd.concat([df_final, drm_merge_all_all])
df_final = df_final.sort_values(by=['filtre_produit','couleurs'])
df_final = df_final.fillna(0)
df_final = df_final.round({'Récoltes (hl)': 0, 'Sorties de chais (hl)': 0, "Stock physique en début de camp production (hl)":0})
#df_final


# In[ ]:


def create_graphique(final,appellation,couleur):

    # CREATION DU GRAPHE
    fig = px.line(final, x="campagne", y="value", color='variable', markers=True, symbol="variable",color_discrete_sequence=["blue","green","#ea4f57"],
                  title="Le vignoble",height=650)
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(title={
                        'text': "<b>LE VIGNOBLE</b>",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                      title_font_size=24,
                      title_font_color="#a3a3a3",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="#F7F7F7",
                      plot_bgcolor = "#F7F7F7",
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

    dossier = dossier_graphes+"/LE_VIGNOBLE/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()

    fig.write_html(dossier+"/drm-stock-recoltes-sorties.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    df = df.reset_index()

    for campagne in lastcampagnes:
        if campagne not in df.campagne.unique()[::-1] :
            df.loc[len(df)] = [bloc[0], bloc[1],campagne, 0, 0, 0]

    df = df.sort_values(by=['campagne'])
    df = df.reset_index(drop=True)


    df = pd.melt(df, id_vars=['filtre_produit','couleurs','campagne'], value_vars=['Stock physique en début de camp production (hl)','Récoltes (hl)','Sorties de chais (hl)'])
    create_graphique(df,bloc[0],bloc[1])

