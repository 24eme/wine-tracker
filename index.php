<?php
$path = "graphes/".$_GET['id'];
$filtres = array_diff(scandir($path."/drm"), array('.', '..',$_GET['id'].".json"));

function replace_TOUT($filtre){
  return str_replace("-TOUT",'-1',$filtre);
}
$filtres = array_map('replace_TOUT', $filtres);
sort($filtres);

#choix TOUT au tout début.
$index = array_search("TOUT-1",$filtres);
$touttout = $filtres[$index];
unset($filtres[$index]);
array_unshift($filtres, $touttout);

$json = file_get_contents($path."/".$_GET['id'].".json");
$data = json_decode($json, true);

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
          <div class="mt-5">
            <ul id="nav-bar" class="nav nav-tabs">
              <li class="nav-item">
                <a class="nav-link active" aria-current="page" href="#nav-bar" data-show="drm">DRM</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#nav-bar" data-show="contrats" >CONTRATS</a>
              </li>
            </ul>
          </div>
          <div id="drm" class="onglets d-block">
            <div class="mt-3 d-flex align-items-end flex-column">
              <div class="col-md-5 shadow bg-white rounded">
                <select id="filtre" name="filtre" class="form-select form-control" onchange="changeFilter(this)">
                  <?php foreach($filtres as $f):
                    $f = str_replace("-1","-TOUT",$f);
                    preg_match("/(.+)-(.+)/",$f,$splitappellation);
                    $appellation = $splitappellation[1]; ?>
                    <?php if(array_key_exists($f,$data['produits'][$appellation])):?>
                      <option value="<?php echo str_replace("-1","-TOUT",$f);?>"><?php echo $data['produits'][$appellation][$f];?></option>
                    <?php endif;?>
                  <?php endforeach; ?>
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
                    <p class="entete text-center fw-bold">LE VIGNOBLE</p>
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
                    <p class="entete text-center fw-bold">LE VIGNOBLE</p>
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
        </div>
        <div id="contrats" class="onglets mt-5 d-none">
          <p>POUR LES CONTRATS</p>
          <div class="shadow bg-white rounded">
            <p> GRAPHES CONTRATS</p>
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


<script>

  //option selectionné est le filtre qui est dans l'url
  document.addEventListener("DOMContentLoaded", function(event) {
    var href = new URL(window.location.href);
    document.getElementById('filtre').value = href.searchParams.get('filtre');
  });

  // quand on change de filtre l'url est mis à jour et la page est rechargée.
  function changeFilter(filtre){
    var href = new URL(window.location.href);
    href.searchParams.set('filtre',filtre.value);
    window.location = href;
  }

  document.addEventListener('click', function(e) {

      if( e.target.className.baseVal != "legendtoggle"){
        return;
      }

      var tab = document.getElementsByClassName('legendtext');
      var elementlegendtext = e.target.previousElementSibling.previousElementSibling;

      for( const element of tab){
        if(element.dataset.unformatted == elementlegendtext.dataset.unformatted && element != elementlegendtext){
          element.setAttribute("id","temp");
          document.getElementById("temp").nextElementSibling.nextElementSibling.dispatchEvent(new Event('mouseup'));
          element.removeAttribute("id");
        }
      }
  });


  var onglets = document.getElementById("nav-bar");
  onglets.addEventListener("click",function(e){
     if(e.target.tagName != "A"){
       return;
     }
     active = onglets.querySelector(".active");
     active.classList.remove("active");
     document.getElementById(active.dataset.show).classList.remove("d-block");
     document.getElementById(active.dataset.show).classList.add("d-none");

     e.target.classList.add("active");
     document.getElementById(e.target.dataset.show).classList.remove("d-none");
     document.getElementById(e.target.dataset.show).classList.add("d-block");
  });

</script>