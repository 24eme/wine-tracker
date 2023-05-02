#!/bin/bash

IDENTIFIANT=$1

if [ -n "$IDENTIFIANT" ]; then echo "$IDENTIFIANT"; else echo "TOUS"; fi


if [ -n "$IDENTIFIANT" ];then
    echo $IDENTIFIANT
else
    tail -n +2 data/contrats/export_bi_etablissements.csv | cut -d ';' -f7
fi | while read ID; do
    python3 src/00_prealable/01_chiffres-cles.py "$ID"
    python3 src/00_prealable/00_informations-operateur.py "$ID"
done


python3 src/01_DRM/01_drm-stock-recoltes-sorties.py "$IDENTIFIANT"
python3 src/01_DRM/02_drm-sortie-vrac-condionne.py "$IDENTIFIANT"
python3 src/01_DRM/03_drm-sorties-par-campagne-et-mois.py "$IDENTIFIANT"
python3 src/01_DRM/04_drm-sorties-cumul-par-mois.py "$IDENTIFIANT"


if [ -n "$IDENTIFIANT" ];then
    echo $IDENTIFIANT
else
    tail -n +2 data/contrats/export_bi_etablissements.csv | cut -d ';' -f7
fi | while read ID; do
    python3 src/02_contrat/01_contrats-contractualisation-mes-clients.py "$ID"
    python3 src/02_contrat/01_contrats-contractualisation-mes-clients-tableau-a-date.py "$ID"
    python3 src/02_contrat/02_contrats-contractualisation-top10-5-dernieres-campagnes.py "$ID"
    python3 src/02_contrat/03_contrats-contractualisation-comparaison-deroulement-par-campagne.py "$ID"
done
