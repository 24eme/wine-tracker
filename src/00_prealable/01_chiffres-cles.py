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
from dateutil.relativedelta import relativedelta


# In[ ]:


date = datetime.today()
#date = datetime(2023, 7, 31)
date = date.replace(year=date.year - 1).isoformat()


# In[ ]:


path = pathlib.Path().absolute()
path = str(path).replace("/src","").replace("/00_prealable","")
dossier_graphes=path+"/graphes/"
csv_contrats = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
csv_etablissements = path+"/data/contrats/export_bi_etablissements.csv" #il manque un ; à la fin du header.
csv_mouvements = path+"/data/drm/export_bi_mouvements.csv"


# In[ ]:


chiffres = pd.DataFrame()


# In[ ]:


filtre_operateur=None

parser = argparse.ArgumentParser()
parser.add_argument("filtre_operateur", help="Identifiant opérateur", default=filtre_operateur, nargs='?')

try:
    args = parser.parse_args()
    filtre_operateur = args.filtre_operateur
except:
    True


# In[ ]:


mouvements = pd.read_csv(csv_mouvements, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)
mouvements = mouvements[mouvements['genre'] != 'VCI']
mouvements = mouvements[mouvements['libelle type'] == 'Suspendu']
mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-2:]

if filtre_operateur:
    mouvements = mouvements.query("identifiant == @filtre_operateur").reset_index()

mouvements = mouvements.query('campagne in @lastcampagnes')
mouvements = mouvements.query("appellation != 'CDP'")

mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)
typedemouvements = ['sorties/vrac','sorties/crd', 'sorties/factures', 'sorties/export','sorties/acq_crd','sorties/consommation']
mouvements = mouvements.query("type_de_mouvement in @typedemouvements").reset_index()

mouvements['mois'] = mouvements['periode'].apply(lambda x: (int(x.split('-')[1]) + 4) % 12)


# In[ ]:


#Forcer le tableau de sorties à avoir tous les opérateurs
chiffres['identifiant_mouvements'] = mouvements.identifiant.unique()
chiffres.set_index('identifiant_mouvements', inplace = True)


# In[ ]:


#Sorties du cumul campagne complete
campagne_n_1 = lastcampagnes[-2]
sorties = mouvements.query("campagne==@campagne_n_1")
sorties = sorties.groupby(["identifiant"]).agg({'periode': max,  'volume mouvement': sum})

mois_en_cours = pd.DataFrame()
mois_en_cours['mois'] = sorties['periode'].apply(lambda x: (int(x.split('-')[1]) + 4) % 12)
mois_en_cours.reset_index(inplace=True)
chiffres['cumul_sortie_campagne_n_1'] = sorties['volume mouvement']


# In[ ]:


#Sorties du cumul de la campagne précédente à date
sorties = mouvements.query("campagne==@campagne_n_1")

sorties["a_date"] = (sorties['date mouvement'] <= date)
sorties = sorties.query("a_date==True")
sorties = sorties.groupby(["identifiant"]).agg({'periode': max,  'volume mouvement': sum})

mois_en_cours = pd.DataFrame()
mois_en_cours['mois'] = sorties['periode'].apply(lambda x: (int(x.split('-')[1]) + 4) % 12)
mois_en_cours.reset_index(inplace=True)
chiffres['cumul_sortie_campagne_n_1_a_date'] = sorties['volume mouvement']


# In[ ]:


#Sorties du cumul campagne actuelle

campagne_courante = lastcampagnes[-1]
sorties = mouvements.query("campagne==@campagne_courante")
sorties = sorties.groupby(["identifiant"]).agg({'periode': max,  'volume mouvement': sum, 'date mouvement' : max})
mois_en_cours = pd.DataFrame()
mois_en_cours['mois'] = sorties['periode'].apply(lambda x: (int(x.split('-')[1]) + 4) % 12)
mois_en_cours.reset_index(inplace=True)
chiffres['cumul_sortie_campagne_en_cours'] = sorties['volume mouvement']

