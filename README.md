# wine-tracker

## Dépendances

Pour éviter tout conflit avec les librairies systèmes, il est recommandé d'utilisé un virtualenv :

```
python3 -m venv dir/
```

Pour la génération des graphes, jupyter notebook est utilisé :

```
pip3 install jupyter
pip3 install pandas
pip3 install plotly
pip3 install argparse
```

Pour la génération des .py à partir des jupyter :

```
pip3 install Jinja2
pip3 install nbconvert
```

## Préparation des données

Mettre les CSV d'entrées issus de Déclarvins dans le dossier data/
* data/drm/stock.csv
* data/drm/mouvements.csv
* data/contrats/contrats.csv
* data/contrats/etablissements.csv

## Génération des données

Pour générer les .py: `cd src/ && make`

Pour générer tous les graphes : `bash src/generate_all.sh`

Pour générer tous les graphes du "vignoble" : `bash src/generate_levignoble.sh`

Pour générer tous les graphes de "ma cave" pour tous les opérateurs : `bash src/generate_macave.sh`

Pour générer tous les graphes de "ma cave" pour tous 1 opérateur : `bash src/generate_macave.sh $id_compte`
