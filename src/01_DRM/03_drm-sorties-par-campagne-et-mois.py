#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib
from datetime import datetime


# In[ ]:


path = pathlib.Path().absolute()
path = str(path).replace("/src","").replace("/01_DRM","")
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


mouvements = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)
mouvements = mouvements[mouvements['genre'] != 'VCI']
mouvements = mouvements[mouvements['libelle type'] == 'Suspendu']

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-3:]
mouvements = mouvements.query('campagne in @lastcampagnes')
mouvements = mouvements.query("appellation != 'CDP'")

mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)

if(id_operateur):
    mouvements = mouvements.query("identifiant == @id_operateur").reset_index()

mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)

typedemouvements = ['sorties/vrac','sorties/crd', 'sorties/factures', 'sorties/export','sorties/acq_crd','sorties/consommation']
mouvements = mouvements.query("type_de_mouvement in @typedemouvements").reset_index()


mouvements['sorties'] = mouvements["type_de_mouvement"].str.lower().str.startswith("sorties/")

mouvements['filtre_produit'] = mouvements['appellation'] + "-" + mouvements['lieu'] + "-" +mouvements['certification']+ "-" +mouvements['genre']+ "-" +mouvements['mention']

mouvements['mois'] = mouvements["periode"].str.extract('.*(\d{2})', expand = False)

mouvements['mois'] = mouvements['mois'].map(mois,na_action=None)

#mouvements


# In[ ]:


### PAR APPELLATION ET COULEUR

sorties = mouvements.query("sorties == True")

sorties = sorties.groupby(["identifiant","filtre_produit","couleur",'campagne','mois']).sum(["volume mouvement"])[["volume mouvement"]]
sorties = sorties.reset_index()

sorties['couleur'] = sorties['couleur'].str.upper()

sorties.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

sorties['ordre-mois'] = sorties['mois'].map(mois_sort,na_action=None)

sorties_spe_spe = sorties.sort_values(by=["identifiant",'filtre_produit','couleur',"campagne",'ordre-mois'])

#sorties_spe_spe


# In[ ]:


# PAR APPELLATIONS

sorties_spe_all = sorties_spe_spe.groupby(["identifiant","filtre_produit",'campagne','mois','ordre-mois']).sum(["volume mouvement"])[["volume mouvement"]]
sorties_spe_all = sorties_spe_all.sort_values(by=["identifiant",'filtre_produit',"campagne",'ordre-mois'])
sorties_spe_all["couleur"] = "TOUT"
sorties_spe_all = sorties_spe_all.reset_index()
sorties_spe_all.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

#sorties_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

sorties_all_all = sorties_spe_spe.groupby(["identifiant",'campagne','mois','ordre-mois']).sum(["volume mouvement"])[["volume mouvement"]]
sorties_all_all = sorties_all_all.sort_values(by=["identifiant","campagne",'ordre-mois'])
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
df_final['campagne-ordre-mois'] = df_final['campagne']+"-"+df_final['ordre-mois']
df_final['mois-campagne'] = df_final['mois']+"-"+df_final['campagne']


# In[ ]:


df_final.rename(columns = {'volume mouvement':'volume',"mois-campagne":'periode'}, inplace = True)

df_final = df_final.fillna(0)
df_final = df_final.round({'volume': 0})


# In[ ]:


def create_graphe(final,identifiant,appellation,couleur):
    # CREATION DU GRAPHE
    fig = px.line(final, x='periode', y="volume", custom_data=['mois', 'campagne'], markers=True, color_discrete_sequence=["#ea4f57"], title="Ma cave",height=650)
    fig.update_layout(title={
                        'text': "<b>MA CAVE</b>",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                      title_font_size=24,
                      title_font_color="#f7bb58",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="white",
                      plot_bgcolor = "white",
                      yaxis=dict(tickformat=".0f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5),
                      legend_itemdoubleclick=False,
                      legend_font_size=15
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True, showline=True, linewidth=1, linecolor='Lightgrey', showticklabels=False)
    fig.update_yaxes(fixedrange=True, rangemode="tozero")
    fig.update_yaxes(tickformat=",")
    fig.update_layout(separators="* .*")
    
    fig.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]} %{customdata[1]}",
            "%{y} hl",
        ])
    )
    for tick in range(len(final)):
        if tick % 12 == 0:
            fig.add_vline(tick, annotation_text=final['campagne'][tick])

    #fig.show()

    dossier = dossier_graphes+"/"+identifiant+"/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()

    fig.write_html(dossier+"/drm-sorties-par-campagne-et-mois.html",include_plotlyjs=False)

    return


# In[ ]:


current_month = str(datetime.today().month).zfill(2)
current_month_order = mois_sort[mois[current_month]]

for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    for m in mois_sort.keys():
        for campagne in lastcampagnes:
            if(m+'-'+campagne not in df.periode.values):
                if(campagne == lastcampagnes[-1] and mois_sort[m] > current_month_order):
                    continue
                tmp = { "campagne": campagne, "mois": m, "volume" : 0, "ordre-mois" : mois_sort[m],"campagne-ordre-mois":campagne+'-'+mois_sort[m], "periode":m+'-'+campagne}
                tmp = pd.DataFrame(data=tmp, index=[bloc])
                df= pd.concat([df, tmp], axis=0).sort_index()

    df = df.sort_values(by=['campagne','ordre-mois'])
    create_graphe(df,bloc[0],bloc[1],bloc[2])

