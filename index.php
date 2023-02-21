<?php
$path = "graphes/".$_GET['id']."/drm";
$filtres = array_diff(scandir($path), array('.', '..'));

#choix TOUT-TOUT au tout début.
$index = array_search("TOUT-TOUT",$filtres);
$touttout = $filtres[$index];
unset($filtres[$index]);
array_unshift($filtres, $touttout);
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
              <h2>Statistiques et graphiques pour : <?php echo "XXXXXXXXXXX" ?> </h2>
          </div>
          <hr class="border border-danger border-2 opacity-50">
          <div>
            <p>"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."</p>
          </div>
          
          <div class="mt-5">
            <h4>Statistiques</h4>
            <ul class="nav nav-tabs">
              <li id="drm" class="nav-item">
                <a class="nav-link active" aria-current="page" href="#">DRM</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">CONTRATS</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">AUTRES</a>
              </li>
            </ul>
            <p class="mt-3">Dernière mise à jour : XX/XX/XXXX</p>
          </div>
          <div class="mt-5">
            <div class="col-md-5 shadow bg-white rounded">
              <select id="filtre" name="filtre" class="form-select form-control" onchange="changeFilter(this)">
                <?php foreach($filtres as $f): ?>
                  <option value="<?php echo($f);?>"><?php echo($f);?></option>
                <?php  endforeach; ?>
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
            <div>
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
            <div>
              <div class="row mt-3">
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

  // document.addEventListener('dblclick', function(e) {
  //     if( e.target.className.baseVal != "legendtoggle"){
  //       return;
  //     }
  //     var tab = document.getElementsByClassName('legendtext');
  //     var elementclicked = e.target.previousElementSibling.previousElementSibling;
  //     //je désactive tout :
  //     for(const element of tab){
  //       if(element.dataset.unformatted == elementclicked.dataset.unformatted && element != elementclicked){
  //         var tab2 = element.parentNode.parentNode.parentNode.parentNode.getElementsByClassName('legendtoggle');
  //         for( const el of tab2){
  //           el.dispatchEvent(new Event('mouseup'));
  //         }
  //         break;
  //       }
  //     }
  //
  //     //ok  -----------
  //
  //     //si un de mes voisins vaut 0.5 en opacity alors je clique sur mon jumeau :
  //     var elementstracesfromsamegraphe = e.target.parentNode.parentNode.parentNode.getElementsByClassName('traces'); //moi et mes voisins
  //     for (n of elementstracesfromsamegraphe){
  //       console.log(n.style.opacity);
  //       if(n.style.opacity == 0.5 ){ //si un de mes voisins est grisé je click sur mon jumeau :
  //         console.log(tab2) //tab2 a tous les elements voisins dont mon jumeau
  //         for(const element of tab2){
  //           if( elementclicked.dataset.unformatted == element.parentNode.firstChild.dataset.unformatted){ //si mon jumeau
  //             element.dispatchEvent(new Event('mouseup')); //je clique sur lui
  //           }
  //         }
  //         return
  //       }
  //     }
  //
  //     //si ils sont tous à 1 //je les séléctionne tous
  //     for(const element of tab2){
  //       if( elementclicked.dataset.unformatted == element.parentNode.firstChild.dataset.unformatted){ //si mon jumeau
  //         element.dispatchEvent(new Event('mouseup'));
  //       }
  //     }
  // });

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
</script>