<?php

$args = [
    'id' => FILTER_SANITIZE_STRING,
    'filtre' => FILTER_SANITIZE_STRING,
    'bis' => FILTER_SANITIZE_STRING
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

if (! $_SESSION['etablissement_id'] || !isset($_SESSION['etablissement_id']) || ($_SESSION['etablissement_id'] != $identifiant) ) {
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

$json_chiffre = file_get_contents($path_cave."/".$identifiant."_chiffre.json");
$chiffres = json_decode($json_chiffre, true);


if (json_last_error() !== JSON_ERROR_NONE) {
    die('Erreur dans la lecture des données : '.json_last_error_msg());
}

$list_produits_drm = $data['produits']['drm'];
$list_produits_contrats = $data['produits']['contrats'];
?><!DOCTYPE html>
<html lang='fr'>
<head>
    <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="main.css" rel="stylesheet">
    <title>Statistiques personnalisées pour <?php echo $data["name"];?></title>
    <script src="bootstrap/js/bootstrap.bundle.min.js"></script>
    <script src="plotly-2.18.0.min.js"></script>
</head>
<body>
    <header class="container">
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

        <div class="nav-scroller py-1 mb-2 col-8">
            <nav class="nav d-flex justify-content-between">
                <a href="/drm/<?php echo $identifiant; ?>" class="p-2 link-declarvins">DRM</a></li>
                <a href="/vrac/<?php echo $identifiant; ?>" class="p-2 link-declarvins">Contrat</a></li>
                <a href="." class="p-2 link-secondary active">Statistiques</a></li>
                <a href="/dae/<?php echo $identifiant; ?>" class="p-2 link-declarvins">Commercialisation</a></li>
                <a href="/facture/<?php echo $identifiant; ?>" class="p-2 link-declarvins">Factures</a></li>
                <a href="/subvention/etablissement/<?php echo $identifiant; ?>" class="p-2 link-declarvins">Aides Occitanie</a></li>
                <a href="/fichier/etablissement/<?php echo $identifiant; ?>" class="p-2 link-declarvins">Documents</a></li>
                <a href="/profil/<?php echo $identifiant; ?>" class="p-2 link-declarvins">Profil</a></li>
            </nav>
        </div>
    </header>

    <main class="container">
        <div class="p-4 p-md-5 mb-4 text-white rounded bg-vvr-main">
            <div class="col-md-6 px-0">
                <h1 class="display-4 fst-italic">Espace de statistiques personnalisées</h1>
                <p class="lead my-3">"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."</p>
            </div>
        </div>

        <div class="row g-5">
            <div class="col-3 offset-9 text-muted">
                Dernière mise à jour : <?php echo $data["date"];?>
            </div>
            <h3 class="pb-4 mb-4 fst-italic border-bottom">
                Statistiques et graphiques pour <?php echo $data["name"];?>
                <?php
                if (file_exists('../debug')) {
                    echo "<span style='color:red;'>DEBUG</span>";
                }
                ?>
            </h3>
        </div>

        <article class="blog-post">
            <div class="container mt-5">
                <div class="content">
                    <div class="mt-5">
                        <div class="row">
                            <div class="row shadow bg-white rounded p-4 pt-5 pb-5">
                                <?php if ($chiffres["cumul_sortie_campagne_en_cours"]): ?>
                                    <div class="col">
                                        <div class="chiffre">
                                            <h2 class="mb-0 end"><?php echo number_format($chiffres["cumul_sortie_campagne_en_cours"], 0, ',', '&nbsp;'); ?> hl <span title="Evolution par rapport à l'année précédente" class="fs-6 badge <?php if($chiffres["evolution_mois_par_rapport_a_n_1"] >= 0):?>bg-success<?php else: ?>bg-danger <?php endif; ?>"><?php echo number_format($chiffres["evolution_mois_par_rapport_a_n_1"], 0, ',', '&nbsp;'); ?> %</span></h2>
                                            <p>Cumul volume de sortie depuis le début de la campagne</p>
                                        </div>
                                    </div>
                                <?php endif; ?>
                                <?php if ($chiffres["volume_de_sortie_vrac"]): ?>
                                    <div class="col">
                                        <div class="chiffre">
                                            <h2 class="mb-0"><?php echo number_format($chiffres["volume_de_sortie_vrac"], 0, ',', '&nbsp;'); ?> hl <span title="Evolution par rapport à l'année précédente" class="fs-6 badge <?php if($chiffres["evolution_sorite_vrac_mois_par_rapport_a_n_1"] >= 0):?>bg-success<?php else: ?>bg-danger <?php endif; ?>"><?php echo number_format($chiffres["evolution_sorite_vrac_mois_par_rapport_a_n_1"], 0, ',', '&nbsp;'); ?> %</span></h2>
                                            <p>Volume de sortie VRAC du mois précédent</p>
                                        </div>
                                    </div>
                                <?php endif; ?>
                                <?php if ($chiffres["volume_sortie_conditionne_mois"]): ?>
                                    <div class="col">
                                        <div class="chiffre">
                                            <h2 class="mb-0"><?php echo number_format($chiffres["volume_sortie_conditionne_mois"], 0, ',', '&nbsp;'); ?> hl <span title="Evolution par rapport à l'année précédente" class="fs-6 badge <?php if($chiffres["evolution_sortie_conditionne_du_mois"] >= 0):?>bg-success<?php else: ?>bg-danger <?php endif; ?>"><?php echo number_format($chiffres["evolution_sortie_conditionne_du_mois"], 0, ',', '&nbsp;'); ?> %</span></h2>
                                            <p>Volume de sortie conditionné du mois précédent</p>
                                        </div>
                                    </div>
                                <?php endif; ?>
                                <?php if ($chiffres["volume_contractualisation"]): ?>
                                    <div class="col">
                                        <div class="chiffre">
                                            <h2 class="mb-0"><?php echo number_format($chiffres["volume_contractualisation"], 0, ',', '&nbsp;'); ?> hl <span title="Evolution par rapport à l'année précédente" class="fs-6 badge <?php if($chiffres["evolution_par_rapport_a_n_1"] >= 0):?>bg-success<?php else: ?>bg-danger <?php endif; ?>"><?php echo number_format($chiffres["evolution_par_rapport_a_n_1"], 0, ',', '&nbsp;'); ?> %</span></h2>
                                            <p>Volume contractualisation depuis le début de la campagne</p>
                                        </div>
                                    </div>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>


                    <span id="drm"></span>
                    <span id="contrats"></span>

                    <nav class="mt-5">
                        <div class="nav nav-tabs" id="nav-tab" role="tablist">
                            <?php if (count($ls_dossier_drm)): ?><a href="#drm"><button class="nav-link active" id="nav-drm-tab" data-onglet="drm" data-bs-toggle="tab" data-bs-target="#nav-drm" type="button" role="tab" aria-controls="nav-drm" aria-selected="true">DRM</button></a><?php endif; ?>
                            <?php if (count($ls_dossier_contrats)): ?><a href="#contrats"><button class="nav-link" id="nav-contrats-tab" data-onglet="contrats" data-bs-toggle="tab" data-bs-target="#nav-contrats" type="button" role="tab" aria-controls="nav-contrats" aria-selected="false">CONTRATS</button></a><?php endif; ?>
                        </div>
                    </nav>


                    <div class="tab-content" id="nav-tabContent">
                        <?php if (count($ls_dossier_drm)): ?>
                            <div class="tab-pane fade show active" id="nav-drm" role="tabpanel" aria-labelledby="nav-drm-tab" tabindex="0" id="drm" class="onglets d-block">
                                <div class="mt-3 d-flex align-items-end flex-column">
                                    <div class="col-md-5 shadow bg-white rounded">
                                        <select id="filtre-drm" name="filtre-drm" class="form-select form-control" onchange="changeFilter(this)">
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

                                <div class="mt-5 row">
                                    <div class="row shadow bg-white rounded p-1 graphs-container">
                                        <h3 class="col-xs-12 p-4 text-center fw-bold">Évolution des stocks, récoltes et sorties</h3>
                                        <div class="col-md-6 mt-4 graph-container" style="height: 650px;">
                                            <?php include $drm_graph_path."/drm-stock-recoltes-sorties.html";?>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container" style="height: 650px;">
                                            <?php include $drm_graph_le_vignoble_path."/drm-stock-recoltes-sorties.html";?>
                                        </div>
                                        <div class="col-xs-12">
                                            <p class="text-muted text-end fs-6">
                                                En hl. Sorties hors replis, hors déclassements.</br>
                                                Sources : DRM Inter-Rhône
                                            </p>
                                        </div>
                                    </div>

                                    <div class="mt-3 row shadow bg-white rounded p-1 graphs-container">
                                        <h3 class="col-xs-12 p-4 text-center fw-bold">Évolution des sorties de chais VRAC/Conditionné</h3>
                                        <div class="col-md-6 mt-4 graph-container" style="height: 650px;">
                                            <?php if(file_exists($drm_graph_path."/drm-sortie-vrac-condionne.html")): ?>
                                                <?php include $drm_graph_path."/drm-sortie-vrac-condionne.html";?>
                                            <?php else: ?>
                                                <div class="col-xs-12 mt-5 p-5 text-center fw-bold entete">
                                                    <img height="400px" src="img/database-slash.svg" title="Données non disponible" />
                                                </div>
                                            <?php endif;?>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container" style="height: 650px;">
                                            <?php include $drm_graph_le_vignoble_path."/drm-sortie-vrac-condionne.html";?>
                                        </div>
                                        <div class="col-xs-12">
                                            <p class="text-muted text-end fs-6">
                                                En hl. Sources: DRM Inter-Rhône
                                            </p>
                                        </div>
                                    </div>

                                    <div class="row mt-3 shadow bg-white rounded p-1 graphs-container">
                                        <h3 class="col-xs-12 p-4 text-center fw-bold">Évolution des sorties par mois - campagne</h3>
                                        <div class="col-md-6 mt-4 graph-container" style="height: 650px;">
                                            <?php if(file_exists($drm_graph_path."/drm-sorties-par-campagne-et-mois.html")): ?>
                                                <?php include $drm_graph_path."/drm-sorties-par-campagne-et-mois.html";?>
                                            <?php else: ?>
                                                <div class="col-xs-12 mt-5 p-5 text-center fw-bold entete">
                                                    <img height="400px" src="img/database-slash.svg" title="Données non disponible" />
                                                </div>
                                            <?php endif;?>
                                        </div>
                                        <div class="col-md-6 mt-4 graph-container" style="height: 650px;">
                                            <?php include $drm_graph_le_vignoble_path."/drm-sorties-par-campagne-et-mois.html";?>
                                        </div>
                                        <div class="col-xs-12">
                                            <p class="text-muted text-end fs-6">
                                                Sources: DRM Inter-Rhône
                                            </p>
                                        </div>
                                    </div>
                                <?php if(file_exists($drm_graph_path."/drm-sorties-cumul-par-mois.html")): ?>
                                    <div class="row mt-3 shadow bg-white rounded p-1 graphs-container">
                                        <h3 class="col-xs-12 p-4 text-center fw-bold entete">Cumul de l'évolution des sorties de chais par mois</h3>
                                        <h4 class="col-xs-12 text-center fw-bold">MA CAVE</h4>
                                        <div class="col-md-12 graph-container" style="height: 500px;">
                                            <?php include $drm_graph_path."/drm-sorties-cumul-par-mois.html";?>
                                        </div>
                                    </div>
                                <?php endif;?>
                            </div>
                        </div>
                    <?php endif; ?>

                    <?php if (count($ls_dossier_contrats)): ?>
                        <div class="tab-pane fade" id="nav-contrats" role="tabpanel" aria-labelledby="nav-contrats-tab" tabindex="0" id="contrats" class="onglets mt-5 d-none">
                            <div class="mt-3 d-flex align-items-end flex-column">
                                <div class="col-md-5 shadow bg-white rounded">
                                    <select id="filtre-contrats" name="filtre-contrats" class="form-select form-control" onchange="changeFilter(this)">
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
                            <div class="mt-5 row">
                                <?php if(file_exists($contrat_graph_path."/contrats-contractualisation-mes-clients-en-hl.html")): ?>
                                    <div class="mt-3 row shadow bg-white rounded p-1">
                                        <h3 class="col-xs-12 p-4 text-center fw-bold entete">Moyenne contractualisation sur les 5 dernières campagnes</h3>
                                        <div class="col-2 btn-group" role="group">
                                            <input type="radio" class="radio-btn-contrats btn-check" name="btnradio" id="btn-radio-volume" autocomplete="off" checked onclick="changeRadioValue(this)" data-toshow="pie-volume" data-tohide="pie-prix">
                                            <label class="btn btn-light" for="btn-radio-volume">en hl</label>
                                            <input type="radio" class="radio-btn-contrats btn-check" name="btnradio" id="btn-radio-prix" autocomplete="off" onclick="changeRadioValue(this)" data-toshow="pie-prix" data-tohide="pie-volume">
                                            <label class="btn btn-light" for="btn-radio-prix">en €</label>
                                        </div>
                                        <div id="pie-volume" class="d-block">
                                            <?php include $contrat_graph_path."/contrats-contractualisation-mes-clients-en-hl.html";?>
                                            <div class="col-xs-12">
                                                <p class="text-muted text-end fs-6">
                                                    En hl. Sources: Contrats Inter-Rhône
                                                </p>
                                            </div>
                                        </div>
                                        <div id="pie-prix" class="d-none">
                                            <?php include $contrat_graph_path."/contrats-contractualisation-mes-clients-en-euros.html";?>
                                            <div class="col-xs-12">
                                                <p class="text-muted text-end fs-6">
                                                    En €. Sources: Contrats Inter-Rhône
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                <?php endif;?>
                                <?php if(file_exists($contrat_graph_path."/contrats-contractualisation-mes-clients-tableau-a-date.html")): ?>
                                    <div class="mt-3 row shadow bg-white rounded p-1">
                                        <h3 class="col-xs-8 pt-4 text-center fw-bold entete">Comparaison à date des contractualisations</h3>
                                        <h4 class="col-xs-8 p-1 pb-4 text-center fw-bold entete">Évolution de volume contractualisé comparée à la campagne précédente et à la moyenne des 5 dernières campagnes</h4>
                                        <div class="col-xs-10">
                                            <?php include $contrat_graph_path."/contrats-contractualisation-mes-clients-tableau-a-date.html";?>
                                        </div>
                                        <p class="text-muted text-end fs-6">
                                            En hl. Sources: Contrats Inter-Rhône
                                        </p>
                                    </div>
                                <?php endif;?>
                                <?php if(file_exists($contrat_graph_path."/contrats-contractualisation-top-10-5-dernieres-campagnes.html")): ?>
                                    <div class="mt-3 row shadow bg-white rounded p-1">
                                        <h3 class="col-xs-8 p-4 text-center fw-bold entete">Top 10 des volumes des tiers sur 5 ans</h3>
                                        <div class="col-xs-10">
                                            <?php include $contrat_graph_path."/contrats-contractualisation-top-10-5-dernieres-campagnes.html";?>
                                        </div>
                                        <p class="text-muted text-end fs-6">
                                            En hl. Sources: Contrats Inter-Rhône
                                        </p>
                                    </div>
                                <?php endif;?>
                                <?php if(file_exists($contrat_graph_path."/contrats-contractualisation-comparaison-deroulement-par-campagne.html")): ?>
                                    <div class="mt-3 row shadow bg-white rounded p-1">
                                        <h3 class="col-xs-8 p-4 text-center fw-bold entete">Comparaison déroulement de la campagne sur les 5 dernières campagnes</h3>
                                        <div class="col-xs-10">
                                            <?php include $contrat_graph_path."/contrats-contractualisation-comparaison-deroulement-par-campagne.html";?>
                                        </div>
                                        <p class="text-muted text-end fs-6">
                                            En hl. Sources: Contrats Inter-Rhône
                                        </p>
                                    </div>
                                <?php endif;?>
                            </div>
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
