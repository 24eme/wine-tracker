#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib


# In[ ]:


path = pathlib.Path().absolute()
path = str(path).replace("/src","").replace("/01_DRM","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/drm/export_bi_mouvements.csv"  #il manque un ; à la fin du header.
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


# In[ ]:


#préparations des données de l'opérateur sans filtres
mouvements = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False, index_col=False)
mouvements = mouvements[mouvements['genre'] != 'VCI']
mouvements = mouvements[mouvements['libelle type'] == 'Suspendu']

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-10:]
mouvements = mouvements.query('campagne in @lastcampagnes')
mouvements = mouvements.query("appellation != 'CDP'")

mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)

if(id_operateur):
    mouvements = mouvements.query("identifiant == @id_operateur").reset_index()

#mouvements


# In[ ]:


mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)
mouvements['sorties'] = mouvements["type_de_mouvement"].str.lower().str.startswith("sorties/")
mouvements = mouvements.query("sorties == True")
mouvements['filtre_produit'] = mouvements['appellation'] + "-" + mouvements['lieu'] + "-" +mouvements['certification']+ "-" +mouvements['genre']+ "-" +mouvements['mention']

#mouvements['type_de_mouvement'].unique()


# In[ ]:


### PAR APPELLATION ET COULEUR

#les VRACS # 'sorties/vrac', 'sorties/vrac_contrat','sorties/vrac_export'
typedemouvementsvracs = ['sorties/vrac']
vrac = mouvements.query("type_de_mouvement in @typedemouvementsvracs").reset_index()
vrac = vrac.groupby(["identifiant","filtre_produit","couleur","campagne"]).sum(["volume mouvement"])[["volume mouvement"]]
vrac.rename(columns = {'volume mouvement':'Vrac'}, inplace = True)

#les CONDITIONNE # 'sorties/crd', 'sorties/factures', 'sorties/export', 'sorties/crd_acquittes', 'sorties/acq_crd'
typedemouvementsconditionne = ['sorties/crd', 'sorties/factures', 'sorties/export', 'sorties/acq_crd']
conditionne = mouvements.query("type_de_mouvement in @typedemouvementsconditionne").reset_index()
conditionne = conditionne.groupby(["identifiant","filtre_produit","couleur","campagne"]).sum(["volume mouvement"])[["volume mouvement"]]
conditionne.rename(columns = {'volume mouvement':'Conditionné'}, inplace = True)

df_final_spe_spe = pd.concat([vrac, conditionne],axis=1)
df_final_spe_spe = df_final_spe_spe.sort_values(by=['identifiant', 'filtre_produit','couleur'])

df_final_spe_spe = df_final_spe_spe.reset_index()
df_final_spe_spe['couleur'] = df_final_spe_spe['couleur'].str.upper()
df_final_spe_spe.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

#df_final_spe_spe


# In[ ]:


# PAR APPELLATIONS

#les VRACS
vrac_spe_all = vrac.groupby(["identifiant","filtre_produit","campagne"]).sum(["Vrac"])[["Vrac"]]

#les CONDITIONNE
conditionne_spe_all = conditionne.groupby(["identifiant","filtre_produit","campagne"]).sum(["Conditionné"])[["Conditionné"]]

df_final_spe_all = pd.concat([vrac_spe_all, conditionne_spe_all],axis=1)
df_final_spe_all = df_final_spe_all.sort_values(by=['identifiant', 'filtre_produit'])

df_final_spe_all['couleur'] = "TOUT"

df_final_spe_all = df_final_spe_all.reset_index()
df_final_spe_all.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

#df_final_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

#les VRACS
vrac_all_all = vrac.groupby(["identifiant","campagne"]).sum(["Vrac"])[["Vrac"]]
#les CONDITIONNE
conditionne_all_all = conditionne.groupby(["identifiant","campagne"]).sum(["Conditionné"])[["Conditionné"]]

df_final_all_all = pd.concat([vrac_all_all, conditionne_all_all],axis=1)

df_final_all_all['couleur'] = "TOUT"
df_final_all_all['filtre_produit'] = "TOUT"

df_final_all_all = df_final_all_all.reset_index()
df_final_all_all.set_index(['identifiant','filtre_produit','couleur'], inplace = True)

#df_final_all_all


# In[ ]:


#MERGE DES 3 SOUS TABLEAUX :
df_final = pd.concat([df_final_spe_spe, df_final_spe_all])
df_final = pd.concat([df_final, df_final_all_all])
df_final = df_final.sort_values(by=['identifiant', 'filtre_produit','couleur','campagne'])
df_final = df_final.fillna(0)
df_final = df_final.round({'Vrac': 0, 'Conditionné': 0})


# In[ ]:


def create_graphe(final,identifiant,appellation,couleur):
    fig = px.bar(final, x="campagne", y="volume", color="variable",color_discrete_sequence=["#ea4f57","#f7bb58"],
                 text_auto=True,
                 title="Ma cave",height=650)
    fig.update_layout(title={
                        'text': "<b>MA CAVE</b>",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                      title_font_size=24,
                      title_font_color="#f7bb58",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="white",
                      plot_bgcolor = "white",
                      hovermode = False,
                      yaxis=dict(tickformat=".0f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5),
                      legend_itemdoubleclick=False,
                      legend_font_size=15
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    #fig.show()
    fig.update_yaxes(tickformat=",")
    fig.update_layout(separators="* .*")

    dossier = dossier_graphes+"/"+identifiant+"/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)
    pathlib.Path(dossier).parent.parent.touch()

    fig.write_html(dossier+"/drm-sortie-vrac-condionne.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    df = df.reset_index()

    for campagne in lastcampagnes:
        if campagne not in df.campagne.unique()[::-1] :
            df.loc[len(df)] = [bloc[0], bloc[1], bloc[2], campagne, 0, 0]

    df = df.sort_values(by=['campagne'])
    df = df.reset_index(drop=True)

    df = pd.melt(df, id_vars=['identifiant','filtre_produit','couleur','campagne'], value_vars=['Vrac','Conditionné'])
    df.rename(columns = {'value':'volume'}, inplace = True)
    create_graphe(df,bloc[0],bloc[1],bloc[2])

