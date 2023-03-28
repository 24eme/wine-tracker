#!/bin/bash

CVI=
[ $# -eq 1 ] && CVI=$1

if [ -n "$CVI" ]; then echo "$CVI"; else echo "TOUS"; fi

python3 src/drm-stock-recoltes-sorties.py "$CVI"
python3 src/drm-sortie-vrac-condionne.py "$CVI"
python3 src/drm-sortie-tous.py "$CVI"
python3 src/drm-sorties-cumul-par-mois.py "$CVI"
python3 src/drm-sorties-par-campagne-et-mois.py "$CVI"

if [ -n "$CVI" ];then
  python3 src/contrats-contractualisation-mes-clients.py "$CVI"
  python3 src/contrats-contractualisation-mes-clients-tableau-a-date.py "$CVI"
  python3 src/contrats-contractualisation-comparaison-deroulement-par-campagne.py "$CVI"
  python3 src/contrats-contractualisation-top10-5-dernieres-campagnes.py "$CVI"
  python3 src/informations-operateur.py "$CVI"
  python3 src/chiffres-cles.py "$CVI"
else
  cut -d ';' -f7 < data/contrats/export_bi_etablissements.csv | while read ID;
  do
    python3 src/contrats-contractualisation-mes-clients.py "$ID"
    python3 src/contrats-contractualisation-mes-clients-tableau-a-date.py "$ID"
    python3 src/contrats-contractualisation-comparaison-deroulement-par-campagne.py "$ID"
    python3 src/contrats-contractualisation-top10-5-dernieres-campagnes.py "$ID"
    python3 src/informations-operateur.py "$ID"
    python3 src/chiffres-cles.py "$ID"
  done
fi
