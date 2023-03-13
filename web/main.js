//option selectionné est le filtre qui est dans l'url

document.addEventListener("DOMContentLoaded", function(event) {
  var url = window.location.href;
  var onglet = url.split('#').pop();
  var href = new URL(url);
  if(onglet == "drm" || onglet == "contrats"){
    document.getElementById("nav-"+onglet+"-tab").click()
  }

  if(!href.searchParams.get('filtre')){ //si pas de filtre dans l'url par defaut "TOUT-TOUT"
    href.searchParams.set('filtre',filtre.value);
    window.location = href;
  }
  else{

    let drmOptionNames = [...document.getElementById('filtre').options].map(o => o.value);

    if(drmOptionNames.includes(href.searchParams.get('filtre'))){
      document.getElementById('filtre').value = href.searchParams.get('filtre');
    }
    else{
      var onglets = document.getElementsByClassName("nav-link");
      for (var i = 0; i < onglets.length; i++) {
          onglets[i].addEventListener('click',function() {
            href.searchParams.set('filtre',"TOUT-TOUT");
            href.hash = "#"+this.dataset.onglet;
            window.location = href;
          });
      }
    }

    let contratsOptionNames = [...document.getElementById('filtre-contrat').options].map(o => o.value);

    if(contratsOptionNames.includes(href.searchParams.get('filtre'))){
      document.getElementById('filtre-contrat').value = href.searchParams.get('filtre');
    }

    else{
      var onglets = document.getElementsByClassName("nav-link");
      for (var i = 0; i < onglets.length; i++) {
          onglets[i].addEventListener('click',function() {
            href.searchParams.set('filtre',"TOUT-TOUT");
            href.hash = "#"+this.dataset.onglet;
            window.location = href;
          });
      }
    }
  }
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

function changeRadioValue(choix){
  document.getElementById(choix.dataset.toshow).classList.remove("d-none");
  document.getElementById(choix.dataset.toshow).classList.add("d-block");

  document.getElementById(choix.dataset.tohide).classList.remove("d-block");
  document.getElementById(choix.dataset.tohide).classList.add("d-none");
}