#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import argparse
import pathlib
from pathlib import Path
from datetime import datetime
import json
import re
import collections


path = pathlib.Path().absolute()
path = str(path).replace("/src","").replace('/00_prealable','')
dossier_graphes=path+"/graphes/"
csv = path+"/data/drm/export_bi_drm_stock.csv"  #il manque un ; à la fin du header.
csv_contrats = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
csv_etablissements = path+"/data/contrats/export_bi_etablissements.csv" #il manque un ; à la fin du header.


# In[ ]:


filter_operateur=None

parser = argparse.ArgumentParser()
parser.add_argument("filter_operateur", help="Identifiant opérateur", default=filter_operateur, nargs='?')

try:
    args = parser.parse_args()
    filter_operateur = args.id_operateur
except:
    True


# In[ ]:


etablissements = pd.read_csv(csv_etablissements, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)
etablissements['familles'] = etablissements['famille'].str.split(' ')
etablissements['famille_ok'] = etablissements['familles'].apply(lambda f: f[0] != 'courtier' and ((f[0] == 'producteur') and (f[1] == 'cave_particuliere' or f[1] == 'cave_cooperative')) or (f[0] in ['negociant', 'cave cooperative']))
etablissements = etablissements[etablissements['famille_ok']]
etablissements['famille'] = etablissements['familles'].apply(lambda f: f[0])

etablissements = etablissements[['identifiant','famille', 'raison sociale']]

vendeurs = etablissements[etablissements['famille'] == 'producteur']
acheteurs = etablissements[etablissements['famille'] != 'producteur']


# In[ ]:


drm = pd.read_csv(csv, sep=";",encoding="iso-8859-1", low_memory=False, index_col=False)
if filter_operateur:
    drm = drm.query("identifiant == @filter_operateur")
drm['libelle produit'] = drm['libelle produit'].str.replace('ï¿½','é') #problème d'encoddage.
drm = drm[drm['genres'] != 'VCI']
drm = drm.loc[drm['appellations'] != "CDP"]

contrats = pd.read_csv(csv_contrats,sep=";",encoding="iso-8859-1", low_memory=False, index_col=False)
if filter_operateur:
    contrats = pd.concat([
        contrats[contrats['identifiant acheteur'] == filter_operateur],
        contrats[contrats['identifiant vendeur'] == filter_operateur]
    ])
contrats['libelle produit'] = contrats['libelle produit'].str.replace('ï¿½','é') #problème d'encoddage.
contrats = contrats.loc[contrats['appellation'] != "CDP"]


# In[ ]:


drm = drm[['identifiant', 'appellations', 'lieux', 'certifications', 'genres', 'mentions', 'couleurs', 'libelle produit']].drop_duplicates()

drm['filtre_produits'] = drm[['appellations', 'lieux', 'certifications', 'genres', 'mentions', 'couleurs']].apply(lambda rows: '-'.join(rows.values.astype('str')).upper(), axis=1)
drm['filtre_appellations'] = drm[['appellations', 'lieux', 'certifications', 'genres', 'mentions']].apply(lambda rows: '-'.join(rows.values.astype('str'))+'-0TOUT', axis=1)
drm['libelle_appellations'] = drm['libelle produit'].str.split().apply(lambda libelles: re.sub(r' (rouge|blanc|rosé).*', '', ' '.join(libelles), flags=re.I))
drm['libelle produit'] = drm['libelle produit'].apply(lambda libelle: re.sub(r' (rouge|blanc|rosé).*', r' \g<1>', libelle, flags=re.I))

drm_tout = pd.DataFrame()
drm_tout['identifiant'] = drm['identifiant']
drm_tout['filtre_produits'] = '0TOUT-TOUT'
drm_tout['libelle produit'] = 'Toutes les appellations'

drm_produits = pd.concat([
    drm[['identifiant', 'filtre_produits', 'libelle produit']],
    drm[['identifiant', 'filtre_appellations', 'libelle_appellations']].rename(columns = {'libelle_appellations': 'libelle produit', 'filtre_appellations': 'filtre_produits'}),
    drm_tout
]).sort_values(['identifiant', 'filtre_produits']).drop_duplicates()
drm_produits['type'] = 'drm'

drm_produits = drm_produits.set_index(['identifiant', 'filtre_produits', 'libelle produit'])
drm_produits['nb_produits'] = drm.set_index(['identifiant', 'appellations', 'lieux', 'certifications', 'genres', 'mentions', 'couleurs']).groupby(['identifiant','filtre_appellations','libelle_appellations'])[['filtre_produits']].count().reset_index().rename(columns={'filtre_produits': 'nb_produits', 'filtre_appellations': 'filtre_produits', 'libelle_appellations': 'libelle produit'}).set_index(['identifiant', 'filtre_produits', 'libelle produit'])
drm_produits.fillna(0, inplace=True)

