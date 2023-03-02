#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib

path = pathlib.Path().absolute()
path = str(path).replace("src/drm","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
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


contrats = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False)

lastcampagnes = contrats['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-1:]

contrats_csv = contrats.query('campagne in @lastcampagnes')

contrats_csv['couleur'] = contrats_csv['couleur'].str.upper()

contrats_csv.rename(columns = {'identifiant vendeur':'identifiant_vendeur','nom acheteur': 'nom_acheteur','volume enleve (en hl)':'volume enleve'}, inplace = True)


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


# In[ ]:


# PAR APPELLATION ET COULEUR

contrats['filtre_produit'] = contrats['appellation'] + "-" + contrats['lieu'] + "-" +contrats['certification']+ "-" +contrats['genre']+ "-" +contrats['mention']

contrats_spe_spe = contrats.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]

contrats_spe_spe = contrats_spe_spe.reset_index(level='identifiant acheteur')
contrats_spe_spe = contrats_spe_spe.reset_index(level='nom_acheteur')

#contrats_spe_spe

# PAR APPELLATIONS


contrats_spe_all = contrats_spe_spe.groupby(["identifiant_vendeur","filtre_produit",'identifiant acheteur',"nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_spe_all["couleur"] = "TOUT"
contrats_spe_all = contrats_spe_all.reset_index()
contrats_spe_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

#contrats_spe_all

#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS


contrats_all_all = contrats_spe_spe.groupby(["identifiant_vendeur",'identifiant acheteur',"nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_all_all["couleur"] = "TOUT"
contrats_all_all["filtre_produit"] = "TOUT"
contrats_all_all = contrats_all_all.reset_index()

contrats_all_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

#contrats_all_all


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([contrats_spe_spe, contrats_spe_all])
df_final = pd.concat([df_final, contrats_all_all])

df_final = df_final.sort_values(by=['identifiant_vendeur','filtre_produit','couleur'])

df_final.rename(columns = {'volume enleve':'volume'}, inplace = True)
df_final.rename(columns = {'nom_acheteur':"Client"}, inplace = True)

#df_final


# In[ ]:


def create_graphe(df, identifiant, appellation, couleur):

    fig = px.pie(df, values='volume', names='Client', color_discrete_sequence=px.colors.sequential.Agsunset, title="Contractualisation "+lastcampagnes[0], width=632, height=650)
    fig.update_traces(textposition='inside', textinfo='label+text', text=df['volume'].map("{:,} hl".format))
    #fig.show()

    dossier = dossier_graphes+"/"+identifiant+"/contrat/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)

    fig.write_html(dossier+"/graphe1.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[bloc]
    create_graphe(df, bloc[0], bloc[1], bloc[2])


# In[ ]:




