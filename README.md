# wine-tracker

##Polices

Télécharger les fonts qui se trouvent dans le dossier web/fonts/

## Dépendances

Pour éviter tout conflit avec les librairies systèmes, il est recommandé d'utiliser un virtualenv :

```
python3 -m venv dir/
source dir/bin/activate
```

Pour la génération des graphes, jupyter notebook est utilisé :

```
pip3 install jupyter pandas plotly argparse
```

Pour la génération des .py à partir des jupyter :

```
pip3 install Jinja2 nbconvert
```

## Préparation des données

Mettre les CSV d'entrées issus de Déclarvins dans le dossier data/
* data/drm/export_bi_drm_stock.csv
* data/drm/export_bi_mouvements.csv
* data/contrats/export_bi_etablissements.csv
* data/contrats/export_bi_contrats.csv

## Génération des données

Pour générer les .py: `cd src/ && make`

Pour générer tous les graphes : `bash bin/generate_all.sh`

Pour générer tous les graphes du "vignoble" : `bash bin/generate_levignoble.sh`

Pour générer tous les graphes de "ma cave" pour tous les opérateurs : `bash bin/generate_macave.sh`

Pour générer tous les graphes de "ma cave" pour 1 opérateur : `bash bin/generate_macave.sh $id_compte`