#Evolution à date
chiffres['evolution_cumul_sortie_campagne_en_cours'] = (sorties['volume mouvement'] - chiffres['cumul_sortie_campagne_n_1_a_date']) * 100 / chiffres['cumul_sortie_campagne_n_1_a_date']

#date de la dernière validation de mouvement du tableau.
chiffres['last_date_validation_campagne_en_cours'] = sorties['date mouvement'].map(lambda f: pd.to_datetime(f).strftime('%d/%m/%Y'))


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


contrats = pd.read_csv(csv_contrats,sep=";",encoding="iso-8859-1", low_memory=False, index_col=False)
contrats = contrats.query("statut == 'SOLDE' or statut == 'NONSOLDE'")
contrats = contrats.query("appellation != 'CDP'")

contrats.rename(columns = {'type de vente':'type_de_vente','date de validation':'date_validation'}, inplace = True)
contrats = contrats.query("type_de_vente == 'vrac'")
contrats['libelle produit'] = contrats['libelle produit'].str.replace('ï¿½','é') #problème d'encoddage.
contrats['date_validation'] = pd.to_datetime(contrats['date_validation'], utc=True)
contrats['date_validation'] = contrats['date_validation'].map(datetime.date)

chiffres['last_date_validation_contrat']  = contrats['date_validation'].max().strftime("%d/%m/%Y")

#changement de la campagne en fonction de la date de validation
contrats['campagne']  = contrats['date_validation'].apply(lambda v: str((v - relativedelta(months=7)).year)+"-"+str((v - relativedelta(months=7)).year+1) )

contrats['date_validation'] = contrats['date_validation'].apply(lambda x: x.isoformat())


#TOUTE LA CAMPAGNE PRECEDENTE JUSQU'A DATE
contrat_passe = contrats.query('campagne == @campagne_n_1 and date_validation<=@date')
contrat_extract = pd.concat([
    contrat_passe[contrat_passe['identifiant acheteur'].isin(acheteurs['identifiant'])][['identifiant acheteur', 'libelle produit', 'volume propose (en hl)']].rename(columns = {'identifiant acheteur' : 'identifiant'}),
    contrat_passe[contrat_passe['identifiant vendeur'].isin(vendeurs['identifiant'])][['identifiant vendeur', 'libelle produit', 'volume propose (en hl)']].rename(columns = {'identifiant vendeur' : 'identifiant'})
])

chiffres['volume_contractualisation_n_1'] = contrat_extract.groupby(['identifiant'])['volume propose (en hl)'].sum()

#CAMPAGNE ACTUELLE
contrats = contrats.query('campagne==@campagne_courante')
contrat_extract = pd.concat([
    contrats[contrats['identifiant acheteur'].isin(acheteurs['identifiant'])][['identifiant acheteur', 'libelle produit', 'volume propose (en hl)']].rename(columns = {'identifiant acheteur' : 'identifiant'}),
    contrats[contrats['identifiant vendeur'].isin(vendeurs['identifiant'])][['identifiant vendeur', 'libelle produit', 'volume propose (en hl)']].rename(columns = {'identifiant vendeur' : 'identifiant'})
])

chiffres['volume_contractualisation'] = contrat_extract.groupby(['identifiant'])['volume propose (en hl)'].sum()

chiffres['evolution_par_rapport_a_n_1'] = (chiffres['volume_contractualisation'] - chiffres['volume_contractualisation_n_1']) * 100 / chiffres['volume_contractualisation_n_1']
chiffres["date_generation"] = datetime.today().strftime("%d/%m/%Y")


# In[ ]:


chiffres.fillna(0, inplace=True)
#chiffres


# In[ ]:


for id_operateur in chiffres.index:
    dossier = dossier_graphes+id_operateur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).touch()

    with open(dossier+"/"+id_operateur+"_chiffre.json", "w") as outfile:
        outfile.write(chiffres.loc[id_operateur].to_json())
        outfile.close()

