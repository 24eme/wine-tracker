 #!/usr/bin/python3
 
import pandas as pd
import subprocess
csv = "../../data/drm/export_bi_drm_stock.csv"  #il manque un ; à la fin du header.
drm = pd.read_csv(csv, sep=";",encoding="iso8859_15")

identifiants = drm.identifiant.unique()
for id_operateur in identifiants:
    subprocess.call(['./wine-tracker-drm-stock-recoltes-sorties.py', id_operateur])
    subprocess.call(['./wine-tracker-drm-sortie_vrac_condionne.py', id_operateur])
    subprocess.call(['./wine-tracker-drm-sorties-par-mois.py', id_operateur])