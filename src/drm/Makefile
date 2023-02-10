all: wine-tracker-drm-stock-recoltes-sorties.py wine-tracker-drm-sortie-vrac-condionne.py wine-tracker-drm-sorties-par-mois.py wine-tracker-drm-sortie-tous.py wine-tracker-drm-stock-recoltes-sorties-moyenne.py wine-tracker-drm-sortie-vrac-condionne-moyenne.py wine-tracker-drm-sortie-tous-moyenne.py
%.py: %.ipynb
	jupyter nbconvert --to script $^
