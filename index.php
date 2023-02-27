<?php
$path = "graphes/".$_GET['id'];
$ls_dossier_drm = array_diff(scandir($path."/drm"), array('.', '..'));
$ls_dossier_contrats = array_diff(scandir($path."/contrat"), array('.', '..'));

$json = file_get_contents($path."/".$_GET['id'].".json");
$data = json_decode($json, true);

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
              <a href="#drm"><button class="nav-link active" id="nav-drm-tab" data-onglet="drm" data-bs-toggle="tab" data-bs-target="#nav-drm" type="button" role="tab" aria-controls="nav-drm" aria-selected="true">DRM</button></a>
              <a href="#contrats"><button class="nav-link" id="nav-contrats-tab" data-onglet="contrats" data-bs-toggle="tab" data-bs-target="#nav-contrats" type="button" role="tab" aria-controls="nav-contrats" aria-selected="false">CONTRATS</button></a>
            </div>
          </nav>
          <div class="tab-content" id="nav-tabContent">
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
                <div class="mt-5">
                  <div class="row">
                    <div class="row shadow bg-white rounded" style="height: 750px;">
                      <div class="col-md-6 mt-4" style="height: 650px;">
                        <p class="entete text-center fw-bold">MA CAVE</p>
                        <div class="shadow bg-white rounded">
                          <?php include "graphes/".$_GET['id']."/drm/".$_GET['filtre']."/graphe1.html";?>
                        </div>
                      </div>
                      <div class="col-md-6 mt-4" style="height: 650px;">
                        <p class="entete-vignoble text-center fw-bold">LE VIGNOBLE</p>
                        <div class="shadow bg-white rounded">
                          <?php include "graphes/1-REFERENCE/drm/".$_GET['filtre']."/graphe1.html";?>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="row mt-3" >
                    <div class="row shadow bg-white rounded" style="height: 750px;">
                      <div class="col-md-6 mt-4" style="height: 650px;">
                        <p class="entete text-center fw-bold">MA CAVE</p>
                        <?php if( ! $_GET['bis']):?>
                          <div class="shadow bg-white rounded">
                            <?php include "graphes/".$_GET['id']."/drm/".$_GET['filtre']."/graphe2.html";?>
                          </div>
                        <?php else :?>
                          <div class="shadow bg-white rounded">
                            <?php include "graphes/".$_GET['id']."/drm/".$_GET['filtre']."/graphe2-bis.html";?>
                          </div>
                        <?php endif; ?>
                      </div>
                      <div class="col-md-6 mt-4" style="height: 650px;">
                        <p class="entete-vignoble text-center fw-bold">LE VIGNOBLE</p>
                        <?php if( ! $_GET['bis']):?>
                          <div class="shadow bg-white rounded">
                            <?php include "graphes/1-REFERENCE/drm/".$_GET['filtre']."/graphe2.html";?>
                          </div>
                        <?php else :?>
                          <div class="shadow bg-white rounded">
                            <?php include "graphes/1-REFERENCE/drm/".$_GET['filtre']."/graphe2-bis.html";?>
                          </div>
                        <?php endif; ?>
                      </div>
                    </div>
                  </div>
                  <div class="row mt-3">
                    <div class="row shadow bg-white rounded" style="height: 750px;">
                      <div class="col-md-6 mt-4" style="height: 650px;">
                        <p class="entete text-center fw-bold">MA CAVE</p>
                        <div class="shadow bg-white rounded">
                          <?php include "graphes/".$_GET['id']."/drm/".$_GET['filtre']."/graphe4.html";?>
                        </div>
                      </div>
                      <div class="col-md-6 mt-4" style="height: 650px;">
                        <p class="entete-vignoble text-center fw-bold">LE VIGNOBLE</p>
                        <div class="shadow bg-white rounded">
                          <?php include "graphes/1-REFERENCE/drm/".$_GET['filtre']."/graphe4.html";?>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="row mt-3">
                    <div class="row shadow bg-white rounded p-4 pt-5 pb-5">
                      <div class="col-md-12" style="height: 500px;">
                        <div class="shadow bg-white rounded">
                          <?php include "graphes/".$_GET['id']."/drm/".$_GET['filtre']."/graphe3.html";?>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            <div class="tab-pane fade" id="nav-contrats" role="tabpanel" aria-labelledby="nav-contrats-tab" tabindex="0" id="contrats" class="onglets mt-5 d-none">
                <div class="mt-3 d-flex align-items-end flex-column">
                  <div class="col-md-5 shadow bg-white rounded">
                    <select id="filtre-contrat" name="filtre-contrat" class="form-select form-control" onchange="changeFilter(this)">
                      <?php
                      foreach($list_produits_contrats as $filtre => $libelle):
                        if(in_array(str_replace("-1","-TOUT",$filtre),$ls_dossier_contrats))://si le dossier existe on l'affiche ?>
                          <option value="<?php echo str_replace("-1","-TOUT",$filtre);?>"><?php echo $libelle;?></option>
                      <?php endif;
                      endforeach;
                      ?>
                    </select>
                  </div>
                </div>
                <div class="shadow bg-white rounded">
                  <?php include "graphes/".$_GET['id']."/contrat/".$_GET['filtre']."/graphe1.html";?>
                </div>
              </div>
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
  </body>
</html>
<script src="web/main.js"></script>