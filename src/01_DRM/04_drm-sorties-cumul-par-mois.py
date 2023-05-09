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

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-5:]
mouvements = mouvements.query('campagne in @lastcampagnes')
mouvements = mouvements[mouvements['genre'] != 'VCI']
mouvements = mouvements[mouvements['libelle type'] == 'Suspendu']
mouvements = mouvements.query("appellation != 'CDP'")

mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)

if(id_operateur):
    mouvements = mouvements.query("identifiant == @id_operateur").reset_index()

mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)
typedemouvements = ['sorties/vrac','sorties/crd', 'sorties/factures', 'sorties/export','sorties/acq_crd','sorties/consommation']
mouvements = mouvements.query("type_de_mouvement in @typedemouvements").reset_index()

mouvements['sorties'] = mouvements["type_de_mouvement"].str.lower().str.startswith("sorties/")
mouvements['filtre_produit'] = mouvements['appellation'] + "-" + mouvements['lieu'] + "-" +mouvements['certification']+ "-" +mouvements['genre']+ "-" +mouvements['mention']


# In[ ]:


### PAR APPELLATION ET COULEUR

sorties = mouvements.query("sorties == True")

sorties = sorties.groupby(["identifiant","filtre_produit","couleur",'campagne','periode']).sum(["volume mouvement"])[["volume mouvement"]]
sorties = sorties.reset_index()

sorties['couleur'] = sorties['couleur'].str.upper()

sorties.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

sorties['m'] = sorties["periode"].str.extract('.*(\d{2})', expand = False)
sorties['mois'] = sorties['m'].map(mois,na_action=None)

sorties['ordre_mois']= sorties['mois'].map(mois_sort,na_action=None)

sorties_spe_spe = sorties.sort_values(by=["identifiant",'filtre_produit','couleur',"ordre_mois","campagne"])


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

tabcouleur = ["#CFCFCF", "#A1A1A1", "#5D5D5D","#0A0A0A","#ea4f57"]
couleurs = tabcouleur[-len(df_final['campagne'].unique()):]

df_final.sort_values(by=["identifiant",'filtre_produit','couleur',"ordre_mois","campagne"])

df_final["annee"] = df_final["periode"].str.extract('(\d{4}).*', expand = False)

df_final = df_final.round({'volume': 0})


# In[ ]:


def create_graphe(final,identifiant,appellation,couleur):
    # CREATION DU GRAPHE
    fig = px.bar(final, x="mois", y="volume cumule",custom_data=['campagne'],
                 color='campagne', barmode='group',
                 height=500,
                 color_discrete_sequence=couleurs)
    fig.update_layout(title={
                        'text': "<b>MA CAVE</b>",
                        'y':0.98,
                        'x':0.489,
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
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    fig.update_yaxes(tickformat=",")
    fig.update_layout(separators="* .*")
    fig.update_traces(
        hovertemplate="<br>".join([
            "%{x} %{customdata[0]}",
            "%{y} hl",
        ])
    )

    #fig.show()

    dossier = dossier_graphes+"/"+identifiant+"/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()

    fig.write_html(dossier+"/drm-sorties-cumul-par-mois.html",include_plotlyjs=False)

    return


# In[ ]:


df_final.sort_values(by=["identifiant",'filtre_produit','couleur',"ordre_mois","campagne"])


# In[ ]:


#REMPLIR AVEC DES 0 POUR LES MOIS POUR LES QUELLES NOUS N'AVONS RIEN ET CREATION DES GRAPHES DANS LA FOULE

currentMonth = format(datetime.now().month, "02d")

annees = sorted(df_final['annee'].unique())

annees.append(str(int(annees[0])-1))
annees = sorted(annees)
les_mois = sorted(sorties["m"].unique())

for bloc in df_final.index.unique():

    df = df_final.loc[[bloc]]
    df = df.reset_index()
    for a in annees:
        for m in les_mois:
            if(a == annees[0] and int(m) < 8): #si la première annees ne pas prendre de 0 à 8
                continue
            if(a == annees[len(annees)-1] and int(m) > int(currentMonth)): #si la dernière annee ne pas prendre de 0 à 8
                continue
            p = a+'-'+m
            campagne = str(a)+'-'+str(int(a)+1)
            if (int(m)  < 8): #si le mois est plus petit que 8 alors campagne précédente
                campagne = str(int(a)-1)+'-'+str(a)
            if(p not in df.periode.unique()): #si la periode ne se trouve pas dans la liste on l'ajoute
                df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne, p, 0, m ,mois[m],mois_sort[mois[m]],a]

    df = df.sort_values(by=["identifiant",'filtre_produit','couleur',"ordre_mois","campagne"])
    df['volume cumule'] = df.groupby(["identifiant","filtre_produit", "couleur","campagne"])['volume'].cumsum()
    df = df.reset_index(drop=True)
    create_graphe(df,bloc[0],bloc[1],bloc[2])

