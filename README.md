# wine-tracker

Pour la génération des graphes :

pip3 install pandas
pip3 install plotly
pip3 install argparse

Pour la génération des .py à partir des jupyter :

pip3 install Jinja2
pip3 install nbconvert

Pour générer les .py: 

make dans le dossier  src/drm

Pour générer tous les graphes :

bash src/drm/generate_all.sh

Pour générer tous les graphes du "vignoble" :

bash src/drm/generate_levignoble.sh

Pour générer tous les graphes de "ma cave" pour tous les opérateurs :

bash src/drm/generate_macave.sh

Pour générer tous les graphes de "ma cave" pour tous 1 opérateur :

bash src/drm/generate_macave.sh $cvi
