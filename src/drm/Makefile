all: wine-tracker-drm-stock-recoltes-sorties.py wine-tracker-drm-sortie_vrac_condionne.py wine-tracker-drm-sorties-par-mois.py wine-tracker-drm-sortie_tous.py

%.py: %.ipynb
	jupyter nbconvert --to script $^
