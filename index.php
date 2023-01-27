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
              <h2>Statistiques et graphiques pour : <?php echo "XXXXXXXXXXX" ?> </h2>
          </div>
          <hr class="border border-danger border-2 opacity-50">
          <div>
            <p>"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."</p>
          </div>
          
          <div class="mt-5">
            <h4>Statistiques</h4>
            <ul class="nav nav-tabs">
              <li class="nav-item">
                <a class="nav-link active" aria-current="page" href="#">DRM</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">CONTRATS</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">AUTRES</a>
              </li>
            </ul>
            <p class="mt-3" >Dernière mise à jour : XX/XX/XXXX</p>
          </div>
          
          <div class="row">
            <div class="col-md-6" style="height: 500px;">
              <div class="shadow bg-white rounded">
                <?php include "graphes/".$_GET['id']."_graphe1.html";?>
              </div>
            </div>
            <div class="col-md-6" style="height: 500px;">
              <?php if( ! $_GET['bis']):?>
                <div class="shadow bg-white rounded">
                  <?php include "graphes/".$_GET['id']."_graphe2.html";?>
                </div>
              <?php else :?>
                <div class="shadow bg-white rounded">
                  <?php include "graphes/".$_GET['id']."_graphe2bis.html";?>
                </div>
              <?php endif; ?>
            </div>
            <div>
              <div class="row mt-3">
                <div class="col-md-12" style="height: 500px;">
                  <div class="shadow bg-white rounded">
                    <?php include "graphes/".$_GET['id']."_graphe3.html";?>
                  </div>
                </div>
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
