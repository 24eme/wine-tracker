//option selectionné est le filtre qui est dans l'url

document.addEventListener("DOMContentLoaded", function(event) {
  var url = new URL(window.location.href);
  var onglet = url.hash;
  var href = new URL(url.href);

  if(onglet == "#drm" || onglet == "#contrats"){
    document.getElementById("nav-"+onglet.replace('#', '')+"-tab").click()
  }

  (document.querySelectorAll('#nav-tab .nav-link') || []).forEach(function (nav) {
    const trigger = new bootstrap.Tab(nav)
    nav.addEventListener('click', function (e) {
      e.preventDefault()
      trigger.show()
      window.location.hash = nav.dataset.onglet

      const currentFilter = href.searchParams.get('filtre') || 'TOUT-TOUT'
      const select = document.getElementById('filtre-'+nav.dataset.onglet)

      if ([...select.options].map(o => o.value).includes(currentFilter) === false) {
        const redirectTo = new URL(window.location.href);
        redirectTo.searchParams.set('filtre', 'TOUT-TOUT')
        window.location = redirectTo
        return false;
      }
    })
  });
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
