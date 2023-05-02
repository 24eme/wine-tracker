all: 00_informations-operateur.py 01_chiffres-cles.py

%.py: %.ipynb
	jupyter nbconvert --to script $^
