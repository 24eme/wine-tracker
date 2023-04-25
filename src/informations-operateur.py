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
path = str(path).replace("src","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/drm/export_bi_drm_stock.csv"  #il manque un ; à la fin du header.
csv_contrats = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
csv_etablissements = path+"/data/contrats/export_bi_etablissements.csv" #il manque un ; à la fin du header.


# In[ ]:


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

drm = pd.read_csv(csv, sep=";",encoding="iso-8859-1", low_memory=False, index_col=False)
contrats = pd.read_csv(csv_contrats,sep=";",encoding="iso-8859-1", low_memory=False, index_col=False)


contrats_csv = contrats.copy()
contrats_csv['couleur'] = contrats_csv['couleur'].str.upper()

contrats_csv.rename(columns = {'identifiant vendeur':'identifiant_vendeur','volume propose (en hl)':'volume propose'}, inplace = True)

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
    

drm['libelle produit'] = drm['libelle produit'].str.replace('ï¿½','é') #problème d'encoddage.
contrats['libelle produit'] = contrats['libelle produit'].str.replace('ï¿½','é') #problème d'encoddage.

csv= drm.query("identifiant == @id_operateur").reset_index()

nom = csv.nom.unique()[0]
date = datetime.today().strftime('%d/%m/%Y')

csv['filtre_produits'] = csv['appellations'] + "-" + csv['lieux'] + "-" +csv['certifications']+ "-" +csv['genres']+ "-" +csv['mentions']+ "-" +csv['couleurs'].str.upper()

### CREATION DU TABLEAU ASSOCIATIF APPELLATION-LIBELLE ###

produits = csv[["filtre_produits","libelle produit"]]
produits = produits.drop_duplicates()
produits = produits.to_dict('records')

d = {}
for p in produits:
    if p["filtre_produits"] in d.keys():
        nb_caractere_ancien = len(d[p["filtre_produits"]])
        nb_caractere_nouveau = len(p["libelle produit"])
        if(nb_caractere_nouveau < nb_caractere_ancien):
            d[p["filtre_produits"]]=p["libelle produit"]
    else:
        d[p["filtre_produits"]]=p["libelle produit"]


produits = d

appellations = csv['appellations'] + "-" + csv['lieux'] + "-" +csv['certifications']+ "-" +csv['genres']+ "-" +csv['mentions']
appellations = appellations.unique()

couleurs = csv['couleurs'].str.upper().unique()

for element in appellations :
    if not element+"-1" in produits.keys():
        countNbColorForOneAppellation = 0;
        for couleur in couleurs :
            if(element+"-"+couleur in produits.keys()):
                countNbColorForOneAppellation +=1
                if(countNbColorForOneAppellation >= 2):
                    produitLibelle = produits[element+"-"+couleur].replace('é','e')
                    pattern = re.compile(couleur, re.IGNORECASE)
                    appellation = pattern.sub("",produitLibelle)
                    produits[element+"-1"] = appellation
                    break

produits = collections.OrderedDict(sorted(produits.items()))

update_produits = {"TOUT-TOUT": "Toutes les appellations"}
update_produits.update(produits)

produits = update_produits


#produits presents dans les contrats :

contrats.rename(columns = {'identifiant vendeur':'identifiant_vendeur'},inplace = True)

csv= contrats.query("identifiant_vendeur == @id_operateur").reset_index()
csv['filtre_produits'] = csv['appellation'] + "-" + csv['lieu'] + "-" +csv['certification']+ "-" +csv['genre']+ "-" +csv['mention']+ "-" +csv['couleur'].str.upper()

produits_contrat = csv[["filtre_produits","libelle produit"]]
produits_contrat = produits_contrat.drop_duplicates()
produits_contrat = produits_contrat.to_dict('records')

d = {}
for p in produits_contrat:
    if p["filtre_produits"] in d.keys():
        nb_caractere_ancien = len(d[p["filtre_produits"]])
        nb_caractere_nouveau = len(p["libelle produit"])
        if(nb_caractere_nouveau < nb_caractere_ancien):
            d[p["filtre_produits"]]=p["libelle produit"]
    else:
        d[p["filtre_produits"]]=p["libelle produit"]


produits_contrat = d

appellations = csv['appellation'] + "-" + csv['lieu'] + "-" +csv['certification']+ "-" +csv['genre']+ "-" +csv['mention']
appellations = appellations.unique()

couleurs = csv['couleur'].str.upper().unique()


for element in appellations :
    if not element+"-1" in produits_contrat.keys():
        countNbColorForOneAppellation = 0;
        for couleur in couleurs :
            if (element+"-"+couleur in produits_contrat.keys()):
                countNbColorForOneAppellation +=1
                if(countNbColorForOneAppellation >= 2):
                    produitLibelle = produits_contrat[element+"-"+couleur].replace('é','e')
                    pattern = re.compile(couleur, re.IGNORECASE)
                    appellation = pattern.sub("",produitLibelle)
                    produits_contrat[element+"-1"] = appellation
                    break

produits_contrat = collections.OrderedDict(sorted(produits_contrat.items()))
produits_contrat = json.loads(json.dumps(produits_contrat))

update_produits = {"TOUT-TOUT": "Toutes les appellations"}
update_produits.update(produits_contrat)

produits_contrat = update_produits

### FIN CREATION DU TABLEAU ###

dictionary ={
    "name" : nom,
    "date" : date,
    "produits": {"drm" :produits,"contrats": produits_contrat}
}


dossier = dossier_graphes+id_operateur
pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)

with open(dossier+"/"+id_operateur+".json", "w") as outfile:
    json.dump(dictionary, outfile)