drm_produits = drm_produits[drm_produits['nb_produits'] != 1][['type']].reset_index()


# In[ ]:


contrat_extract = pd.concat([
    contrats[contrats['identifiant acheteur'].isin(acheteurs['identifiant'])][['identifiant acheteur','certification', 'genre', 'appellation', 'mention','lieu', 'couleur', 'cepage', 'libelle produit']].rename(columns = {'identifiant acheteur' : 'identifiant'}),
    contrats[contrats['identifiant vendeur'].isin(vendeurs['identifiant'])][['identifiant vendeur','certification', 'genre', 'appellation', 'mention','lieu', 'couleur', 'cepage', 'libelle produit']].rename(columns = {'identifiant vendeur' : 'identifiant'})
]).drop_duplicates()

contrat_extract['couleur'] = contrat_extract['couleur'].str.upper()
contrat_extract['filtre_produits'] = contrat_extract[['appellation', 'lieu', 'certification', 'genre', 'mention', 'couleur']].apply(lambda rows: '-'.join(rows.values.astype('str')).upper(), axis=1)
contrat_extract['filtre_appellations'] = contrat_extract[['appellation', 'lieu', 'certification', 'genre', 'mention']].apply(lambda rows: '-'.join(rows.values.astype('str'))+'-0TOUT', axis=1)
contrat_extract['libelle_appellations'] = contrat_extract['libelle produit'].str.split().apply(lambda libelles: re.sub(r' (rouge|blanc|rosé).*', '', ' '.join(libelles), flags=re.I))
contrat_extract['libelle produit'] = contrat_extract['libelle produit'].apply(lambda libelle: re.sub(r' (rouge|blanc|rosé).*', r' \g<1>', libelle, flags=re.I))

contrat_tout = pd.DataFrame()
contrat_tout['identifiant'] = contrat_extract['identifiant']
contrat_tout['filtre_produits'] = '0TOUT-TOUT'
contrat_tout['libelle produit'] = 'Toutes les appellations'

contrat_produits = pd.concat([
    contrat_extract[['identifiant', 'filtre_produits', 'libelle produit']],
    contrat_extract[['identifiant', 'filtre_appellations', 'libelle_appellations']].rename(columns = {'libelle_appellations': 'libelle produit', 'filtre_appellations': 'filtre_produits'}),
    contrat_tout
]).sort_values(['identifiant', 'filtre_produits']).drop_duplicates()
contrat_produits['type'] = 'contrat'

contrat_produits = contrat_produits.set_index(['identifiant', 'filtre_produits', 'libelle produit'])
contrat_produits['nb_produits'] = contrat_extract.set_index(['identifiant', 'appellation', 'lieu', 'certification', 'genre', 'mention', 'couleur']).groupby(['identifiant','filtre_appellations','libelle_appellations'])[['filtre_produits']].count().reset_index().rename(columns={'filtre_produits': 'nb_produits', 'filtre_appellations': 'filtre_produits', 'libelle_appellations': 'libelle produit'}).set_index(['identifiant', 'filtre_produits', 'libelle produit'])
contrat_produits.fillna(0, inplace=True)

contrat_produits = contrat_produits[contrat_produits['nb_produits'] != 1][['type']].reset_index()


# In[ ]:


produits = pd.concat([drm_produits, contrat_produits]).set_index(['identifiant'])
produits['filtre_produits'] = produits['filtre_produits'].apply(lambda s: s.replace('0TOUT', 'TOUT'))


# In[ ]:


date = datetime.today().strftime('%d/%m/%Y')

for id_operateur in produits.index.unique():
    
    df = produits.loc[[id_operateur]]
    
    drm = {}
    for [filtre, libelle] in df[df['type'] == 'drm'][['filtre_produits', 'libelle produit']].values:
        drm[filtre] = libelle

    contrats = {}
    for [filtre, libelle] in df[df['type'] == 'contrat'][['filtre_produits', 'libelle produit']].values:
        contrats[filtre] = libelle
    
    rs = etablissements[etablissements['identifiant'] == id_operateur]['raison sociale']
    if len(rs.values):
        rs = rs.values[0]
    else:
        continue
    
    dictionary ={
        "name" : rs,
        "date" : date,
        "produits": {"drm" : drm, "contrats": contrats},
        "is_producteur": not id_operateur in acheteurs.index,
        "is_negociant": id_operateur in acheteurs.index
    }

    dossier = dossier_graphes+id_operateur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).touch()

    with open(dossier+"/"+id_operateur+".json", "w") as outfile:
        json.dump(dictionary, outfile)


# In[ ]:




