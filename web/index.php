<?php

$debug = file_exists('../debug');

function include_with_debug($f) {
    global $debug;
    if ($debug && !file_exists($f)) {
        echo "<p><pre>ERROR $f not found</pre></p>";
    }else{
        include($f);
    }
}

$args = [
    'id' => FILTER_SANITIZE_STRING,
    'filtre' => FILTER_SANITIZE_STRING
];

$GET = filter_input_array(INPUT_GET, $args, true);
session_name('symfony');
session_start();

if (!isset($GET['id'])  || !$GET['id']) {
    if (!file_exists('../debug')) {
        header('Location: /');
        exit;
    }
}

$identifiant = $GET['id'];

if (
    !isset($_SESSION['etablissement_id']) || ! $_SESSION['etablissement_id']
    || (strpos($identifiant, ".") > 0)  || (strpos($identifiant, "/") > 0)
    || (($_SESSION['etablissement_id'] != $identifiant) && ($identifiant !== "CXXXX-01"))
   ) {
    if (!file_exists('../debug')) {
        header('Location: /');
        exit;
    }
}

if (! $GET['filtre']) {
    header('Location: ./?'.http_build_query(['id' => $identifiant, 'filtre' => 'TOUT-TOUT']));
    exit;
}

$path_cave = "../graphes/".$identifiant;
$path_vignoble = "../graphes/LE_VIGNOBLE";


if (! is_dir($path_cave."/drm") && ! is_dir($path_cave."/contrat")) {
    die('Il manque au moins les dossiers de données. La génération a été lancée ?');
}

$ls_dossier_drm = array_diff((scandir($path_cave."/drm")) ?: [], array('.', '..'));
$ls_dossier_contrats = array_diff((scandir($path_cave."/contrat")) ?: [], array('.', '..'));

$drm_graph_path               = $path_cave."/drm/".$GET['filtre'];
$drm_graph_le_vignoble_path     = $path_vignoble."/drm/".$GET['filtre'];
$contrat_graph_path           = $path_cave."/contrat/".$GET['filtre'];
$contrat_le_vignoble_graph_path = $path_vignoble."/contrat/".$GET['filtre'];

$json = file_get_contents($path_cave."/".$identifiant.".json");
$data = json_decode($json, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    die('Pas de données concernant cet opérateur.');
}

$json_chiffre = file_get_contents($path_cave."/".$identifiant."_chiffre.json");
$chiffres = json_decode($json_chiffre, true);


$list_produits_drm = $data['produits']['drm'];
$list_produits_contrats = $data['produits']['contrats'];

$dateDRM = strtotime(str_replace('/', '-', $chiffres['last_date_validation_campagne_en_cours']));
$dateContrat = strtotime(str_replace('/', '-', $chiffres['last_date_validation_contrat']));

$maxDate = date('d/m/Y', max($dateDRM, $dateContrat));

?><!DOCTYPE html>
<html lang='fr'>
<head>
    <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="main.css" rel="stylesheet">
    <title>Statistiques personnalisées pour <?php echo $data["name"];?></title>
    <script src="bootstrap/js/bootstrap.bundle.min.js"></script>
    <script src="jquery-3.2.1.min.js"></script>
    <script src="plotly-2.18.0.min.js"></script>
    <script src="plotly-locale-fr.js"></script>
    <script>Plotly.setPlotConfig({locale: 'fr',displaylogo: false})</script>
