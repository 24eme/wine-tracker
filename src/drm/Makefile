all: wine-tracker-drm-stock-recoltes-sorties.py wine-tracker-drm-sortie-vrac-condionne.py wine-tracker-drm-sorties-par-mois.py wine-tracker-drm-sortie-tous.py

%.py: %.ipynb
	jupyter nbconvert --to script $^
