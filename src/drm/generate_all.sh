#!/bin/bash

mkdir -p graphes

python3 src/drm/wine-tracker-drm-stock-recoltes-sorties.py
python3 src/drm/wine-tracker-drm-sortie_vrac_condionne.py
python3 src/drm/wine-tracker-drm-sorties-par-mois.py
