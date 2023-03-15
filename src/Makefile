all: drm-stock-recoltes-sorties.py drm-sortie-vrac-condionne.py drm-sorties-cumul-par-mois.py drm-sortie-tous.py drm-stock-recoltes-sorties-le-vignoble.py drm-sortie-vrac-condionne-le-vignoble.py drm-sortie-tous-le-vignoble.py drm-sorties-par-campagne-et-mois.py drm-sorties-par-campagne-et-mois-le-vignoble.py informations-operateur.py contrats-contractualisation-mes-clients.py contrats-contractualisation-mes-clients-tableau-a-date.py contrats-contractualisation-comparaison-deroulement-par-campagne.py
%.py: %.ipynb
	jupyter nbconvert --to script $^
