all: prealable drm contrat

drm: 01_DRM/01_drm-stock-recoltes-sorties-le-vignoble.py 01_DRM/01_drm-stock-recoltes-sorties.py 01_DRM/02_drm-sortie-vrac-condionne-le-vignoble.py 01_DRM/02_drm-sortie-vrac-condionne.py 01_DRM/03_drm-sorties-par-campagne-et-mois-le-vignoble.py 01_DRM/03_drm-sorties-par-campagne-et-mois.py 01_DRM/04_drm-sorties-cumul-par-mois.py 01_DRM/drm-sortie-tous-le-vignoble.py 01_DRM/drm-sortie-tous.py

prealable: 00_prealable/00_informations-operateur.py  00_prealable/01_chiffres-cles.py

contrat: 02_contrat/01_contrats-contractualisation-mes-clients.py 02_contrat/03_contrats-contractualisation-mes-clients-tableau-a-date.py 02_contrat/02_contrats-contractualisation-top10-5-dernieres-campagnes.py 02_contrat/04_contrats-contractualisation-comparaison-deroulement-par-campagne.py

01_DRM/%.py: 01_DRM/%.ipynb
	jupyter nbconvert --to script $^

02_contrat/%.py: 02_contrat/%.ipynb
	jupyter nbconvert --to script $^

00_prealable/%.py: 00_prealable/%.ipynb
	jupyter nbconvert --to script $^

clean:
	rm */*py
