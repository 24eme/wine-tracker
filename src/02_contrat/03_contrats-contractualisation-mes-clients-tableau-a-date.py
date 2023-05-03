#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib
import numpy as np
from datetime import date

path = pathlib.Path().absolute()
path = str(path).replace("/src","").replace("/02_contrat","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
csv_etablissements = path+"/data/contrats/export_bi_etablissements.csv" #il manque un ; à la fin du header.
tab_mois = { 1 : "Janvier",
             2 : "Février",
             3 : "Mars",
             4 : "Avril",
             5 : "Mai",
             6 : "Juin",
             7 : "Juillet",
             8 : "Août",
             9 : "Septembre",
             10 : "Octobre",
             11 : "Novembre",
             12 : "Décembre"
            }


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

if not id_operateur:
    raise Exception("manque id_operateur")


# In[ ]:


etablissements = pd.read_csv(csv_etablissements, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)
etablissement = etablissements.query("identifiant == @id_operateur")
famille = etablissement['famille'].unique()[0]

if not famille:
    raise Exception("OPERATEUR N'EST PAS DANS LE CSV DES ETABLISSEMENT")


# In[ ]:


contrats = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)
contrats = contrats.query("statut == 'SOLDE' or statut == 'NONSOLDE'")
contrats.rename(columns = {'type de vente':'type_de_vente'}, inplace = True)
contrats = contrats.query("type_de_vente == 'vrac'")

