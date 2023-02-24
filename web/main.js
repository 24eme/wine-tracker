//option selectionné est le filtre qui est dans l'url
document.addEventListener("DOMContentLoaded", function(event) {
  var href = new URL(window.location.href);
  if(!href.searchParams.get('filtre')){
    document.getElementById('filtre').value = "TOUT-TOUT";
    document.getElementById('filtre-contrats').value = "TOUT-TOUT"
  }
  else{
    document.getElementById('filtre').value = href.searchParams.get('filtre');
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



