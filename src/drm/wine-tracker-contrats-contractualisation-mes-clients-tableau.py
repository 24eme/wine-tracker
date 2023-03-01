#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib
import plotly.graph_objects as go

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
lastcampagnes = lastcampagnes[-5:]


contrats = contrats.query('campagne in @lastcampagnes')
contrats['couleur'] = contrats['couleur'].str.upper()

contrats.rename(columns = {'identifiant vendeur':'identifiant_vendeur','nom acheteur': 'nom_acheteur','volume enleve (en hl)':'volume enleve'}, inplace = True)

if(id_operateur):
    contrats = contrats.query("identifiant_vendeur == @id_operateur").reset_index()
#contrats


# In[ ]:


# PAR APPELLATION ET COULEUR

contrats['filtre_produit'] = contrats['appellation'] + "-" + contrats['lieu'] + "-" +contrats['certification']+ "-" +contrats['genre']+ "-" +contrats['mention']

#LES CONTRATS 5 DERNIERES CAMPAGNES 
contrats_all = contrats.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_all.rename(columns = {'volume enleve':'5 DA'}, inplace = True)


#LES CONTRATS DE LA CAMPAGNE COURANTE
campagne_courante = lastcampagnes[-1:]
contrats_annee_courante = contrats.query('campagne in @campagne_courante')
contrats_annee_courante = contrats_annee_courante.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_annee_courante.rename(columns = {'volume enleve':'n'}, inplace = True)
contrats_annee_courante = contrats_annee_courante.sort_values(by=['n'], ascending=False)

#LES CONTRATS DE LA CAMPAGNE_PRECEDENTE n-1
campagne_n_1 = lastcampagnes[-2:][0]
contrats_annee_n_1 = contrats.query('campagne in @campagne_n_1')
contrats_annee_n_1 = contrats_annee_n_1.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_annee_n_1.rename(columns = {'volume enleve':'n-1'}, inplace = True)


df_merge_spe_spe = contrats_annee_courante.merge(contrats_annee_n_1,how = 'left',on=['identifiant_vendeur','filtre_produit','couleur','identifiant acheteur','nom_acheteur']).merge(contrats_all,on=['identifiant_vendeur','filtre_produit','couleur','identifiant acheteur','nom_acheteur'])
df_merge_spe_spe = df_merge_spe_spe.reset_index()
df_merge_spe_spe.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

df_merge_spe_spe


# In[ ]:


# PAR APPELLATIONS

#LES CONTRATS 5 DERNIERES CAMPAGNES 
contrats_all_spe_all= contrats.groupby(["identifiant_vendeur","filtre_produit","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_all_spe_all.rename(columns = {'volume enleve':'5 DA'}, inplace = True)


#LES CONTRATS DE LA CAMPAGNE COURANTE
contrats_annee_courante_spe_all = contrats.query('campagne in @campagne_courante')
contrats_annee_courante_spe_all = contrats_annee_courante_spe_all.groupby(["identifiant_vendeur","filtre_produit","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_annee_courante_spe_all.rename(columns = {'volume enleve':'n'}, inplace = True)
contrats_annee_courante_spe_all = contrats_annee_courante_spe_all.sort_values(by=['n'], ascending=False)


#LES CONTRATS DE LA CAMPAGNE_PRECEDENTE n-1
contrats_annee_n_1_spe_all = contrats.query('campagne in @campagne_n_1')
contrats_annee_n_1_spe_all = contrats_annee_n_1_spe_all.groupby(["identifiant_vendeur","filtre_produit","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_annee_n_1_spe_all.rename(columns = {'volume enleve':'n-1'}, inplace = True)


df_merge_spe_all = contrats_annee_courante_spe_all.merge(contrats_annee_n_1_spe_all,how = 'left',on=['identifiant_vendeur','filtre_produit','identifiant acheteur','nom_acheteur']).merge(contrats_all_spe_all,on=['identifiant_vendeur','filtre_produit','identifiant acheteur','nom_acheteur'])
df_merge_spe_all["couleur"] = "TOUT"
df_merge_spe_all = df_merge_spe_all.reset_index()
df_merge_spe_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

#df_merge_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

#LES CONTRATS 5 DERNIERES CAMPAGNES 
contrats_all_all_all= contrats.groupby(["identifiant_vendeur","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_all_all_all.rename(columns = {'volume enleve':'5 DA'}, inplace = True)

#LES CONTRATS DE LA CAMPAGNE COURANTE
contrats_annee_courante_all_all = contrats.query('campagne in @campagne_courante')
contrats_annee_courante_all_all = contrats_annee_courante_all_all.groupby(["identifiant_vendeur","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_annee_courante_all_all.rename(columns = {'volume enleve':'n'}, inplace = True)
contrats_annee_courante_all_all = contrats_annee_courante_all_all.sort_values(by=['n'], ascending=False)


#LES CONTRATS DE LA CAMPAGNE_PRECEDENTE n-1
contrats_annee_n_1_all_all = contrats.query('campagne in @campagne_n_1')
contrats_annee_n_1_all_all = contrats_annee_n_1_all_all.groupby(["identifiant_vendeur","identifiant acheteur","nom_acheteur"]).sum(["volume enleve"])[["volume enleve"]]
contrats_annee_n_1_all_all.rename(columns = {'volume enleve':'n-1'}, inplace = True)

df_merge_all_all = contrats_annee_courante_all_all.merge(contrats_annee_n_1_all_all,how = 'left',on=['identifiant_vendeur','identifiant acheteur','nom_acheteur']).merge(contrats_all_all_all,on=['identifiant_vendeur','identifiant acheteur','nom_acheteur'])
df_merge_all_all["couleur"] = "TOUT"
df_merge_all_all["filtre_produit"] = "TOUT"
df_merge_all_all = df_merge_all_all.reset_index()
df_merge_all_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
#df_merge_all_all


# In[ ]:


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([df_merge_spe_spe, df_merge_spe_all])
df_final = pd.concat([df_final, df_merge_all_all])

df_final["5 DA"] = df_final["5 DA"]/5
df_final = df_final.fillna(0)

#df_final


# In[ ]:


def create_graphe(df,identifiant,appellation,couleur):
    fig = go.Figure(data=[go.Table(
                header=dict(values=list(df.columns),
                            fill_color='#E75047',font=dict(color='white'),
                            align='left',line_color='black'),
                cells=dict(values=df.transpose().values.tolist(),
                           align='left',fill_color=['white'],line_color='black')
            )
    ])
    #fig.show()

    dossier = dossier_graphes+"/"+identifiant+"/contrat/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)

    fig.write_html(dossier+"/graphe2.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[bloc]
    create_graphe(df,bloc[0],bloc[1],bloc[2])