lastcampagnes = contrats['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-6:]

campagne_5_completes = lastcampagnes[:-1]
campagne_courante = lastcampagnes[-1:]
campagne_n_1 = lastcampagnes[-2:][0]

contrats_csv = contrats.query('campagne in @lastcampagnes')
contrats_csv = contrats_csv.copy()
contrats_csv['couleur'] = contrats_csv['couleur'].str.upper()
contrats_csv.rename(columns = {'identifiant vendeur':'identifiant_vendeur','nom acheteur': 'nom_acheteur','volume propose (en hl)':'volume propose'}, inplace = True)
contrats = contrats_csv.query("identifiant_vendeur == @id_operateur").reset_index()

negociant = False

if 'negociant' in famille:
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

contrats['date de validation'] = pd.to_datetime(contrats['date de validation'], utc=True)
contrats['mois_de_validation'] = contrats['date de validation'].dt.month
current_month = date.today().month
contrats = contrats.query("mois_de_validation >= 8 | mois_de_validation <= @current_month") #seulement ceux qui sont entre Aout et le mois courant.

#contrats


# In[ ]:


# PAR APPELLATION ET COULEUR

contrats['filtre_produit'] = contrats['appellation'] + "-" + contrats['lieu'] + "-" +contrats['certification']+ "-" +contrats['genre']+ "-" +contrats['mention']

#LES CONTRATS 5 DERNIERES CAMPAGNES
contrats_all = contrats.query('campagne in @campagne_5_completes')
contrats_all = contrats_all.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_all.rename(columns = {'volume propose':'5 DA'}, inplace = True)

#LES CONTRATS DE LA CAMPAGNE COURANTE
contrats_annee_courante = contrats.query('campagne in @campagne_courante')
contrats_annee_courante = contrats_annee_courante.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_annee_courante.rename(columns = {'volume propose':'n'}, inplace = True)
contrats_annee_courante = contrats_annee_courante.sort_values(by=['n'], ascending=False)

#LES CONTRATS DE LA CAMPAGNE_PRECEDENTE n-1
contrats_annee_n_1 = contrats.query('campagne in @campagne_n_1')
contrats_annee_n_1 = contrats_annee_n_1.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_annee_n_1.rename(columns = {'volume propose':'n-1'}, inplace = True)


df_merge_spe_spe = contrats_annee_courante.merge(contrats_annee_n_1,how = 'left',on=['identifiant_vendeur','filtre_produit','couleur','identifiant acheteur','nom_acheteur']).merge(contrats_all,how = 'left',on=['identifiant_vendeur','filtre_produit','couleur','identifiant acheteur','nom_acheteur'])
df_merge_spe_spe = df_merge_spe_spe.reset_index()
df_merge_spe_spe.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

#df_merge_spe_spe


# In[ ]:


# PAR APPELLATIONS

#LES CONTRATS 5 DERNIERES CAMPAGNES
contrats_all_spe_all = contrats.query('campagne in @campagne_5_completes')
contrats_all_spe_all= contrats_all_spe_all.groupby(["identifiant_vendeur","filtre_produit","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_all_spe_all.rename(columns = {'volume propose':'5 DA'}, inplace = True)


#LES CONTRATS DE LA CAMPAGNE COURANTE
contrats_annee_courante_spe_all = contrats.query('campagne in @campagne_courante')
contrats_annee_courante_spe_all = contrats_annee_courante_spe_all.groupby(["identifiant_vendeur","filtre_produit","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_annee_courante_spe_all.rename(columns = {'volume propose':'n'}, inplace = True)
contrats_annee_courante_spe_all = contrats_annee_courante_spe_all.sort_values(by=['n'], ascending=False)


#LES CONTRATS DE LA CAMPAGNE_PRECEDENTE n-1
contrats_annee_n_1_spe_all = contrats.query('campagne in @campagne_n_1')
contrats_annee_n_1_spe_all = contrats_annee_n_1_spe_all.groupby(["identifiant_vendeur","filtre_produit","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_annee_n_1_spe_all.rename(columns = {'volume propose':'n-1'}, inplace = True)


df_merge_spe_all = contrats_annee_courante_spe_all.merge(contrats_annee_n_1_spe_all,how = 'left',on=['identifiant_vendeur','filtre_produit','identifiant acheteur','nom_acheteur']).merge(contrats_all_spe_all,how = 'left',on=['identifiant_vendeur','filtre_produit','identifiant acheteur','nom_acheteur'])
df_merge_spe_all["couleur"] = "TOUT"
df_merge_spe_all = df_merge_spe_all.reset_index()
df_merge_spe_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

#df_merge_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

#LES CONTRATS 5 DERNIERES CAMPAGNES
contrats_all_all_all = contrats.query('campagne in @campagne_5_completes')
contrats_all_all_all= contrats_all_all_all.groupby(["identifiant_vendeur","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_all_all_all.rename(columns = {'volume propose':'5 DA'}, inplace = True)

#LES CONTRATS DE LA CAMPAGNE COURANTE
contrats_annee_courante_all_all = contrats.query('campagne in @campagne_courante')
contrats_annee_courante_all_all = contrats_annee_courante_all_all.groupby(["identifiant_vendeur","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_annee_courante_all_all.rename(columns = {'volume propose':'n'}, inplace = True)
contrats_annee_courante_all_all = contrats_annee_courante_all_all.sort_values(by=['n'], ascending=False)


#LES CONTRATS DE LA CAMPAGNE_PRECEDENTE n-1
contrats_annee_n_1_all_all = contrats.query('campagne in @campagne_n_1')
contrats_annee_n_1_all_all = contrats_annee_n_1_all_all.groupby(["identifiant_vendeur","identifiant acheteur","nom_acheteur"]).sum(["volume propose"])[["volume propose"]]
contrats_annee_n_1_all_all.rename(columns = {'volume propose':'n-1'}, inplace = True)

df_merge_all_all = contrats_annee_courante_all_all.merge(contrats_annee_n_1_all_all,how = 'left',on=['identifiant_vendeur','identifiant acheteur','nom_acheteur']).merge(contrats_all_all_all,how = 'left',on=['identifiant_vendeur','identifiant acheteur','nom_acheteur'])
df_merge_all_all["couleur"] = "TOUT"
df_merge_all_all["filtre_produit"] = "TOUT"
df_merge_all_all = df_merge_all_all.reset_index()

df_merge_all_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

#df_merge_all_all


# In[ ]:


#CONCATENATION DES 3 TABLEAUX :

df_final = pd.concat([df_merge_spe_spe, df_merge_spe_all])
df_final = pd.concat([df_final, df_merge_all_all])


df_final['n'] = round(df_final['n']).astype(int)
df_final["n-1"] = round(df_final["n-1"].fillna(0)).astype(int)

df_final["5 DA"] = df_final["5 DA"]/5
df_final["5 DA"] = round(df_final["5 DA"].fillna(0)).astype(int)

nom_col_n_1 = '<p class="text-end">Campagne '+lastcampagnes[-2:][0]+'</p>'
nom_col_5_DA = '<p class="text-end">Moyenne 5 dernières campagnes complètes</p>'

df_final[nom_col_n_1] = ((df_final["n"] - df_final['n-1']) / df_final['n-1'])*100
df_final[nom_col_5_DA] = ((df_final["n"] - df_final['5 DA']) / df_final['5 DA'])*100

df_final = df_final.round(1)

def addSign(v):
    if(v == float("inf")):
        return ""
    if(v >= 0):
        return "<span class='text-success'>"+'+'+str(v)+"%"
    else:
        return "<span class='text-danger'>"+str(v)+"%"

df_final[nom_col_n_1] = df_final[nom_col_n_1].map(addSign)
df_final[nom_col_5_DA] = df_final[nom_col_5_DA].map(addSign)

df_final[nom_col_n_1] = df_final[nom_col_n_1].astype(str)+' <div class="icone-info"><svg color="black" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-question-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/></svg><span class="icone-info-text">'+df_final['n-1'].astype(str)+" hl</span></div>"
df_final[nom_col_5_DA] = df_final[nom_col_5_DA].astype(str)+' <div class="icone-info"><svg color="black" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-question-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/></svg><span class="icone-info-text">'+df_final['5 DA'].astype(str)+" hl</span></div>"


df_final['n'] = df_final['n'].map('{:,.0f}'.format).replace(',', ' ', regex=True)+' hl'

df_final.rename(columns = {'n': '<p class="text-end">Campagne courante</p>' }, inplace = True)

if(negociant):
    df_final.rename(columns = {'nom_acheteur':'<p>Fournisseur</p>'}, inplace = True)
else :
    df_final.rename(columns = {'nom_acheteur':'<p>Acheteur</p>'}, inplace = True)

df_final = df_final.sort_values(by=['identifiant_vendeur','filtre_produit','couleur'])

df_final = df_final.drop(['identifiant acheteur','n-1','5 DA'], axis=1)


# In[ ]:


def create_table(df, identifiant, appellation, couleur):
    pd.set_option('display.max_colwidth', 40)
    html_table = df.to_html(index=False, justify='left',classes='table table-bordered text-end',escape=False)
    #print(html_table)
    dossier = dossier_graphes+"/"+identifiant+"/contrat/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()

    html_file = open(dossier+"/contrats-contractualisation-mes-clients-tableau-a-date.html","w")
    html_file.write(html_table)
    html_file.close()

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[bloc]
    create_table(df, bloc[0], bloc[1], bloc[2])

