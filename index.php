<?php

$args = [
    'id' => FILTER_SANITIZE_STRING,
    'filtre' => FILTER_SANITIZE_STRING,
    'bis' => FILTER_SANITIZE_STRING
];

$GET = filter_input_array(INPUT_GET, $args, true);

if (! $GET['id']) {
    die('Paramètre requis manquant : id');
}

$path = "graphes/".$GET['id'];
$ls_dossier_drm = array_diff(scandir($path."/drm"), array('.', '..'));
$ls_dossier_contrats = array_diff(scandir($path."/contrat"), array('.', '..'));

$drm_graph_path               = $path."/drm/".$GET['filtre'];
$drm_graph_reference_path     = "graphes/1-REFERENCE/drm/".$GET['filtre'];
$contrat_graph_path           = $path."/contrat/".$GET['filtre'];
$contrat_reference_graph_path = "graphes/1-REFERENCE/contrat/".$GET['filtre'];

$json = file_get_contents($path."/".$GET['id'].".json");
$data = json_decode($json, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    die('Erreur dans la lecture des données : '.json_last_error_msg());
}

$list_produits_drm = $data['produits']['drm'];
$list_produits_contrats = $data['produits']['contrats'];
?>

<html>
  <head>
    <link href="bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="web/main.css" rel="stylesheet">
    <script src="bootstrap/js/bootstrap.bundle.min.js"></script>
    <script src="web/plotly-2.18.0.min.js"></script>
  </head>
  <body>
    <nav class="navbar">
      <div class="container mt-2">
        <h2>
          ESPACE <span class="fw-bold">DE STATISTIQUES PERSONNALISES</span>
        </h2>
      <img height="40px" src="web/img/logo.png"></img>
      </div>
    </nav>
    <div class="container mt-5">
      <div class="content">
          <div>
              <h2>Statistiques et graphiques pour : <?php echo $data["name"];?> </h2>
          </div>
          <hr class="border border-danger border-2 opacity-50">
          <div>
            <p>"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."</p>
          </div>
          <div class="mt-5">
            <p class="mt-3">Dernière mise à jour : <?php echo $data["date"];?></p>
            <div class="row">
              <div class="row shadow bg-white rounded p-4 pt-5 pb-5">
                <div class="col-md-3">
                  <div class="chiffre">
                    <h2>35%</h2>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="chiffre">
                    <h2>1000hl</h2>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="chiffre">
                    <h2>60</h2>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="chiffre">
                    <h2>99%</h2>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
                    <select id="filtre" name="filtre" class="form-select form-control" onchange="changeFilter(this)">
                        <?php
                        foreach($list_produits_drm as $filtre => $libelle):
                            if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_drm))://si le dossier existe on l'affiche ?>
                                                  <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"><?php echo $libelle;?></option>
                        <?php endif;
                        endforeach;
                        ?>
                    </select>
                  </div>
                </div>

                <div class="mt-5 row">
                  <div class="row shadow bg-white rounded p-1">
                    <h3 class="col-xs-12 p-4 text-center fw-bold">Évolution des stocks, récoltes et sorties</h3>
                    <div class="col-md-6 mt-4" style="height: 650px;">
                        <?php include $drm_graph_path."/graphe1.html";?>
                    </div>
                    <div class="col-md-6 mt-4" style="height: 650px;">
                        <?php include $drm_graph_reference_path."/graphe1.html";?>
                    </div>
                    <div class="col-xs-12">
                      <p class="text-muted text-end fs-6">
                        En hl. Sorties hors replis, hors déclassements.</br>
                        Sources : DRM Inter-Rhône
                      </p>
                    </div>
                  </div>

                  <div class="mt-3 row shadow bg-white rounded p-1">
                    <h3 class="col-xs-12 p-4 text-center fw-bold">Évolution des sorties de chais VRAC/Conditionné</h3>
                      <div class="col-md-6 mt-4" style="height: 650px;">
                        <?php if( ! $GET['bis']):?>
                            <?php include $drm_graph_path."/graphe2.html";?>
                        <?php else :?>
                            <?php include $drm_graph_path."/graphe2-bis.html";?>
                        <?php endif; ?>
                      </div>
                      <div class="col-md-6 mt-4" style="height: 650px;">
                        <?php if( ! $GET['bis']):?>
                            <?php include $drm_graph_reference_path."/graphe2.html";?>
                        <?php else :?>
                            <?php include $drm_graph_reference_path."/graphe2-bis.html";?>
                        <?php endif; ?>
                      </div>
                      <div class="col-xs-12">
                        <p class="text-muted text-end fs-6">
                          En hl. Sources: DRM Inter-Rhône
                        </p>
                      </div>
                  </div>

                  <div class="row mt-3 shadow bg-white rounded p-1">
                    <h3 class="col-xs-12 p-4 text-center fw-bold">Évolution des sorties par trimestre</h3>
                      <div class="col-md-6 mt-4" style="height: 650px;">
                          <?php include $drm_graph_path."/graphe4.html";?>
                      </div>
                      <div class="col-md-6 mt-4" style="height: 650px;">
                          <?php include $drm_graph_reference_path."/graphe4.html";?>
                      </div>
                      <div class="col-xs-12">
                        <p class="text-muted text-end fs-6">
                          Sources: DRM Inter-Rhône
                        </p>
                      </div>
                  </div>

                  <div class="row mt-3 shadow bg-white rounded p-1">
                    <h3 class="col-xs-12 p-4 text-center fw-bold">Évolution des sorties de chais par mois</h3>
                      <div class="col-md-12" style="height: 500px;">
                          <?php include $drm_graph_path."/graphe3.html";?>
                      </div>
                      <div class="col-xs-12">
                        <p class="text-muted text-end fs-6">
                          En hl, Cumul depuis le début de la campagne).
                          Sources: DRM Inter-Rhône
                        </p>
                      </div>
                  </div>
                </div>
              </div>
            <?php endif; ?>

            <?php if (count($ls_dossier_contrats)): ?>
            <div class="tab-pane fade" id="nav-contrats" role="tabpanel" aria-labelledby="nav-contrats-tab" tabindex="0" id="contrats" class="onglets mt-5 d-none">
                <div class="mt-3 d-flex align-items-end flex-column">
                  <div class="col-md-5 shadow bg-white rounded">
                    <select id="filtre-contrat" name="filtre-contrat" class="form-select form-control" onchange="changeFilter(this)">
                        <?php
                        foreach($list_produits_contrats as $filtre => $libelle):
                            if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_contrats))://si le dossier existe on l'affiche ?>
                              <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"><?php echo $libelle;?></option>
                            <?php endif;
                        endforeach; ?>
                    </select>
                  </div>
                </div>
                <?php if(file_exists($contrat_graph_path."/graphe1.html")): ?>
                <div class="mt-3 row shadow bg-white rounded p-1">
                  <h3 class="col-xs-12 p-4 text-center fw-bold">Contractualisation</h3>
                    <div class="col-md-6 mt-4" style="height: 650px;">
                        <?php include $contrat_graph_path."/graphe1.html";?>
                    </div>
                    <div class="col-md-6 mt-4" style="height: 650px;">
                      <?php include $contrat_graph_path."/graphe2.html";?>
                    </div>
                    <div class="col-xs-12">
                      <p class="text-muted text-end fs-6">
                        En hl. Sources: DRM Inter-Rhône
                      </p>
                    </div>
                </div>
                <?php endif;?>
                <?php if(file_exists($contrat_graph_path."/graphe3.html")): ?>
                  <div class="mt-3 row shadow bg-white rounded p-1">
                  <?php include $contrat_graph_path."/graphe3.html";?>
                  </div>
                <?php endif;?>
              </div>
            <?php endif; ?>
          </div>
        </div>
    </div>
    <footer>
      <div class="container">
        <div class="row">
          <div class="col-md-6 text-left p-4">
            <img height="40px" src="web/img/logo-footer.jpg"></img>
          </div>
          <div class="col-md-6 text-end p-4">
            <img height="40px" src="web/img/logo.png"></img>
          </div>
        </div>
      </div>
    </footer>
    <script src="web/main.js"></script>
  </body>
</html>
