#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib
from datetime import datetime

path = pathlib.Path().absolute()
path = str(path).replace("src","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
source = "DRM Inter-Rhône"

sort_week = [31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]


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


contrats = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False)

contrats['date de validation'] = pd.to_datetime(contrats['date de validation'], utc=True)
contrats['semaine'] = contrats['date de validation'].dt.isocalendar().week
#contrats['semaine'].unique()
lastcampagnes = contrats['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-5:]


contrats_csv = contrats.query('campagne in @lastcampagnes')
contrats_csv['couleur'] = contrats_csv['couleur'].str.upper()

contrats_csv.rename(columns = {'identifiant vendeur':'identifiant_vendeur','volume enleve (en hl)':'volume enleve'}, inplace = True)

if(id_operateur):
    contrats = contrats_csv.query("identifiant_vendeur == @id_operateur").reset_index()
    negociant = False
    if not (len(contrats.index)): ##si c'est un négociant
        negociant = True
        contrats_csv.rename(columns = {'identifiant acheteur':'identifiant_acheteur'}, inplace = True)
        contrats = contrats_csv.query("identifiant_acheteur == @id_operateur").reset_index()
        contrats.rename(columns = { 'identifiant_acheteur' : 'identifiant_a', #temp
                                    'identifiant_vendeur' : 'identifiant_v',
                                    'nom_acheteur' : 'nom_a',
                                    ' nom vendeur' : 'nom_v'
                                    }, inplace = True)

        contrats.rename(columns = { 'identifiant_a' : 'identifiant_vendeur',
                                    'identifiant_v' : 'identifiant acheteur',
                                    'nom_a' : 'nom_vendeur',
                                    'nom_v' : 'nom_acheteur'}, inplace = True)
# PAR APPELLATION ET COULEUR

contrats['filtre_produit'] = contrats['appellation'] + "-" + contrats['lieu'] + "-" +contrats['certification']+ "-" +contrats['genre']+ "-" +contrats['mention']

contrats_spe_spe = contrats.groupby(["identifiant_vendeur","filtre_produit", "couleur","campagne","semaine"]).sum(["volume enleve"])[["volume enleve"]]
contrats_spe_spe.reset_index(level=['semaine'], inplace=True)
contrats_spe_spe['semaine-sort'] = (contrats_spe_spe['semaine']-31)%53
contrats_spe_spe = contrats_spe_spe.sort_values(by=["identifiant_vendeur","filtre_produit", "couleur","campagne",'semaine-sort'])
#contrats_spe_spe['volume'] = contrats_spe_spe.groupby(["identifiant_vendeur","filtre_produit", "couleur","campagne"])['volume enleve'].cumsum()
contrats_spe_spe = contrats_spe_spe.reset_index()
contrats_spe_spe.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
#contrats_spe_spe


# PAR APPELLATIONS

contrats_spe_all = contrats.groupby(["identifiant_vendeur","filtre_produit", "campagne","semaine"]).sum(["volume enleve"])[["volume enleve"]]
contrats_spe_all.reset_index(level=['semaine'], inplace=True)
contrats_spe_all['semaine-sort'] = (contrats_spe_all['semaine']-31)%53
contrats_spe_all = contrats_spe_all.sort_values(by=["identifiant_vendeur","filtre_produit","campagne",'semaine-sort'])
#contrats_spe_all['volume'] = contrats_spe_all.groupby(["identifiant_vendeur","filtre_produit","campagne"])['volume enleve'].cumsum()
contrats_spe_all["couleur"] = "TOUT"
contrats_spe_all = contrats_spe_all.reset_index()
contrats_spe_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
#contrats_spe_all


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

contrats_all_all = contrats.groupby(["identifiant_vendeur","campagne","semaine"]).sum(["volume enleve"])[["volume enleve"]]
contrats_all_all.reset_index(level=['semaine'], inplace=True)
contrats_all_all['semaine-sort'] = (contrats_all_all['semaine']-31)%53
contrats_all_all = contrats_all_all.sort_values(by=["identifiant_vendeur","campagne",'semaine-sort'])
#contrats_all_all['volume'] = contrats_all_all.groupby(["identifiant_vendeur","campagne"])['volume enleve'].cumsum()
contrats_all_all["couleur"] = "TOUT"
contrats_all_all["filtre_produit"] = "TOUT"
contrats_all_all = contrats_all_all.reset_index()
contrats_all_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
#contrats_all_all


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([contrats_spe_spe, contrats_spe_all])
df_final = pd.concat([df_final, contrats_all_all])
df_final = df_final.sort_values(by=['identifiant_vendeur', 'filtre_produit','couleur'])


df_final['campagne-semaine'] = df_final['campagne']+"-"+df_final['semaine'].apply(str)

tabcouleur = ["#CFCFCF", "#A1A1A1", "#5D5D5D","#0A0A0A","#E75047"]
couleurs = tabcouleur[-len(df_final['campagne'].unique()):]


# In[ ]:


def create_graphe(df,identifiant,appellation,couleur):
    fig = px.line(df, x="semaine", y="volume", color='campagne', width=1200, height=500,color_discrete_sequence=couleurs,
                 labels={
                     "semaine": "Numéro de la semaine - Début de campagne : Semaine 31",
                     "volume": "Volume contractualisé hebdomadaire (en hl)"})
    fig.update_layout(xaxis_type = 'category')
    fig.update_xaxes(categoryorder='array', categoryarray= sort_week)

    dossier = dossier_graphes+"/"+identifiant+"/contrat/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)

    fig.write_html(dossier+"/contrats-contractualisation-comparaison-deroulement-par-campagne.html",include_plotlyjs=True)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    df = df.reset_index()
    for campagne in lastcampagnes:
        if campagne+'-31' not in df['campagne-semaine'].unique():
            df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne, 31,0,0,campagne+'-31']

        if campagne+'-30' not in df['campagne-semaine'].unique() and campagne != lastcampagnes[-1:][0]:
            df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne, 30,0,53,campagne+'-30']

        currentweek = datetime.today().isocalendar()[1]
        if campagne+'-'+str(currentweek) not in df['campagne-semaine'].unique() and campagne == lastcampagnes[-1:][0]:
            df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne, currentweek,0,(currentweek-31)%53,campagne+'-'+str(currentweek)]

    df = df.sort_values(by=['campagne'])
    df = df.reset_index(drop=True)
    df = df.sort_values(by=['identifiant_vendeur', 'filtre_produit','couleur','campagne','semaine-sort'])
    df['volume'] = df.groupby(["identifiant_vendeur","filtre_produit", "couleur","campagne"])['volume enleve'].cumsum()

    create_graphe(df,bloc[0],bloc[1],bloc[2])

