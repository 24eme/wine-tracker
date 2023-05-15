#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib

path = pathlib.Path().absolute()
path = str(path).replace("/src","").replace("/02_contrat","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
csv_etablissements = path+"/data/contrats/export_bi_etablissements.csv" #il manque un ; à la fin du header.
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
contrats["Chiffre d'affaire"] = contrats['prix unitaire (en hl)'] * contrats['volume propose (en hl)']

contrats.rename(columns = {'type de vente':'type_de_vente'}, inplace = True)


contrats = contrats.query("type_de_vente == 'vrac'")
contrats = contrats.query("appellation != 'CDP'")

lastcampagnes = contrats['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[:-1][-5:]

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


# In[ ]:


# PAR APPELLATION ET COULEUR

contrats['filtre_produit'] = contrats['appellation'] + "-" + contrats['lieu'] + "-" +contrats['certification']+ "-" +contrats['genre']+ "-" +contrats['mention']

contrats_spe_spe = contrats.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume propose","Chiffre d'affaire"])[["volume propose","Chiffre d'affaire"]]

contrats_spe_spe = contrats_spe_spe.reset_index(level='identifiant acheteur')
contrats_spe_spe = contrats_spe_spe.reset_index(level='nom_acheteur')

#contrats_spe_spe

# PAR APPELLATIONS


contrats_spe_all = contrats_spe_spe.groupby(["identifiant_vendeur","filtre_produit",'identifiant acheteur',"nom_acheteur"]).sum(["volume propose","Chiffre d'affaire"])[["volume propose","Chiffre d'affaire"]]
contrats_spe_all["couleur"] = "TOUT"
contrats_spe_all = contrats_spe_all.reset_index()
contrats_spe_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

#contrats_spe_all

#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS


contrats_all_all = contrats_spe_spe.groupby(["identifiant_vendeur",'identifiant acheteur',"nom_acheteur"]).sum(["volume propose","Chiffre d'affaire"])[["volume propose","Chiffre d'affaire"]]
contrats_all_all["couleur"] = "TOUT"
contrats_all_all["filtre_produit"] = "TOUT"
contrats_all_all = contrats_all_all.reset_index()

contrats_all_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)

#contrats_all_all


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([contrats_spe_spe, contrats_spe_all])
df_final = pd.concat([df_final, contrats_all_all])

df_final = df_final.sort_values(by=['identifiant_vendeur','filtre_produit','couleur'])

df_final.rename(columns = {'volume propose':'volume'}, inplace = True)
df_final.rename(columns = {'nom_acheteur':"Client"}, inplace = True)


df_final['volume'] = round(df_final['volume']/len(lastcampagnes)).astype(int)
df_final["Chiffre d'affaire"] = round(df_final["Chiffre d'affaire"]/len(lastcampagnes)).astype(int)

#df_final


# In[ ]:


def format_hl(x):
    x = "{:,.0f}".format(x)
    x = str(x).replace(","," ")+" hl"
    return x

def format_euro(x):
    x = "{:,.0f}".format(x)
    x = str(x).replace(","," ")+" €"
    return x


# In[ ]:


def create_graphe(df, identifiant, appellation, couleur):
    fig = px.pie(df, values='volume', names='Client',custom_data=['Client','volume','commune'], color_discrete_sequence=px.colors.sequential.Agsunset, width=1250, height=650)
    fig.update_traces(textposition='inside', textinfo='label+text', text=(df['volume'].map(format_hl)))
    fig.update_layout(legend_font_size=15)
    fig.update_yaxes(tickformat=",")
    fig.update_layout(separators=". .*")
    fig.update_traces(
    hovertemplate="<br>".join([
        "%{customdata[0][0]}",
        "%{customdata[0][2]}",
        "%{customdata[0][1]:,} hl",
        "%{percent}"
    ])
    )

    #fig.show()

    dossier = dossier_graphes+"/"+identifiant+"/contrat/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()

    fig.write_html(dossier+"/contrats-contractualisation-mes-clients-en-hl.html",include_plotlyjs=False)

    fig = px.pie(df, values="Chiffre d'affaire", names='Client',custom_data=['Client', "Chiffre d'affaire",'commune'], color_discrete_sequence=px.colors.sequential.Agsunset, width=1250, height=650)
    fig.update_traces(textposition='inside', textinfo='label+text', text=(df["Chiffre d'affaire"].map(format_euro)))
    fig.update_yaxes(tickformat=",")
    fig.update_layout(separators=". .*")
    fig.update_layout(legend_font_size=15)
    fig.update_traces(
    hovertemplate="<br>".join([
        "%{customdata[0][0]}",
        "%{customdata[0][2]}",
        "%{customdata[0][1]:,} €",
        "%{percent}"
    ])
    )
    #fig.show()

    fig.write_html(dossier+"/contrats-contractualisation-mes-clients-en-euros.html",include_plotlyjs=False)
    return


# In[ ]:


etablissements.rename(columns = {'identifiant':'identifiant acheteur','siege.commune':'commune'}, inplace = True)
dfcommune = etablissements[['commune','identifiant acheteur']]
dfcommune.set_index(['identifiant acheteur'], inplace = True)

d = {'volume':'sum', "Chiffre d'affaire":'sum', 'Client':'first','commune':'first'}
for bloc in df_final.index.unique():
    df = df_final.loc[bloc]
    #AJOUT DE LA COMMUNE
    df = pd.merge(df, dfcommune, how='left', on=['identifiant acheteur'])
    df = df.groupby('identifiant acheteur').agg(d)
    create_graphe(df, bloc[0], bloc[1], bloc[2])

