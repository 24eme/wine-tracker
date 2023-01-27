#!/bin/bash

mkdir -p graphes


if test "$1" ; then
	cvi=$1
	echo "$cvi"
	python3 src/drm/wine-tracker-drm-stock-recoltes-sorties.py $cvi
        python3 src/drm/wine-tracker-drm-sortie-vrac-condionne.py $cvi
        python3 src/drm/wine-tracker-drm-sorties-par-mois.py $cvi
	python3 src/drm/wine-tracker-drm-sortie-tous.py $cvi
else
	echo "ICI"
	python3 src/drm/wine-tracker-drm-stock-recoltes-sorties.py
	python3 src/drm/wine-tracker-drm-sortie-vrac-condionne.py
	python3 src/drm/wine-tracker-drm-sorties-par-mois.py
fi
