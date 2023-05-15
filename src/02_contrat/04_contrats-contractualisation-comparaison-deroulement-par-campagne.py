#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib
from datetime import datetime
import datetime as dt
from dateutil.relativedelta import relativedelta

path = pathlib.Path().absolute()
path = str(path).replace("/src","").replace("/02_contrat","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/contrats/export_bi_contrats.csv"  #il manque un ; à la fin du header.
csv_etablissements = path+"/data/contrats/export_bi_etablissements.csv" #il manque un ; à la fin du header.
source = "DRM Inter-Rhône"

sort_week = [31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]


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
contrats = contrats.query("appellation != 'CDP'")

contrats['date de validation'] = pd.to_datetime(contrats['date de validation'], utc=True)
contrats['semaine'] = contrats['date de validation'].dt.isocalendar().week.apply(lambda x: int(x))
contrats['annee'] = contrats['date de validation'].dt.isocalendar().year
contrats['A-WS'] = contrats['annee'].apply(str)+'-W'+contrats['semaine'].apply(str)+ '-1'
contrats['firstdayoftheweek'] = contrats['A-WS'].map(lambda x: dt.datetime.strptime(x, "%G-W%V-%u"))
#contrats['semaine'] = pd.to_numeric(contrats['semaine'], downcast='integer')


#contrats['semaine'].unique()
lastcampagnes = contrats['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-5:]


contrats_csv = contrats.query('campagne in @lastcampagnes')
contrats_csv = contrats_csv.copy()
contrats_csv['couleur'] = contrats_csv['couleur'].str.upper()

contrats_csv.rename(columns = {'identifiant vendeur':'identifiant_vendeur','volume propose (en hl)':'volume propose'}, inplace = True)

contrats = contrats_csv.query("identifiant_vendeur == @id_operateur").reset_index()

#changement de la campagne en fonction de la date de validation
contrats['campagne']  = contrats['date de validation'].apply(lambda v: str((v - relativedelta(months=7)).year)+"-"+str((v - relativedelta(months=7)).year+1) )


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

# PAR APPELLATION ET COULEUR

contrats['filtre_produit'] = contrats['appellation'] + "-" + contrats['lieu'] + "-" +contrats['certification']+ "-" +contrats['genre']+ "-" +contrats['mention']

contrats_spe_spe = contrats.groupby(["identifiant_vendeur","filtre_produit", "couleur","campagne","semaine","firstdayoftheweek"]).sum(["volume propose"])[["volume propose"]]
contrats_spe_spe.reset_index(level=['semaine'], inplace=True)
contrats_spe_spe['semaine-sort'] = (contrats_spe_spe['semaine']-31)%53
contrats_spe_spe = contrats_spe_spe.sort_values(by=["identifiant_vendeur","filtre_produit", "couleur","campagne",'semaine-sort'])
#contrats_spe_spe['volume'] = contrats_spe_spe.groupby(["identifiant_vendeur","filtre_produit", "couleur","campagne"])['volume propose'].cumsum()
contrats_spe_spe = contrats_spe_spe.reset_index()
contrats_spe_spe.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
#contrats_spe_spe


# PAR APPELLATIONS

contrats_spe_all = contrats.groupby(["identifiant_vendeur","filtre_produit", "campagne","semaine","firstdayoftheweek"]).sum(["volume propose"])[["volume propose"]]
contrats_spe_all.reset_index(level=['semaine'], inplace=True)
contrats_spe_all['semaine-sort'] = (contrats_spe_all['semaine']-31)%53
contrats_spe_all = contrats_spe_all.sort_values(by=["identifiant_vendeur","filtre_produit","campagne",'semaine-sort'])
#contrats_spe_all['volume'] = contrats_spe_all.groupby(["identifiant_vendeur","filtre_produit","campagne"])['volume propose'].cumsum()
contrats_spe_all["couleur"] = "TOUT"
contrats_spe_all = contrats_spe_all.reset_index()
contrats_spe_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
#contrats_spe_all


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

contrats_all_all = contrats.groupby(["identifiant_vendeur","campagne","semaine","firstdayoftheweek"]).sum(["volume propose"])[["volume propose"]]
contrats_all_all.reset_index(level=['semaine'], inplace=True)
contrats_all_all['semaine-sort'] = (contrats_all_all['semaine']-31)%53
contrats_all_all = contrats_all_all.sort_values(by=["identifiant_vendeur","campagne",'semaine-sort'])
#contrats_all_all['volume'] = contrats_all_all.groupby(["identifiant_vendeur","campagne"])['volume propose'].cumsum()
contrats_all_all["couleur"] = "TOUT"
contrats_all_all["filtre_produit"] = "TOUT"
contrats_all_all = contrats_all_all.reset_index()
contrats_all_all.set_index(['identifiant_vendeur','filtre_produit','couleur'], inplace = True)
#contrats_all_all


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([contrats_spe_spe, contrats_spe_all])
df_final = pd.concat([df_final, contrats_all_all])
df_final = df_final.sort_values(by=['identifiant_vendeur', 'filtre_produit','couleur'])


df_final['campagne-semaine'] = df_final['campagne']+"-"+df_final['semaine'].apply(str)


df_final = df_final.round({'volume propose': 0})


# In[ ]:


def create_graphe(df,identifiant,appellation,couleur):

    df['firstdayoftheweek'] = df['firstdayoftheweek'].dt.strftime('%d/%m/%Y')

    fig = px.line(df, x="semaine", y="volume", color='campagne', custom_data=['semaine-sort','campagne','firstdayoftheweek'], width=1250, height=650,color_discrete_sequence=["#CFCFCF", "#A1A1A1", "#5D5D5D","#0A0A0A","#ea4f57"],
                 labels={
                     "semaine": "Numéro de la semaine - Début de campagne : Semaine 31",
                     "volume": "Volume contractualisé hebdomadaire (en hl)"})
    fig.update_layout(xaxis_type = 'category')
    fig.update_xaxes(categoryorder='array', categoryarray= sort_week)

    fig.update_layout(    paper_bgcolor="white",
                          plot_bgcolor = "white",
                          yaxis=dict(tickformat=".0f"),
                          legend=dict(orientation="h",xanchor = "center",x = 0.5, y= -0.3),
                          legend_itemdoubleclick=False,
                          legend_title=None,
                          legend_font_size=15,
                          legend_traceorder="reversed"
                         )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True,showline=True, linewidth=1, linecolor='Lightgrey')
    fig.update_yaxes(fixedrange=True,rangemode="tozero")

    fig.update_yaxes(tickformat=",")
    fig.update_layout(separators="*  .")

    fig.add_vline(x=0)
    fig.add_hline(y=0)

    fig.update_traces(
        hovertemplate="<br>".join([
            "Campagne %{customdata[1]}",
            "Semaine n°%{customdata[0]} (%{customdata[2]})",
            "%{y} hl",
        ])
    )
    #fig.show()

    dossier = dossier_graphes+"/"+identifiant+"/contrat/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()

    fig.write_html(dossier+"/contrats-contractualisation-comparaison-deroulement-par-campagne.html",include_plotlyjs=False)

    return


# In[ ]:


#AJOUT DES 0
for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    df = df.reset_index()
    for campagne in lastcampagnes:
        annee = str(campagne[5:])
        if campagne+'-31' not in df['campagne-semaine'].unique():
            df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne,dt.datetime.strptime(annee+'-W31-1', "%G-W%V-%u"),31,0,0,campagne+'-31']

        if campagne+'-30' not in df['campagne-semaine'].unique() and campagne != lastcampagnes[-1:][0]:
            df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne,dt.datetime.strptime(annee+'-W30-1', "%G-W%V-%u"),30,0,53,campagne+'-30']

        currentweek = datetime.today().isocalendar()[1]
        if campagne+'-'+str(currentweek) not in df['campagne-semaine'].unique() and campagne == lastcampagnes[-1:][0]:
            df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne,dt.datetime.strptime(annee+'-W'+str(currentweek)+'-1', "%G-W%V-%u"),currentweek,0,(currentweek-31)%53,campagne+'-'+str(currentweek)]

    df = df.sort_values(by=['campagne'])
    df = df.reset_index(drop=True)
    df = df.sort_values(by=['identifiant_vendeur', 'filtre_produit','couleur','campagne','semaine-sort'])
    df['volume'] = df.groupby(["identifiant_vendeur","filtre_produit", "couleur","campagne"])['volume propose'].cumsum()
    create_graphe(df,bloc[0],bloc[1],bloc[2])

