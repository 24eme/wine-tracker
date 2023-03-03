#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse
import pathlib


# In[ ]:


path = pathlib.Path().absolute()
path = str(path).replace("src","")
dossier_graphes=path+"/graphes/"
csv = path+"/data/drm/export_bi_mouvements.csv"  #il manque un ; à la fin du header.
source = "DRM Inter-Rhône"

mois = { "08" : "Août" , "09" : "Septembre", "10" : "Octobre", "11" : "Novembre" , "12" : "Décembre",
        "01" : "Janvier", "02" : "Février", "03" : "Mars", "04" : "Avril", "05" : "Mai", "06" : "Juin",
        "07" : "Juillet" }

mois_sort = { "Août" : "01" , "Septembre" : "02", "Octobre" : "03", "Novembre" : "04" , "Décembre" : "05",
        "Janvier" : "06", "Février" : "07", "Mars" : "08", "Avril" : "09", "Mai" : "10", "Juin" : "11",
        "Juillet" : "12" }


# In[ ]:


mouvements = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False)

lastcampagnes = mouvements['campagne'].unique()
lastcampagnes.sort()
lastcampagnes = lastcampagnes[-3:]
mouvements = mouvements.query('campagne in @lastcampagnes')

mouvements.rename(columns = {'identifiant declarant':'identifiant'}, inplace = True)

mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)
typedemouvements = ['sorties/vrac','sorties/vrac_contrat','sorties/vrac_export','sorties/crd', 'sorties/factures', 'sorties/export', 'sorties/crd_acquittes', 'sorties/acq_crd','sorties/consommation']
mouvements = mouvements.query("type_de_mouvement in @typedemouvements").reset_index()

mouvements["volume mouvement"] = mouvements["volume mouvement"]*(-1)
mouvements['sorties'] = mouvements["type_de_mouvement"].str.lower().str.startswith("sorties/")
mouvements['filtre_produit'] = mouvements['appellation'] + "-" + mouvements['lieu'] + "-" +mouvements['certification']+ "-" +mouvements['genre']+ "-" +mouvements['mention']

mouvements['mois'] = mouvements["periode"].str.extract('.*(\d{2})', expand = False)
mouvements['mois'] = mouvements['mois'].map(mois,na_action=None)

#mouvements


# In[ ]:


### PAR APPELLATION ET COULEUR

sorties = mouvements.query("sorties == True")

sorties = sorties.groupby(["filtre_produit","couleur",'campagne','mois']).sum(["volume mouvement"])[["volume mouvement"]]
sorties = sorties.reset_index()

sorties['couleur'] = sorties['couleur'].str.upper()

sorties.set_index(['filtre_produit','couleur'], inplace = True)

sorties['ordre-mois'] = sorties['mois'].map(mois_sort,na_action=None)

sorties_spe_spe = sorties.sort_values(by=['filtre_produit','couleur',"campagne","ordre-mois"])

#sorties_spe_spe


# In[ ]:


# PAR APPELLATIONS

sorties_spe_all = sorties_spe_spe.groupby(["filtre_produit",'campagne','mois','ordre-mois']).sum(["volume mouvement"])[["volume mouvement"]]
sorties_spe_all = sorties_spe_all.sort_values(by=['filtre_produit',"campagne",'ordre-mois'])
sorties_spe_all["couleur"] = "TOUT"
sorties_spe_all = sorties_spe_all.reset_index()
sorties_spe_all.set_index(['filtre_produit','couleur'], inplace = True)

#sorties_spe_all


# In[ ]:


#AUCUN FILTRE TOUTES LES APPELLATIONS ET TOUTES LES COULEURS

sorties_all_all = sorties_spe_spe.groupby(['campagne','mois','ordre-mois']).sum(["volume mouvement"])[["volume mouvement"]]
sorties_all_all = sorties_all_all.sort_values(by=["campagne",'ordre-mois'])

sorties_all_all["couleur"] = "TOUT"
sorties_all_all["filtre_produit"] = "TOUT"
sorties_all_all = sorties_all_all.reset_index()

sorties_all_all.set_index(['filtre_produit','couleur'], inplace = True)

#sorties_all_all


# In[ ]:


#CONCATENATION DES 3 TABLEAUX :
df_final = pd.concat([sorties_spe_spe, sorties_spe_all])
df_final = pd.concat([df_final, sorties_all_all])

df_final = df_final.sort_values(by=['filtre_produit','couleur'])
df_final['campagne-ordre-mois'] = df_final['campagne']+"-"+df_final['ordre-mois']
df_final['mois-campagne'] = df_final['mois']+"-"+df_final['campagne']

#AJOUT DE TOUS LES MOIS
for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    for campagne in lastcampagnes:
        for m in list((range(1,13))):
            com = campagne+'-'+str(m).zfill(2)
            pcom = max(df['campagne-ordre-mois'].unique())
            if( com < pcom and com not in df['campagne-ordre-mois'].unique()):
                if(m != 5):
                    real_mois = (m+7)%12
                else:
                    real_mois = (m+8)%12
                mois_string = mois[str(real_mois).zfill(2)]
                new = [bloc[0],bloc[1],campagne,mois_string,0,format(m, '02d'),campagne+'-'+str(format(m, '02d')),mois_string+'-'+campagne]
                df = df.reset_index()
                df = df.append(pd.Series(new, index=df.columns[:len(new)]), ignore_index=True)
                df.set_index(['filtre_produit','couleur'], inplace = True)
    new = df_final.loc[[bloc]].merge(df,on = ['filtre_produit','couleur',"campagne","mois","volume mouvement",'ordre-mois','campagne-ordre-mois','mois-campagne'], how = "right")
    df_final = df_final.drop([bloc])
    df_final = pd.concat([df_final, new])

df_final = df_final.sort_values(by=['filtre_produit','couleur',"campagne",'ordre-mois'])
df_final.rename(columns = {'volume mouvement':'volume',"mois-campagne":'periode'}, inplace = True)

tabcouleur = ["#CFCFCF","#5D5D5D","#E75047"]
couleurs = tabcouleur[-len(df_final['campagne'].unique()):]


# In[ ]:


def create_graphe(final,appellation,couleur):
    # CREATION DU GRAPHE
    fig = px.line(final, x='periode', y="volume",color="campagne", markers=True, color_discrete_sequence=couleurs, title="Le vignoble")
    fig.update_layout(title={
                        'text': "<b>LE VIGNOBLE</b>",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                      title_font_size=24,
                      title_font_color="grey",
                      xaxis_title=None,
                      yaxis_title=None,
                      legend_title=None,
                      paper_bgcolor="#F7F7F7",
                      plot_bgcolor = "#F7F7F7",
                      yaxis=dict(tickformat=".f"),
                      legend=dict(orientation="h",xanchor = "center",x = 0.5),
                      legend_itemdoubleclick=False
                     )
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
    fig.update_xaxes(fixedrange=True,showline=True, linewidth=1, linecolor='Lightgrey',showticklabels=False)
    fig.update_yaxes(fixedrange=True,rangemode="tozero")
    #fig.show()
    
    dossier = dossier_graphes+"/LE_VIGNOBLE/drm/"+appellation+"-"+couleur
    pathlib.Path(dossier).mkdir(parents=True, exist_ok=True)

    fig.write_html(dossier+"/drm-sorties-par-campagne-et-mois.html",include_plotlyjs=False)

    return


# In[ ]:


for bloc in df_final.index.unique():
    df = df_final.loc[[bloc]]
    create_graphe(df,bloc[0],bloc[1])

