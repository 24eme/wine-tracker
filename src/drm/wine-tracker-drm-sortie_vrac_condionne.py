#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import argparse


# In[ ]:


#arguments
id_operateur="XXXXX-XX"

parser = argparse.ArgumentParser()
parser.add_argument("id_operateur", help="Identifiant opérateur", default=id_operateur, nargs='?')

try:
    args = parser.parse_args()
    id_operateur = args.id_operateur
except:
    print("Arguments pas défaut")



# In[ ]:


dossier_graphes="../../graphes/"
csv = "../../data/drm/export_bi_mouvements.csv"
source = "DRM Inter-Rhône"


# In[ ]:


#préparations des données de l'opérateur sans filtres
mouvements = pd.read_csv(csv, sep=";",encoding="iso8859_15", low_memory=False)
mouvements.rename(columns = {'identifiant declarant':'identifiant_declarant'}, inplace = True)
mouvements = mouvements.query("identifiant_declarant == @id_operateur").reset_index()
mouvements["volume mouvement"] = mouvements["volume mouvement"]*(-1)


# In[ ]:


#applications des filtres
mouvements.rename(columns = {'type de mouvement':'type_de_mouvement'}, inplace = True)
mouvements['sorties'] = mouvements["type_de_mouvement"].str.lower().str.startswith("sorties/")
mouvements = mouvements.query("sorties == True")


#les VRACS
vrac = mouvements.query("type_de_mouvement == 'sorties/vrac'").reset_index()
vrac = vrac["volume mouvement"].groupby(vrac['campagne']).agg('sum').reset_index()
vrac.rename(columns = {'volume mouvement':'Vrac'}, inplace = True)

#les CONDITIONNE
conditionne = mouvements.query("type_de_mouvement == 'sorties/crd'").reset_index()
conditionne = conditionne["volume mouvement"].groupby(conditionne['campagne']).agg('sum').reset_index()
conditionne.rename(columns = {'volume mouvement':'Conditionné'}, inplace = True)


#AUTRES

autres = mouvements.query("type_de_mouvement != 'sorties/vrac' and type_de_mouvement != 'sorties/crd'").reset_index()
autres = autres["volume mouvement"].groupby(autres['campagne']).agg('sum').reset_index()
autres.rename(columns = {'volume mouvement':'Autres'}, inplace = True)


#MERGE DES 3
final = pd.merge(vrac, conditionne,how='outer', on=['campagne'])
final = pd.merge(final, autres ,how='outer', on=['campagne'])

#FORMATTAGE DU TABLEAU 
final = pd.melt(final, id_vars=['campagne'], value_vars=['Vrac','Conditionné','Autres'])
final.rename(columns = {'value':'volume'}, inplace = True)

print(final)


# In[ ]:


# CREATION DU GRAPHE
fig = px.bar(final, x="campagne", y="volume", color="variable",color_discrete_sequence=["blue", "red", "purple"],
             text_auto=True,
             title="Evolution de MES sorties de Chais Vrac/Conditionné <br>(en hl, Sources "+source+")")
fig.update_layout(xaxis_title=None, 
                  yaxis_title=None,
                  legend_title=None,
                  paper_bgcolor="#b7e1e5",
                  plot_bgcolor = "white",
                  hovermode = False,
                  yaxis=dict(tickformat=".0f"),
                  legend=dict(orientation="h",xanchor = "center",x = 0.5)
                 )
fig.for_each_xaxis(lambda x: x.update(showgrid=False))
fig.for_each_yaxis(lambda x: x.update(gridcolor='Lightgrey'))
fig.update_xaxes(fixedrange=True)
fig.update_yaxes(fixedrange=True)
fig.show()


# In[ ]:


# GRAPHE DANS UN FICHIER HTML
fig.write_html(dossier_graphes+id_operateur+"_graphe2.html")

