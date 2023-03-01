all: wine-tracker-drm-stock-recoltes-sorties.py wine-tracker-drm-sortie-vrac-condionne.py wine-tracker-drm-sorties-par-mois.py wine-tracker-drm-sortie-tous.py wine-tracker-drm-stock-recoltes-sorties-moyenne.py wine-tracker-drm-sortie-vrac-condionne-moyenne.py wine-tracker-drm-sortie-tous-moyenne.py wine-tracker-drm-sorties-par-trimestre.py wine-tracker-drm-sorties-par-trimestre-moyenne.py wine-tracker-informations-operateur.py wine-tracker-contrats-contractualisation-mes-clients.py wine-tracker-contrats-contractualisation-mes-clients-tableau.py
%.py: %.ipynb
	jupyter nbconvert --to script $^
