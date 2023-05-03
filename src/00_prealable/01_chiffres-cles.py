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


# In[ ]:


path = pathlib.Path().absolute()
path = str(path).replace("src","")
dossier_graphes=path+"/graphes/"
csv_contrats = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
csv_etablissements = path+"/data/contrats/export_bi_etablissements.csv" #il manque un ; à la fin du header.
csv_mouvements = path+"/data/drm/export_bi_mouvements.csv"


# In[ ]:


chiffre1 = 0
chiffre2 = 0
chiffre3 = 0
chiffre4 = 0
chiffre5 = 0
chiffre6 = 0
chiffre7 = 0
chiffre8 = 0


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


mouvements = pd.read_csv(csv_mouvements, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-2:]

mois = { "08" : "Août" , "09" : "Septembre", "10" : "Octobre", "11" : "Novembre" , "12" : "Décembre",
        "01" : "Janvier", "02" : "Février", "03" : "Mars", "04" : "Avril", "05" : "Mai", "06" : "Juin",
        "07" : "Juillet" }

mois_sort = { "Août" : "01" , "Septembre" : "02", "Octobre" : "03", "Novembre" : "04" , "Décembre" : "05",
        "Janvier" : "06", "Février" : "07", "Mars" : "08", "Avril" : "09", "Mai" : "10", "Juin" : "11",
        "Juillet" : "12" }

mouvements = mouvements.query('campagne in @lastcampagnes')
mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)
mouvements = mouvements.query("identifiant == @id_operateur").reset_index()

mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)
typedemouvements = ['sorties/vrac', 'sorties/crd', 'sorties/factures', 'sorties/export','sorties/consommation']
mouvements = mouvements.query("type_de_mouvement in @typedemouvements").reset_index()

lastMonth = format(datetime.now().month-1, "02d")
lastMonthFrench = mois[lastMonth]
lastMonthOrdre = mois_sort[lastMonthFrench].replace("0", "")

currentMonth = format(datetime.now().month, "02d")
currentMonthFrench = mois[currentMonth]
currentMonthOrdre = mois_sort[currentMonthFrench].replace("0", "")


# In[ ]:


#Sorties du cumul campagne (peut être annualisé sur 12 mois)

campagne_courante = lastcampagnes[-1:][0]
sorties = mouvements.query("campagne==@campagne_courante")
sorties = sorties.groupby(["identifiant",'campagne','periode']).sum(["volume mouvement"])[["volume mouvement"]]
sorties = sorties.reset_index()
sorties.set_index(['identifiant'], inplace = True)
sorties['mois'] = sorties["periode"].str.extract('.*(\d{2})', expand = False)
sorties['mois'] = sorties['mois'].map(mois,na_action=None)
sorties['ordre_mois']= sorties['mois'].map(mois_sort,na_action=None)

sorties_all_all = sorties.groupby(["identifiant",'campagne','periode',"mois","ordre_mois"]).sum(["volume mouvement"])[["volume mouvement"]]
sorties_all_all = sorties_all_all.reset_index()
sorties_all_all['volume cumule'] = sorties_all_all.groupby(["identifiant","campagne"])['volume mouvement'].cumsum()

if(len(sorties_all_all.index) > 0):
    chiffre1 = sorties_all_all["volume cumule"].iat[len(sorties_all_all)-1]
    chiffre1 = round(chiffre1)
#chiffre1


# In[ ]:


#Evolution mois par rapport au mois à n-1
campagne_courante_n_1 = lastcampagnes[-2:][0]
sorties = mouvements.query("campagne==@campagne_courante_n_1")
sorties = sorties[sorties['libelle type'] == 'Suspendu']

sorties = sorties.groupby(["identifiant",'campagne','periode']).sum(["volume mouvement"])[["volume mouvement"]]
sorties = sorties.reset_index()
sorties.set_index(['identifiant'], inplace = True)
sorties['mois'] = sorties["periode"].str.extract('.*(\d{2})', expand = False)
sorties['mois'] = sorties['mois'].map(mois,na_action=None)
sorties['ordre_mois']= sorties['mois'].map(mois_sort,na_action=None)