</head>
<body>
    <header>
      <div class="container">
        <div class="blog-header py-3">
            <div class="row flex-nowrap justify-content-between align-items-center">
                <div class="col-4 pt-1">
                    <a class="link-secondary p-2" href="/"><img src="img/logo_declarvins.png"/></a>
                </div>
                <div class="col-4 text-center">
                    &nbsp;
                </div>
                <div class="col-4 d-flex justify-content-end align-items-center link-declarvins">
                    <a class="btn btn-sm btn-outline-secondary" href="/logout">Se deconnecter</a>
                </div>
            </div>
        </div>
      </div>
      <div class="container">
        <div class="menu">
        <div class="nav-scroller px-3 col-10">
            <nav class="nav d-flex">
                <a href="/drm/<?php echo $identifiant; ?>" class="py-2 px-3 link-declarvins">DRM</a></li>
                <a href="/vrac/<?php echo $identifiant; ?>" class="py-2 px-3 link-declarvins">Contrat</a></li>
                <a href="." class="py-2 px-3 link-secondary active">Statistiques</a></li>
                <a href="/dae/<?php echo $identifiant; ?>" class="py-2 px-3 link-declarvins">Commercialisation</a></li>
                <a href="/facture/<?php echo $identifiant; ?>" class="py-2 px-3 link-declarvins">Factures</a></li>
                <a href="/subvention/etablissement/<?php echo $identifiant; ?>" class="py-2 px-3 link-declarvins">Aides Occitanie</a></li>
                <a href="/fichier/etablissement/<?php echo $identifiant; ?>" class="py-2 px-3 link-declarvins">Documents</a></li>
                <a href="/profil/<?php echo $identifiant; ?>" class="py-2 px-3 link-declarvins">Profil</a></li>
            </nav>
        </div>
        </div>
      </div>
    </header>
    <main class="container">
        <div class="d-flex justify-content-center">
          <div class="loader spinner-border m-5" role="status">
            <span class="sr-only"></span>
          </div>
        </div>
        <div class="p-4 p-md-5 mb-4 text-white bg-vvr-main">
            <div class="col-md-8 px-0">
                <h4><?php echo $data["name"];?> :</h4>
                <h1 class="text-uppercase" style="font-size: 2.5em;font-weight: normal;">Statistiques personnalisées</h1>
                <p class="lead my-3">Retrouvez ici les statistiques personnalisées issues de vos données de DRM et contrats. Les chiffres clés, ainsi que différents tableaux de bords dynamiques, vous permettront d’obtenir une vue d’ensemble de votre activité. Comparez les différentes campagnes, ou vos tendances avec l’ensemble du vignoble. Que cela soit en volume ou en valeur, les informations essentielles sur votre activité se trouvent dans les pages ci-après.</p>
            </div>
        </div>

        <div class="g-5">
            <?php if ($debug): ?>
            <div class="col-9">
                    <h4 style='color:red;'>DEBUG</h4>
            </div>
            <?php endif; ?>
            <div class="col-3 offset-9 text-muted text-end">
                <a class="text-decoration-none" style="color: inherit;" href="#" data-toggle="tooltip" data-placement="top" title="Dernière DRM : <?php echo $chiffres['last_date_validation_campagne_en_cours']; ?> Dernier Contrat : <?php echo $chiffres['last_date_validation_contrat']; ?>">Dernière mise à jour : <?php echo $maxDate;?></a>
            </div>
        </div>

        <article class="blog-post">
            <div class="container">
                <div class="content">
                  <?php if($json_chiffre): ?>
                    <div>
                        <div class="text-end">
                            <div class="row shadow bg-white rounded p-4 pt-5 pb-5">
                                <div class="col-12 entete text-center mb-4">
                                    <h3>Mes indicateurs globaux</h3>
                                </div>
                                <?php if ($chiffres["cumul_sortie_campagne_n_1"]): ?>
                                    <div class="col">
                                        <div class="chiffre chiffre-minor">
                                            <h3 class="mb-0">
                                                <?php echo number_format($chiffres["cumul_sortie_campagne_n_1"], 0, ',', '&nbsp;'); ?> hl
                                                <span class="fs-6 badge"> </span>
                                            </h3>
                                            <p>Total des volumes de sortie sur la <b style="color: #E94E56">campagne précédente</b></p>
                                        </div>
                                    </div>
                                <?php endif; ?>
                                <?php if ($chiffres["cumul_sortie_campagne_en_cours"]): ?>
                                    <div class="col">
                                        <div class="chiffre">
                                            <h3 class="mb-0">
                                                <?php echo number_format($chiffres["cumul_sortie_campagne_en_cours"], 0, ',', '&nbsp;'); ?> hl
                                                <a href="#" data-toggle="tooltip" data-placement="top" title="Évolution par rapport à la campagne précédente <?php echo "&nbsp;(".number_format($chiffres["cumul_sortie_campagne_n_1_a_date"], 0, ',', '&nbsp;')." hl"; ?> au <?php echo date('d/m/Y',strtotime('-1 year', strtotime(date("Y-m-d", strtotime(str_replace('/', '-',$chiffres['last_date_validation_campagne_en_cours'])))))).")"; ?>" ><span class="fs-6 badge <?php if($chiffres["evolution_cumul_sortie_campagne_en_cours"] >= 0):?>bg-success<?php else: ?>bg-danger <?php endif; ?>"><?php echo number_format($chiffres["evolution_cumul_sortie_campagne_en_cours"], 0, ',', '&nbsp;'); ?> %</span></a>
                                            </h3>
                                            <p>Volume de sortie sur la campagne en cours</p>
                                        </div>
                                    </div>
                                <?php endif; ?>
                                <?php if ($chiffres["volume_contractualisation"]): ?>
                                    <div class="col">
                                        <div class="chiffre left-border">
                                            <h3 class="mb-0">
                                                <?php echo number_format($chiffres["volume_contractualisation"], 0, ',', '&nbsp;'); ?> hl
                                                <a href="#" data-toggle="tooltip" data-placement="top" title="Évolution par rapport à la campagne précédente <?php echo "&nbsp;&nbsp;&nbsp;&nbsp;(".number_format($chiffres["volume_contractualisation_n_1"], 0, ',', '&nbsp;')." hl"; ?> au <?php echo date('d/m/Y',strtotime('-1 year', strtotime(date("Y-m-d", strtotime(str_replace('/', '-',$data["date"])))))).")"; ?>"><span  class="fs-6 badge <?php if($chiffres["evolution_par_rapport_a_n_1"] >= 0):?>bg-success<?php else: ?>bg-danger <?php endif; ?>"><?php if($chiffres["evolution_par_rapport_a_n_1"] >= 0):?>+<?php endif;echo number_format($chiffres["evolution_par_rapport_a_n_1"], 0, ',', '&nbsp;'); ?> %</span></a>
                                            </h3>
                                            <p>Volume contractualisé sur la campagne en cours</p>
                                        </div>
                                    </div>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                  <?php endif; ?>

                    <span id="drm"></span>
                    <span id="contrats"></span>

                    <nav class="row mt-5">
                        <div class="nav nav-tabs" id="nav-tab" role="tablist">
                            <?php if (count($ls_dossier_drm)): ?><a href="#drm"><button class="nav-link active" id="nav-drm-tab" data-onglet="drm" data-bs-toggle="tab" data-bs-target="#nav-drm" type="button" role="tab" aria-controls="nav-drm" aria-selected="true">DRM</button></a><?php endif; ?>
                            <?php if (count($ls_dossier_contrats)): ?><a href="#contrats"><button class="nav-link" id="nav-contrats-tab" data-onglet="contrats" data-bs-toggle="tab" data-bs-target="#nav-contrats" type="button" role="tab" aria-controls="nav-contrats" aria-selected="false">CONTRATS</button></a><?php endif; ?>
                        </div>
                    </nav>


                    <div class="tab-content" id="nav-tabContent">
                        <?php if (count($ls_dossier_drm)): ?>
                            <div class="tab-pane fade show active" id="nav-drm" role="tabpanel" aria-labelledby="nav-drm-tab" tabindex="0" class="onglets d-block">
                                <div class="mt-5">
                                    <div id="slide-1" class="row shadow bg-white p-1 graphs-container">
                                        <h3 class="col-xs-8 entete"><span>Stocks, récoltes et sorties</span></h3>
                                        <p class="explications">Évolution des stocks en début de campagne, des récoltes et des sorties de chais (hors replis, déclassement et vendanges fraîches) sur 10 campagnes.</p>
                                        <div class="col-xs-4"></div>
                                        <div class="mt-3 d-flex align-items-end flex-column">
                                            <div class="col-md-5 shadow bg-white rounded">
                                                <select id="filtre-drm" name="filtre-drm" class="form-select form-control" onchange="changeFilter(this)" data-slide="slide-1">
                                                <?php
                                                    foreach($list_produits_drm as $filtre => $libelle):
                                                        if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_drm))://si le dossier existe on l'affiche ?>
                                                            <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"
                                                            <?php if (str_replace('-1', '-TOUT', $filtre) === $GET['filtre']) { echo "selected"; } ?>
                                                            ><?php echo $libelle;?></option>
                                                        <?php endif;
                                                    endforeach;
                                                ?>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container graph-container-ma-cave">
                                            <?php include_with_debug($drm_graph_path."/drm-stock-recoltes-sorties.html");?>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container graph-container-le-vignoble">
                                            <?php include_with_debug($drm_graph_le_vignoble_path."/drm-stock-recoltes-sorties.html");?>
                                        </div>
                                        <div class="col-xs-12">
                                            <p class="text-muted text-end fs-6 mt-3">Sources : DRM Inter-Rhône</p>
                                        </div>
                                    </div>

                                    <div id="slide-2" class="mt-3 row shadow bg-white p-1 graphs-container">
                                        <h3 class="col-xs-12 entete"><span>Sorties de chais VRAC/Conditionné</span></h3>
                                        <p class="explications">Évolution des sorties de chais vrac (france et export), conditionné (crd france et export).</p>
                                        <div class="mt-3 d-flex align-items-end flex-column">
                                            <div class="col-md-5 shadow bg-white rounded">
                                                <select id="filtre-drm" name="filtre-drm" class="form-select form-control" onchange="changeFilter(this)" data-slide="slide-2">
                                                <?php
                                                    foreach($list_produits_drm as $filtre => $libelle):
                                                        if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_drm))://si le dossier existe on l'affiche ?>
                                                            <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"
                                                            <?php if (str_replace('-1', '-TOUT', $filtre) === $GET['filtre']) { echo "selected"; } ?>
                                                            ><?php echo $libelle;?></option>
                                                        <?php endif;
                                                    endforeach;
                                                ?>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container graph-container-ma-cave">
                                            <?php if(file_exists($drm_graph_path."/drm-sortie-vrac-condionne.html")): ?>
                                                <?php include_with_debug($drm_graph_path."/drm-sortie-vrac-condionne.html");?>
                                            <?php else: ?>
                                                <div class="col-xs-12 mt-5 p-5 text-center fw-bold entete</span>"><span>
                                                    <img height="400px" src="img/database-slash.svg" title="Données non disponible" />
                                                </div>
                                            <?php endif;?>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container graph-container-le-vignoble">
                                            <?php include_with_debug($drm_graph_le_vignoble_path."/drm-sortie-vrac-condionne.html");?>
                                        </div>
                                        <div class="col-xs-12">
                                            <p class="text-muted text-end fs-6  mt-3">En hl. Sources: DRM Inter-Rhône</p>
                                        </div>
                                    </div>

                                    <div id="slide-3" class="row mt-3 shadow bg-white p-1 graphs-container">
                                        <h3 class="col-xs-12 entete"><span>Sorties mensuelles</span></h3>
                                        <p class="explications">Évolution des sorties vrac (france et export), conditionné (crd france et export).</p>
                                        <div class="mt-3 d-flex align-items-end flex-column">
                                            <div class="col-md-5 shadow bg-white rounded">
                                                <select id="filtre-drm" name="filtre-drm" class="form-select form-control" onchange="changeFilter(this)" data-slide="slide-3">
                                                <?php
                                                    foreach($list_produits_drm as $filtre => $libelle):
                                                        if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_drm))://si le dossier existe on l'affiche ?>
                                                            <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"
                                                            <?php if (str_replace('-1', '-TOUT', $filtre) === $GET['filtre']) { echo "selected"; } ?>
                                                            ><?php echo $libelle;?></option>
                                                        <?php endif;
                                                    endforeach;
                                                ?>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container graph-container-ma-cave">
                                            <?php if(file_exists($drm_graph_path."/drm-sorties-par-campagne-et-mois.html")): ?>
                                                <?php include_with_debug($drm_graph_path."/drm-sorties-par-campagne-et-mois.html");?>
                                            <?php else: ?>
                                                <div class="col-xs-12 mt-5 p-5 text-center fw-bold entete</span>"><span>
                                                    <img height="400px" src="img/database-slash.svg" title="Données non disponible" />
                                                </div>
                                            <?php endif;?>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container graph-container-le-vignoble">
                                            <?php include_with_debug($drm_graph_le_vignoble_path."/drm-sorties-par-campagne-et-mois.html");?>
                                        </div>
                                        <div class="col-xs-12">
                                            <p class="text-muted text-end fs-6 mt-3">Sources: DRM Inter-Rhône</p>
                                        </div>
                                    </div>
                                <?php if(file_exists($drm_graph_path."/drm-sorties-cumul-par-mois.html")): ?>
                                    <div id="slide-4" class="row mt-3 shadow bg-white p-1 graphs-container">
                                        <h3 class="col-xs-12 entete"><span>Cumul des sorties de chais</span></h3>
                                        <p class="explications">Cumul de campagne sorties de chais vrac (france et export), conditionné (crd france et export).</p>
                                        <div class="mt-3 d-flex align-items-end flex-column">
                                            <div class="col-md-5 shadow bg-white rounded">
                                                <select id="filtre-drm" name="filtre-drm" class="form-select form-control" onchange="changeFilter(this)" data-slide="slide-4">
                                                <?php
                                                    foreach($list_produits_drm as $filtre => $libelle):
                                                        if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_drm))://si le dossier existe on l'affiche ?>
                                                            <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"
                                                            <?php if (str_replace('-1', '-TOUT', $filtre) === $GET['filtre']) { echo "selected"; } ?>
                                                            ><?php echo $libelle;?></option>
                                                        <?php endif;
                                                    endforeach;
                                                ?>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-12 mt-4 graph-container graph-container-ma-cave" style="height: 510px;">
                                            <?php include_with_debug($drm_graph_path."/drm-sorties-cumul-par-mois.html");?>
                                        </div>
                                        <div class="col-xs-12">
                                            <p class="text-muted text-end fs-6 mt-3">Sources: DRM Inter-Rhône</p>
                                        </div>
                                    </div>
                                <?php endif;?>
                            </div>
                            <?php if(count($ls_dossier_contrats)): ?>
                            <div class="btn-footer mt-5">
                                <div class="col-12 text-center">
                                    <a class="btn btn-primary btn-lg" onclick="$('#nav-contrats-tab').click();return false;" >Accéder à mes stats Contrat</a>
                                </div>
                            </div>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>

                    <?php if (count($ls_dossier_contrats)): ?>
                        <div class="tab-pane fade" id="nav-contrats" role="tabpanel" aria-labelledby="nav-contrats-tab" tabindex="0" class="onglets mt-5 d-none">
                            <div class="mt-5">
                                <?php if(file_exists($contrat_graph_path."/contrats-contractualisation-mes-clients-en-hl.html")): ?>
                                    <div id="slide-5" class="row mt-3 shadow bg-white p-1 graphs-container">
                                        <h3 class="col-xs-12 entete">
                                            Contractualisation moyenne par <?php echo ($data['is_producteur']) ? 'clients' : 'fournisseurs'; ?>
                                        </h3>
                                        <div class="pie-volume d-block">
                                          <p class="explications">
                                              Moyenne sur 5 ans des volumes contractualisés en hectolitres par <?php echo ($data['is_producteur']) ? 'clients' : 'fournisseurs'; ?>.
                                          </p>
                                        </div>
                                        <div class="pie-prix d-none">
                                          <p class="explications">
                                              Chiffre d'affaires annuel moyen réalisé par <?php echo ($data['is_producteur']) ? 'clients' : 'fournisseurs'; ?> sur 5 ans
                                          </p>
                                        </div>
                                        <div class="col-md-12 graph-container mt-3">
                                          <div class="col-2 btn-group mx-5 mt-3" role="group">
                                            <input type="radio" class="radio-btn-contrats btn-check" name="btnradio" id="btn-radio-volume" autocomplete="off" checked onclick="changeRadioValue(this)" data-toshow="pie-volume" data-tohide="pie-prix">
                                            <label class="btn btn-light" for="btn-radio-volume">en hl</label>
                                            <input type="radio" class="radio-btn-contrats btn-check" name="btnradio" id="btn-radio-prix" autocomplete="off" onclick="changeRadioValue(this)" data-toshow="pie-prix" data-tohide="pie-volume">
                                            <label class="btn btn-light" for="btn-radio-prix">en €</label>
                                          </div>
                                          <div class="d-flex align-items-end flex-column" style="margin-top: -40px;">
                                              <div class="col-md-5 shadow bg-white rounded">
                                                  <select id="filtre-contrats" name="filtre-contrats" class="form-select form-control" onchange="changeFilter(this)" data-slide="slide-5">
                                                      <?php
                                                      foreach($list_produits_contrats as $filtre => $libelle):
                                                          if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_contrats))://si le dossier existe on l'affiche ?>
                                                          <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"
                                                              <?php if (str_replace('-1', '-TOUT', $filtre) === $GET['filtre']) { echo "selected"; } ?>
                                                              ><?php echo $libelle;?></option>
                                                          <?php endif;
                                                      endforeach; ?>
                                                  </select>
                                              </div>
                                          </div>
                                          <div class="mt-3 pie-volume d-block">
                                            <div class="m-2 graph-container-ma-cave">
                                              <?php include_with_debug($contrat_graph_path."/contrats-contractualisation-mes-clients-en-hl.html");?>
                                            </div>
                                            <div class="col-xs-12">
                                                <p class="text-muted text-end fs-6 mt-3">
                                                    En hl. Sources: Contrats Inter-Rhône
                                                </p>
                                            </div>
                                          </div>
                                          <div class="mt-3 pie-prix d-none">
                                            <div class="m-2 graph-container-ma-cave">
                                              <?php include_with_debug($contrat_graph_path."/contrats-contractualisation-mes-clients-en-euros.html");?>
                                            </div>
                                            <div class="col-xs-12">
                                                <p class="text-muted text-end fs-6 mt-3">
                                                    En €. Sources: Contrats Inter-Rhône
                                                </p>
                                            </div>
                                          </div>
                                        </div>
                                    </div>
                                <?php endif;?>
                                <?php if(file_exists($contrat_graph_path."/contrats-contractualisation-top-10-5-dernieres-campagnes.html")): ?>
                                    <div id="slide-6" class="row mt-3 shadow bg-white p-1 graphs-container">
                                        <h3 class="col-xs-8 entete">
                                            Top 10 des <?php echo ($data['is_producteur']) ? 'clients' : 'fournisseurs'; ?>
                                        </h3>
                                        <p class="explications">
                                            Top 10 du volume total contractualisé par <?php echo ($data['is_producteur']) ? 'clients' : 'fournisseurs'; ?> sur les 5 dernières campagnes complètes.
                                        </p>
                                        <div class="mt-3 d-flex align-items-end flex-column">
                                            <div class="col-md-5 shadow bg-white rounded">
                                                <select id="filtre-contrats" name="filtre-contrats" class="form-select form-control" onchange="changeFilter(this)" data-slide="slide-6">
                                                    <?php
                                                    foreach($list_produits_contrats as $filtre => $libelle):
                                                        if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_contrats))://si le dossier existe on l'affiche ?>
                                                        <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"
                                                            <?php if (str_replace('-1', '-TOUT', $filtre) === $GET['filtre']) { echo "selected"; } ?>
                                                            ><?php echo $libelle;?></option>
                                                        <?php endif;
                                                    endforeach; ?>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-12 graph-container mt-3">
                                            <div class="col-xs-10 graph-container-ma-cave">
                                                <?php include_with_debug($contrat_graph_path."/contrats-contractualisation-top-10-5-dernieres-campagnes.html");?>
                                            </div>
                                            <p class="text-muted text-end fs-6 mt-3">
                                                En hl. Sources: Contrats Inter-Rhône
                                            </p>
                                        </div>
                                    </div>
                                <?php endif;?>
                                <?php if(file_exists($contrat_graph_path."/contrats-contractualisation-mes-clients-tableau-a-date.html")): ?>
                                    <div id="slide-7" class="row mt-3 shadow bg-white p-1 graphs-container">
                                        <h3 class="col-xs-8 pt-4 text-center fw-bold entete"><span>Contractualisations des <?php echo ($data['is_producteur']) ? 'clients' : 'fournisseurs'; ?> à date</span></h3>
                                        <p class="explications">Volumes contractualisés de la campagne en cours comparées à la campagne précédente et à la moyenne des 5 dernières campagnes. Les volumes sont exprimés en hectolitres.</p>
                                        <div class="mt-3 d-flex align-items-end flex-column">
                                            <div class="col-md-5 shadow bg-white rounded">
                                                <select id="filtre-contrats" name="filtre-contrats" class="form-select form-control" onchange="changeFilter(this)" data-slide="slide-7">
                                                    <?php
                                                    foreach($list_produits_contrats as $filtre => $libelle):
                                                        if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_contrats))://si le dossier existe on l'affiche ?>
                                                        <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"
                                                            <?php if (str_replace('-1', '-TOUT', $filtre) === $GET['filtre']) { echo "selected"; } ?>
                                                            ><?php echo $libelle;?></option>
                                                        <?php endif;
                                                    endforeach; ?>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-12 graph-container">
                                            <div class="col-xs-10 mt-3">
                                                <?php include_with_debug($contrat_graph_path."/contrats-contractualisation-mes-clients-tableau-a-date.html");?>
                                            </div>
                                            <p class="text-muted text-end fs-6 mt-3">
                                                En hl. Sources: Contrats Inter-Rhône
                                            </p>
                                        </div>
                                    </div>
                                <?php endif;?>
                                <?php if(file_exists($contrat_graph_path."/contrats-contractualisation-comparaison-deroulement-par-campagne.html")): ?>
                                    <div id="slide-8" class="row mt-3 shadow bg-white p-1 graphs-container">
                                        <h3 class="col-xs-8 pt-4 text-center fw-bold entete"><span>Déroulement de la campagne</span></h3>
                                        <p class="explications">
                                            Comparaison du cumul courant hebdomadaire des volumes contractualisés sur les 5 dernières campagnes.
                                        </p>
                                        <div class="d-flex align-items-end flex-column">
                                            <div class="col-md-5 shadow bg-white rounded">
                                                <select id="filtre-contrats" name="filtre-contrats" class="form-select form-control" onchange="changeFilter(this)" data-slide="slide-8">
                                                    <?php
                                                    foreach($list_produits_contrats as $filtre => $libelle):
                                                        if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_contrats))://si le dossier existe on l'affiche ?>
                                                        <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"
                                                            <?php if (str_replace('-1', '-TOUT', $filtre) === $GET['filtre']) { echo "selected"; } ?>
                                                            ><?php echo $libelle;?></option>
                                                        <?php endif;
                                                    endforeach; ?>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="mt-3 col-md-12 graph-container">
                                            <div class="col-xs-10 graph-container-ma-cave">
                                                <?php include_with_debug($contrat_graph_path."/contrats-contractualisation-comparaison-deroulement-par-campagne.html");?>
                                            </div>
                                            <p class="text-muted text-end fs-6 mt-3">
                                                En hl. Sources: Contrats Inter-Rhône
                                            </p>
                                        </div>
                                    </div>
                                <?php endif;?>
                            </div>
                            <?php if (count($ls_dossier_contrats)): ?>
                            <div class="mt-5 btn-footer">
                                <div class="col-12 text-center">
                                    <a class="btn btn-primary btn-lg" onclick="$('#nav-drm-tab').click();return false;" >Accéder à mes stats DRM</a>
                                </div>
                            </div>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                </div>
                </div>
            </div>
            <footer>
                <div class="container">
                    <div class="row">
                        <div class="col-md-6 text-left p-4">
                            <img height="40px" src="img/logo-footer.jpg"></img>
                        </div>
                        <div class="col-md-6 text-end p-4">
                            <img height="40px" src="img/logo.png"></img>
                        </div>
                    </div>
                </div>
            </footer>
        </article>
    </main>
    <script src="main.js"></script>
</body>
</html>
