#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib


# In[ ]:


path = pathlib.Path().absolute()
path = str(path).replace("src","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/drm/export_bi_mouvements.csv"  #il manque un ; à la fin du header.
source = "DRM Inter-Rhône"


# In[ ]:


#arguments
id_operateur = None

parser = argparse.ArgumentParser()
parser.add_argument("id_operateur", help="Identifiant opérateur", default=id_operateur, nargs='?')

try:
   args = parser.parse_args()
   id_operateur = args.id_operateur
except:
   print("Arguments pas défaut")


# In[ ]:


#préparations des données de l'opérateur sans filtres
mouvements = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-10:]
mouvements = mouvements.query('campagne in @lastcampagnes')

mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)

if(id_operateur):
    mouvements = mouvements.query("identifiant == @id_operateur").reset_index()

mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)
mouvements['sorties'] = mouvements["type_de_mouvement"].str.lower().str.startswith("sorties/")
mouvements = mouvements.query("sorties == True")
mouvements['filtre_produit'] = mouvements['appellation'] + "-" + mouvements['lieu'] + "-" +mouvements['certification']+ "-" +mouvements['genre']+ "-" +mouvements['mention']

#mouvements


# In[ ]:


### PAR APPELLATION ET COULEUR
mouvements_spe_spe = mouvements.groupby(["identifiant","filtre_produit","couleur","campagne","type_de_mouvement"]).sum(["volume mouvement"])[["volume mouvement"]]
mouvements_spe_spe = mouvements_spe_spe.reset_index()
mouvements_spe_spe['couleur'] = mouvements_spe_spe['couleur'].str.upper()
mouvements_spe_spe.set_index(['identifiant','filtre_produit','couleur'], inplace = True)


# PAR APPELLATIONS
mouvements_spe_all = mouvements.groupby(["identifiant","filtre_produit","campagne","type_de_mouvement"]).sum(["volume mouvement"])[["volume mouvement"]]
mouvements_spe_all["couleur"]="TOUT"
mouvements_spe_all = mouvements_spe_all.reset_index()
mouvements_spe_all.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS
mouvements_all_all = mouvements.groupby(["identifiant","campagne","type_de_mouvement"]).sum(["volume mouvement"])[["volume mouvement"]]
mouvements_all_all['filtre_produit']="TOUT"
mouvements_all_all["couleur"]="TOUT"
mouvements_all_all = mouvements_all_all.reset_index()
mouvements_all_all.set_index(['identifiant','filtre_produit','couleur'], inplace = True)


# In[ ]:


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([mouvements_spe_spe, mouvements_spe_all])
df_final = pd.concat([df_final, mouvements_all_all])
df_final = df_final.sort_values(by=['identifiant', 'filtre_produit','couleur','campagne'])
df_final.rename(columns = {'volume mouvement':'volume'}, inplace = True)


# In[ ]:


def create_graphe(final,identifiant,appellation,couleur):
    # CREATION DU GRAPHE
    fig = px.bar(final, x="campagne", y="volume", color="type_de_mouvement",
                 text_auto=True,
                 title="Evolution de MES sorties de Chais Vrac/Conditionné <br>(en hl, Sources "+source+")")
    fig.update_layout(title_font_size=14,
                      title_font_color="black",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="#b7e1e5",
                      plot_bgcolor = "white",
                      hovermode = False,
                      yaxis=dict(tickformat=".0f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5),
                      legend_itemdoubleclick=False
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    #fig.show()

    dossier = dossier_graphes+"/"+identifiant+"/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()

    fig.write_html(dossier+"/drm-sortie-tous.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    create_graphe(df,bloc[0],bloc[1],bloc[2])

