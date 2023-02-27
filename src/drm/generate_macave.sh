if test "$1" ; then
	cvi=$1
	echo "$cvi"
	python3 src/drm/wine-tracker-drm-stock-recoltes-sorties.py $cvi
	python3 src/drm/wine-tracker-drm-sortie-vrac-condionne.py $cvi
	python3 src/drm/wine-tracker-drm-sortie-tous.py $cvi
	python3 src/drm/wine-tracker-drm-sorties-par-mois.py $cvi
	python3 src/drm/wine-tracker-informations-operateur.py $cvi
	python3 src/drm/wine-tracker-drm-sorties-par-trimestre.py $cvi
	python3 src/drm/wine-tracker-contrats-contractualisation-mes-clients.py $cvi
	python3 src/drm/wine-tracker-informations-operateur.py $cvi
else
	echo "TOUS"
	python3 src/drm/wine-tracker-drm-stock-recoltes-sorties.py
	python3 src/drm/wine-tracker-drm-sortie-vrac-condionne.py
	python3 src/drm/wine-tracker-drm-sorties-par-mois.py
	python3 src/drm/wine-tracker-informations-operateur.py
	python3 src/drm/wine-tracker-drm-sorties-par-trimestre.py
	python3 src/drm/wine-tracker-contrats-contractualisation-mes-clients.py
	python3 src/drm/wine-tracker-informations-operateur.py
fi