sorties_all_all = sorties.groupby(["identifiant",'campagne','periode',"mois","ordre_mois"]).sum(["volume mouvement"])[["volume mouvement"]]
sorties_all_all = sorties_all_all.reset_index()
sorties_all_all['volume cumule'] = sorties_all_all.groupby(["identifiant","campagne"])['volume mouvement'].cumsum()


chiffre2 = sorties_all_all["volume cumule"].iat[int(lastMonthOrdre)-1]
if(len(sorties_all_all.index) > 0):
    chiffre2 = (((chiffre1-chiffre2)/chiffre2))*100
    chiffre2 = round(chiffre2)
    if(chiffre2 > 0):
        chiffre2 = '+'+str(chiffre2)

#chiffre2


# In[ ]:


mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)


# In[ ]:


#Volume de sortie vrac hl du mois courant 

typedemouvementsvracs = ['sorties/vrac']
vrac = mouvements.query("type_de_mouvement in @typedemouvementsvracs and campagne==@campagne_courante")
vrac = vrac.groupby(["identifiant",'campagne','periode']).sum(["volume mouvement"])[["volume mouvement"]]
vrac = vrac.reset_index()
vrac.set_index(['identifiant'], inplace = True)

vrac['mois'] = vrac["periode"].str.extract('.*(\d{2})', expand = False)
vrac['mois'] = vrac['mois'].map(mois,na_action=None)
vrac['ordre_mois']= vrac['mois'].map(mois_sort,na_action=None)

last_month_ordre = format(int(lastMonthOrdre), "02d")
vrac = vrac.query("ordre_mois==@last_month_ordre")

if(len(vrac.index) > 0):
    chiffre3 = vrac["volume mouvement"][0]
    chiffre3 = round(chiffre3)

#chiffre3


# In[ ]:


#Evolution sortie vrac du mois par rapport à A n-1
vrac = mouvements.query("type_de_mouvement in @typedemouvementsvracs and campagne==@campagne_courante_n_1")
vrac = vrac.groupby(["identifiant",'campagne','periode']).sum(["volume mouvement"])[["volume mouvement"]]
vrac = vrac.reset_index()
vrac.set_index(['identifiant'], inplace = True)

vrac['mois'] = vrac["periode"].str.extract('.*(\d{2})', expand = False)
vrac['mois'] = vrac['mois'].map(mois,na_action=None)
vrac['ordre_mois']= vrac['mois'].map(mois_sort,na_action=None)

last_month_ordre = format(int(lastMonthOrdre), "02d")
vrac = vrac.query("ordre_mois==@last_month_ordre")

if(len(vrac.index) > 0):
    chiffre4 = vrac["volume mouvement"][0]
    chiffre4 = (((chiffre3-chiffre4)/chiffre4))*100
    chiffre4 = round(chiffre4)
    if(chiffre4 > 0):
        chiffre4 = '+'+str(chiffre4)
#chiffre4


# In[ ]:


#Volume sortie conditionné mois
typedemouvementsconditionne = ['sorties/crd', 'sorties/factures', 'sorties/export']
conditionne = mouvements.query("type_de_mouvement in @typedemouvementsconditionne and campagne==@campagne_courante")
conditionne = conditionne.groupby(["identifiant",'campagne','periode']).sum(["volume mouvement"])[["volume mouvement"]]
conditionne = conditionne.reset_index()
conditionne.set_index(['identifiant'], inplace = True)

conditionne['mois'] = conditionne["periode"].str.extract('.*(\d{2})', expand = False)
conditionne['mois'] = conditionne['mois'].map(mois,na_action=None)
conditionne['ordre_mois']= conditionne['mois'].map(mois_sort,na_action=None)

last_month_ordre = format(int(lastMonthOrdre), "02d")
conditionne = conditionne.query("ordre_mois==@last_month_ordre")

if(len(conditionne.index) > 0):

    chiffre5 = conditionne["volume mouvement"][0]
    chiffre5 = round(chiffre5)

#chiffre5


# In[ ]:


#Evolution sortie conditionné du mois
conditionne = mouvements.query("type_de_mouvement in @typedemouvementsconditionne and campagne==@campagne_courante_n_1")
conditionne = conditionne.groupby(["identifiant",'campagne','periode']).sum(["volume mouvement"])[["volume mouvement"]]
conditionne = conditionne.reset_index()
conditionne.set_index(['identifiant'], inplace = True)

