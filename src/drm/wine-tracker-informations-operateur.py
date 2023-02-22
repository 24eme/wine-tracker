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

path = pathlib.Path().absolute()
path = str(path).replace("src/drm","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/drm/export_bi_drm_stock.csv"  #il manque un ; à la fin du header.


# In[ ]:


id_operateur=None

parser = argparse.ArgumentParser()
parser.add_argument("id_operateur", help="Identifiant opérateur", default=id_operateur, nargs='?')

try:
   args = parser.parse_args()
   id_operateur = args.id_operateur
except:
   print("Arguments pas défaut")


# In[ ]:


#creation d'un fichier json par operateur
drm = pd.read_csv(csv, sep=";",encoding="utf-8")

def get_json(id_operateur,csv):
    csv= csv.query("identifiant == @id_operateur").reset_index()
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
        if not element+"-TOUT" in produits.keys():
            for couleur in couleurs :
                if(element+"-"+couleur in produits.keys()):
                    pattern = re.compile(couleur, re.IGNORECASE)
                    appellation = pattern.sub("",produits[element+"-"+couleur])
                    produits[element+"-TOUT"] = appellation
                    break

    produits["TOUT-TOUT"] = "Toutes les appellations"

    final = {}
    for prod in produits:
        appellation = re.findall(r'(.+)-(.+)',prod)[0][0]
        couleur = re.findall(r'(.+)-(.+)',prod)[0][1]

        if appellation not in final.keys():
            final[appellation] = {}

        if (couleur == "TOUT" and len(final[appellation].keys()) == 1):
            continue

        final[appellation][appellation+"-"+couleur] = produits[prod]

    produits = final

    ### FIN CREATION DU TABLEAU ###

    dictionary ={
        "name" : nom,
        "date" : date,
        "produits": produits
    }

    with open(dossier_graphes+id_operateur+"/"+id_operateur+".json", "w") as outfile:
        json.dump(dictionary, outfile)

    return

if(id_operateur):
    get_json(id_operateur,drm)
else:
    for identifiant in drm.identifiant.unique():
        get_json(identifiant,drm)

