#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib


# In[ ]:


path = pathlib.Path().absolute()
path = str(path).replace("src/drm","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/drm/export_bi_mouvements.csv"  #il manque un ; à la fin du header.
source = "DRM Inter-Rhône"

mois = { "08" : "Août" , "09" : "Septembre", "10" : "Octobre", "11" : "Novembre" , "12" : "Décembre",
        "01" : "Janvier", "02" : "Février", "03" : "Mars", "04" : "Avril", "05" : "Mai", "06" : "Juin",
        "07" : "Juillet" }

mois_sort = { "Août" : "01" , "Septembre" : "02", "Octobre" : "03", "Novembre" : "04" , "Décembre" : "05",
        "Janvier" : "06", "Février" : "07", "Mars" : "08", "Avril" : "09", "Mai" : "10", "Juin" : "11",
        "Juillet" : "12" }
             

trimestre = { "01" : 2, "02" : 3, "03" : 3, "04" : 3, "05" : 4, "06" : 4, "07" : 4, "08" : 1, "09" : 1, "10" : 1, "11" : 2, "12" : 2}

trimestre_string = { 1: "Aôut-Septembre-Octobre" , 2 : "Novembre-Décembre-Janvier", 3 : "Février-Mars-Avril", 4 : "Mai-Juin-Juillet"}


# In[ ]:


mouvements = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False)

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-3:]
mouvements = mouvements.query('campagne in @lastcampagnes')

mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)

mouvements["volume mouvement"] = mouvements["volume mouvement"]*(-1)
mouvements['sorties'] = mouvements["type de mouvement"].str.lower().str.startswith("sorties/")
mouvements['filtre_produit'] = mouvements['appellation'] + "-" + mouvements['lieu'] + "-" +mouvements['certification']+ "-" +mouvements['genre']+ "-" +mouvements['mention']

mouvements['mois'] = mouvements["periode"].str.extract('.*(\d{2})', expand = False)
mouvements['trimestre'] = mouvements['mois'].map(trimestre,na_action=None)

mouvements['mois'] = mouvements['mois'].map(mois,na_action=None)

#mouvements


# In[ ]:


### PAR APPELLATION ET COULEUR

sorties = mouvements.query("sorties == True")

sorties = sorties.groupby(["filtre_produit","couleur",'campagne','trimestre']).sum(["volume mouvement"])[["volume mouvement"]]
sorties = sorties.reset_index()

sorties['couleur'] = sorties['couleur'].str.upper()

sorties.set_index(['filtre_produit','couleur'], inplace = True)

sorties_spe_spe = sorties.sort_values(by=['filtre_produit','couleur',"trimestre","campagne"])

#sorties_spe_spe


# In[ ]:


# PAR APPELLATIONS

sorties_spe_all = sorties_spe_spe.groupby(["filtre_produit",'campagne','trimestre']).sum(["volume mouvement"])[["volume mouvement"]]
sorties_spe_all["couleur"] = "TOUT"
sorties_spe_all = sorties_spe_all.reset_index()
sorties_spe_all.set_index(['filtre_produit','couleur'], inplace = True)

#sorties_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

sorties_all_all = sorties_spe_spe.groupby(['campagne','trimestre']).sum(["volume mouvement"])[["volume mouvement"]]
sorties_all_all["couleur"] = "TOUT"
sorties_all_all["filtre_produit"] = "TOUT"
sorties_all_all = sorties_all_all.reset_index()

sorties_all_all.set_index(['filtre_produit','couleur'], inplace = True)

#sorties_all_all


# In[ ]:


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([sorties_spe_spe, sorties_spe_all])
df_final = pd.concat([df_final, sorties_all_all])

df_final = df_final.sort_values(by=['filtre_produit','couleur'])
df_final['trimestre'] = df_final['trimestre'].map(trimestre_string,na_action=None)

df_final.rename(columns = {'volume mouvement':'volume'}, inplace = True)

#df_final


# In[ ]:


def create_graphe(final,appellation,couleur):
    # CREATION DU GRAPHE
    fig = px.histogram(final, x="campagne", y="volume",
                 color='trimestre', barmode='group',
                 color_discrete_sequence=["#e74e62", "#d1342f", "#ac1c25","#961d50","#961d50","#8F1665","#753452","#8A321A"],
                 title="Evolution de MES sorties de Chais par trimestres <br>(en hl, Sources "+source+"-Cumul depuis le début de la campagne)")
    fig.update_layout(title_font_size=14,
                      title_font_color="black",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="#F7F7F7",
                      plot_bgcolor = "#F7F7F7",
                      yaxis=dict(tickformat=".f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5),
                      legend_itemdoubleclick=False
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    #fig.show()
    
    dossier = dossier_graphes+"/1-REFERENCE/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)

    fig.write_html(dossier+"/graphe4.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    create_graphe(df,bloc[0],bloc[1])