conditionne['mois'] = conditionne["periode"].str.extract('.*(\d{2})', expand = False)
conditionne['mois'] = conditionne['mois'].map(mois,na_action=None)
conditionne['ordre_mois']= conditionne['mois'].map(mois_sort,na_action=None)

last_month_ordre = format(int(lastMonthOrdre), "02d")
conditionne = conditionne.query("ordre_mois==@last_month_ordre")

if(len(conditionne.index) > 0):
    chiffre6 = conditionne["volume mouvement"][0]
    chiffre6 = (((chiffre5-chiffre6)/chiffre6))*100
    chiffre6 = round(chiffre6)
    if(chiffre6 > 0):
        chiffre6 = '+'+str(chiffre6)
#chiffre6


# In[ ]:


etablissements = pd.read_csv(csv_etablissements, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)
etablissement = etablissements.query("identifiant == @id_operateur")
famille = etablissement['famille'].unique()[0]

if not famille:
    raise Exception("OPERATEUR N'EST PAS DANS LE CSV DES ETABLISSEMENT")

contrats = pd.read_csv(csv_contrats,sep=";",encoding="iso-8859-1", low_memory=False, index_col=False)

contrats = contrats.query("statut == 'SOLDE' or statut == 'NONSOLDE'")
contrats.rename(columns = {'type de vente':'type_de_vente'}, inplace = True)
contrats = contrats.query("type_de_vente == 'vrac'")

contrats_csv = contrats.copy()
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


contrats['libelle produit'] = contrats['libelle produit'].str.replace('ï¿½','é') #problème d'encoddage.
contrats = contrats.query('campagne in @lastcampagnes')
contrats['date de validation'] = pd.to_datetime(contrats['date de validation'], utc=True)

contrat_mois_sort = { 8 : "01" , 9 : "02", 10 : "03", 11 : "04" , 12 : "05", 1 : "06", 2 : "07", 3 : "08", 4 : "09", 5 : "10", 6 : "11",7 : "12" }

contrats['mois'] = contrats['date de validation'].dt.month
contrats['ordre_mois']= contrats['mois'].map(contrat_mois_sort,na_action=None)


# In[ ]:


#Contractualisation
contrats_courants = contrats.query("campagne==@campagne_courante")
ordre_mois_courant_n_1 = contrat_mois_sort[datetime.now().month-1];
contrats_n_1 = contrats.query("campagne==@campagne_courante_n_1 and ordre_mois <= @ordre_mois_courant_n_1")

if(len(contrats_n_1.index) > 0):
    chiffre7 = contrats_courants['volume propose'].sum()
    chiffre7 = round(chiffre7)
#chiffre7


# In[ ]:


#Evolution contractualisation n-1
contrats_n_1 = contrats.query("campagne==@campagne_courante_n_1 and ordre_mois <= @ordre_mois_courant_n_1")
if(len(contrats_n_1.index) > 0):
    chiffre8 = contrats_n_1['volume propose'].sum()
    chiffre8 = (((chiffre7-chiffre8)/chiffre8))*100
    chiffre8 = round(chiffre8)
    if(chiffre8 > 0):
        chiffre8 = '+'+str(chiffre8)
#chiffre8


# In[ ]:


dictionary ={
    "cumul_sortie_campagne_en_cours" : chiffre1,
    "evolution_mois_par_rapport_a_n_1": chiffre2,
    "volume_de_sortie_vrac": chiffre3,
    "evolution_sorite_vrac_mois_par_rapport_a_n_1" : chiffre4,
    "volume_sortie_conditionne_mois" : chiffre5,
    "evolution_sortie_conditionne_du_mois" : chiffre6,
    "volume_contractualisation" : chiffre7,
    "evolution_par_rapport_a_n_1" : chiffre8
}

dossier = dossier_graphes+id_operateur
pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
pathlib.Path(dossier).touch()

with open(dossier+"/"+id_operateur+"_chiffre.json", "w") as outfile:
    json.dump(dictionary, outfile)

