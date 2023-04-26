#!/bin/bash

IDENTIFIANT=$1

if [ -n "$IDENTIFIANT" ]; then echo "$IDENTIFIANT"; else echo "TOUS"; fi

python3 src/drm-stock-recoltes-sorties.py "$IDENTIFIANT"
python3 src/drm-sortie-vrac-condionne.py "$IDENTIFIANT"
python3 src/drm-sortie-tous.py "$IDENTIFIANT"
python3 src/drm-sorties-cumul-par-mois.py "$IDENTIFIANT"
python3 src/drm-sorties-par-campagne-et-mois.py "$IDENTIFIANT"

if [ -n "$IDENTIFIANT" ];then
    echo $IDENTIFIANT
else
    tail -n +2 data/contrats/export_bi_etablissements.csv | cut -d ';' -f7
fi | while read ID; do
    python3 src/contrats-contractualisation-mes-clients.py "$ID"
    python3 src/contrats-contractualisation-mes-clients-tableau-a-date.py "$ID"
    python3 src/contrats-contractualisation-comparaison-deroulement-par-campagne.py "$ID"
    python3 src/contrats-contractualisation-top10-5-dernieres-campagnes.py "$ID"
    python3 src/informations-operateur.py "$ID"
    python3 src/chiffres-cles.py "$ID"
done
