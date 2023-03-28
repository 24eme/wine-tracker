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
  if (toggle = e.target.closest('.legendtoggle')) {
    const filter = [...toggle.parentNode.children].filter((child) => child.matches('.legendtext')).map(o => o.dataset.unformatted)
    const block_parent = toggle.closest('.graph-container')

    if (filter === null || block_parent === null) {
      return false
    }

    const row = block_parent.closest('.graphs-container')
    const graphs = [...row.children].filter((child) => (child !== block_parent && child.matches('.graph-container')))

    for (const graph of graphs) {
      const toSwitch = graph.querySelector('.legendtext[data-unformatted="'+filter+'"] ~ .legendtoggle')
      toSwitch.dispatchEvent(new Event('mouseup'));
    }
  }
});

function changeRadioValue(choix){
  document.getElementById(choix.dataset.toshow).classList.remove("d-none");
  document.getElementById(choix.dataset.toshow).classList.add("d-block");

  document.getElementById(choix.dataset.tohide).classList.remove("d-block");
  document.getElementById(choix.dataset.tohide).classList.add("d-none");
}
