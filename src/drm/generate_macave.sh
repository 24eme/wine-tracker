#!/bin/bash

CVI=
[ $# -eq 1 ] && CVI=$1

if [ -n "$CVI" ]; then echo "$CVI"; else echo "TOUS"; fi

python3 src/drm/wine-tracker-drm-stock-recoltes-sorties.py "$CVI"
python3 src/drm/wine-tracker-drm-sortie-vrac-condionne.py "$CVI"
python3 src/drm/wine-tracker-drm-sortie-tous.py "$CVI"
python3 src/drm/wine-tracker-drm-sorties-par-mois.py "$CVI"
python3 src/drm/wine-tracker-informations-operateur.py "$CVI"
python3 src/drm/wine-tracker-drm-sorties-par-trimestre.py "$CVI"
python3 src/drm/wine-tracker-contrats-contractualisation-mes-clients.py "$CVI"
python3 src/drm/wine-tracker-contrats-contractualisation-mes-clients-tableau.py "$CVI"
python3 src/drm/wine-tracker-contrats-contractualisation-comparaison-deroulement-par-campagne.py "$CVI"
python3 src/drm/wine-tracker-informations-operateur.py "$CVI"
