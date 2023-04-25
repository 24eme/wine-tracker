#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib

path = pathlib.Path().absolute()
path = str(path).replace("src","")
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
contrats.rename(columns = {'type de vente':'type_de_vente','prix unitaire (en hl)':'prix'}, inplace = True)
contrats = contrats.query("type_de_vente == 'vrac'")

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

contrats_spe_spe = contrats.groupby(["identifiant_vendeur","filtre_produit", "couleur","identifiant acheteur","nom_acheteur"]).sum(["volume propose","prix"])[["volume propose","prix"]]
contrats_spe_spe = contrats_spe_spe.reset_index(level='identifiant acheteur')
contrats_spe_spe = contrats_spe_spe.reset_index(level='nom_acheteur')
contrats_spe_spe = contrats_spe_spe.sort_values(by=['volume propose'],ascending=False)
contrats_spe_spe = contrats_spe_spe.groupby(["identifiant_vendeur","filtre_produit", "couleur"]).head(10)
contrats_spe_spe = contrats_spe_spe.sort_values(by=['volume propose'])

#contrats_spe_spe

# PAR APPELLATIONS

contrats_spe_all = contrats_spe_spe.groupby(["identifiant_vendeur","filtre_produit",'identifiant acheteur',"nom_acheteur"]).sum(["volume propose","prix"])[["volume propose","prix"]]
contrats_spe_all["couleur"] = "TOUT"
contrats_spe_all = contrats_spe_all.reset_index()
contrats_spe_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
contrats_spe_all = contrats_spe_all.sort_values(by=['volume propose'],ascending=False)
contrats_spe_all = contrats_spe_all.groupby(["identifiant_vendeur","filtre_produit", "couleur"]).head(10)
contrats_spe_all = contrats_spe_all.sort_values(by=['volume propose'])
#contrats_spe_all

#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

contrats_all_all = contrats_spe_spe.groupby(["identifiant_vendeur",'identifiant acheteur',"nom_acheteur"]).sum(["volume propose","prix"])[["volume propose","prix"]]
contrats_all_all["couleur"] = "TOUT"
contrats_all_all["filtre_produit"] = "TOUT"
contrats_all_all = contrats_all_all.reset_index()

contrats_all_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
contrats_all_all = contrats_all_all.sort_values(by=['volume propose'],ascending=False)
contrats_all_all = contrats_all_all.groupby(["identifiant_vendeur","filtre_produit", "couleur"]).head(10)
contrats_all_all = contrats_all_all.sort_values(by=['volume propose'])

#contrats_all_all


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([contrats_spe_spe, contrats_spe_all])
df_final = pd.concat([df_final, contrats_all_all])

df_final = df_final.sort_values(by=['identifiant_vendeur','filtre_produit','couleur'])

df_final.rename(columns = {'volume propose':'volume'}, inplace = True)
df_final.rename(columns = {'nom_acheteur':"Client"}, inplace = True)

#df_final


# In[ ]:


def create_graphe(df, identifiant, appellation, couleur):
    fig = px.bar(df, y='Client',x="volume",color_discrete_sequence=["#E75047"],text_auto=True, width=1250, height=650,orientation='h')
    fig.update_layout(title_font_size=24,
                      title_font_color="rgb(231, 80, 71)",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="white",
                      plot_bgcolor = "white",
                      hovermode = False,
                      yaxis=dict(tickformat=".0f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5),
                      legend_itemdoubleclick=False
                     )
    fig.add_vline(x=0)
    fig.update_traces(textfont_size=14,textposition="outside", cliponaxis=False,texttemplate = "%{value:} hl",)
    fig.for_each_yaxis(lambda x: x.update(showgrid=True))
    fig.for_each_xaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_yaxes(ticksuffix = "  ", fixedrange=True)
    fig.update_xaxes(matches=None, showticklabels=True, visible=False,fixedrange=True)
    
    
    dossier = dossier_graphes+"/"+identifiant+"/contrat/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)

    fig.write_html(dossier+"/contrats-contractualisation-top-10-5-dernieres-campagnes.html",include_plotlyjs=False)
    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[bloc]
    create_graphe(df, bloc[0], bloc[1], bloc[2])

