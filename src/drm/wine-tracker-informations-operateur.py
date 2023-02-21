#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import argparse
import pathlib
from pathlib import Path
from datetime import datetime
import json

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
    
    import json
    
    # Data to be written
    dictionary ={
        "name" : nom,
        "date" : date
    }
    
    with open(dossier_graphes+id_operateur+"/"+id_operateur+".json", "w") as outfile:
        json.dump(dictionary, outfile)

    return


if(id_operateur):
    get_json(id_operateur,drm)
else:
    for identifiant in drm.identifiant.unique():
        get_json(identifiant,drm)

