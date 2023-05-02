all: 01_drm-stock-recoltes-sorties-le-vignoble.py 01_drm-stock-recoltes-sorties.py 02_drm-sortie-vrac-condionne-le-vignoble.py 02_drm-sortie-vrac-condionne.py 03_drm-sorties-par-campagne-et-mois-le-vignoble.py 03_drm-sorties-par-campagne-et-mois.py 04_drm-sorties-cumul-par-mois.py drm-sorties-par-trimestre-le-vignoble.py drm-sorties-par-trimestre.py drm-sortie-tous-le-vignoble.py drm-sortie-tous.py

%.py: %.ipynb
	jupyter nbconvert --to script $^
