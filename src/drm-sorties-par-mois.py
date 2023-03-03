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

mois = { "08" : "Août" , "09" : "Septembre", "10" : "Octobre", "11" : "Novembre" , "12" : "Décembre",
        "01" : "Janvier", "02" : "Février", "03" : "Mars", "04" : "Avril", "05" : "Mai", "06" : "Juin",
        "07" : "Juillet" }

mois_sort = { "Août" : "01" , "Septembre" : "02", "Octobre" : "03", "Novembre" : "04" , "Décembre" : "05",
        "Janvier" : "06", "Février" : "07", "Mars" : "08", "Avril" : "09", "Mai" : "10", "Juin" : "11",
        "Juillet" : "12" }


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


mouvements = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False)

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-5:]
mouvements = mouvements.query('campagne in @lastcampagnes')

mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)

if(id_operateur):
    mouvements = mouvements.query("identifiant == @id_operateur").reset_index()

mouvements["volume mouvement"] = mouvements["volume mouvement"]*(-1)
mouvements['sorties'] = mouvements["type de mouvement"].str.lower().str.startswith("sorties/")
mouvements['filtre_produit'] = mouvements['appellation'] + "-" + mouvements['lieu'] + "-" +mouvements['certification']+ "-" +mouvements['genre']+ "-" +mouvements['mention']


# In[ ]:


### PAR APPELLATION ET COULEUR

sorties = mouvements.query("sorties == True")

sorties = sorties.groupby(["identifiant","filtre_produit","couleur",'campagne','periode']).sum(["volume mouvement"])[["volume mouvement"]]
sorties = sorties.reset_index()

sorties['couleur'] = sorties['couleur'].str.upper()

sorties.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

sorties['mois'] = sorties["periode"].str.extract('.*(\d{2})', expand = False)
sorties['mois'] = sorties['mois'].map(mois,na_action=None)

sorties['ordre_mois']= sorties['mois'].map(mois_sort,na_action=None)

sorties_spe_spe = sorties.sort_values(by=["identifiant",'filtre_produit','couleur',"ordre_mois","campagne"])

#sorties


# In[ ]:


# PAR APPELLATIONS

sorties_spe_all = sorties_spe_spe.groupby(["identifiant","filtre_produit",'campagne','periode',"mois","ordre_mois"]).sum(["volume mouvement"])[["volume mouvement"]]
sorties_spe_all["couleur"] = "TOUT"
sorties_spe_all = sorties_spe_all.reset_index()
sorties_spe_all.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

#sorties_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

sorties_all_all = sorties_spe_spe.groupby(["identifiant",'campagne','periode',"mois","ordre_mois"]).sum(["volume mouvement"])[["volume mouvement"]]
sorties_all_all["couleur"] = "TOUT"
sorties_all_all["filtre_produit"] = "TOUT"
sorties_all_all = sorties_all_all.reset_index()

sorties_all_all.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

#sorties_all_all


# In[ ]:


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([sorties_spe_spe, sorties_spe_all])
df_final = pd.concat([df_final, sorties_all_all])

df_final = df_final.sort_values(by=['identifiant', 'filtre_produit','couleur'])

df_final.rename(columns = {'volume mouvement':'volume'}, inplace = True)

#df_final
tabcouleur = ["#CFCFCF", "#A1A1A1", "#5D5D5D","#0A0A0A","#E75047"]
couleurs = tabcouleur[-len(df_final['campagne'].unique()):]


# In[ ]:


def create_graphe(final,identifiant,appellation,couleur):

    # CREATION DU GRAPHE
    fig = px.histogram(final, x="mois", y="volume",
                 color='campagne', barmode='group',
                 height=500,
                 color_discrete_sequence=couleurs)
    fig.update_layout(title_font_size=24,
                      title_font_color="rgb(231, 80, 71)",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="white",
                      plot_bgcolor = "white",
                      yaxis=dict(tickformat=".f"),
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

    fig.write_html(dossier+"/drm-sorties-par-mois.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    create_graphe(df,bloc[0],bloc[1],bloc[2])

