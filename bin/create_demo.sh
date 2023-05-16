
if ! test -f debug ; then
	echo "No debug : disabled";
	exit 1;
fi

id=$(cat debug)

head -n 1 data/drm/export_bi_drm_stock.csv > data/drm/export_bi_drm_stock_demo.csv
grep -aE "$id" data/drm/export_bi_drm_stock.csv | grep -aE ';CDR;|;CRH;|;CVX;|;SJO;' | sed 's/C....-01/CXXXX-01/g' | awk -F ';' 'OFS=";" {$20="Chateau demo"; print $0}'  >> data/drm/export_bi_drm_stock_demo.csv

head -n 1 data/drm/export_bi_mouvements.csv > data/drm/export_bi_mouvements_demo.csv
grep -aE "$id" data/drm/export_bi_mouvements.csv | grep -aE ';CDR;|;CRH;|;CVX;|;SJO;' | sed 's/C....-01/CXXXX-01/g' >> data/drm/export_bi_mouvements_demo.csv

head -n 1 data/contrats/export_bi_contrats.csv > data/contrats/export_bi_contrats_demo.csv
grep -aE "$id" data/contrats/export_bi_contrats.csv | grep -aE ';CDR;|;CRH;|;CVX;|;SJO;' | sed 's/C....-01/CXXXX-01/g' | awk -F ';' 'OFS=";"{$7="C"int(rand()*10); $8="Nego "$7; $10="vendeur"; if ($12) {$11 = "C"int(rand()*10); $12="courtier "$11; } print $0}' >> data/contrats/export_bi_contrats_demo.csv

head -n 1 data/contrats/export_bi_etablissements.csv > data/contrats/export_bi_etablissements_demo.csv
grep -aE "$id" data/contrats/export_bi_etablissements.csv | sed 's/C....-01/CXXXX-01/g' |  head -n 1 | iconv -f iso88591 | awk -F ';' 'OFS=";"{$6="";$8="Chateau démo";$10="Chateau démo";$11="";$14="";$16="";$17="";$21="";print $0}' | iconv -t iso88591  > data/contrats/export_bi_etablissements_demo.$$.csv
cat data/contrats/export_bi_etablissements_demo.$$.csv >> data/contrats/export_bi_etablissements_demo.csv
for i in 0 1 2 3 4 5 6 7 8 9; do
	cat data/contrats/export_bi_etablissements_demo.$$.csv | sed 's/CXXXX-01/"C'$i'"/g' | awk -F ';' 'OFS=";"{$6="";$8="Nego '$i'";$10="Nego '$i'";$11="";$14="";$16="";$17="";$21="";print $0}' >> data/contrats/export_bi_etablissements_demo.csv
done
rm data/contrats/export_bi_etablissements_demo.$$.csv

if ! grep -l _demo.csv src/*/*py > /dev/null ; then
	sed -i 's/\.csv/_demo.csv/' src/*/*py
fi

bash bin/generate_macave.sh CXXXX-01

sed -i 's/_demo.csv/.csv/' src/*/*py
