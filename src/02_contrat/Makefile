all: 01_contrats-contractualisation-mes-clients.py 03_contrats-contractualisation-mes-clients-tableau-a-date.py 02_contrats-contractualisation-top10-5-dernieres-campagnes.py 04_contrats-contractualisation-comparaison-deroulement-par-campagne.py

%.py: %.ipynb
	jupyter nbconvert --to script $^
