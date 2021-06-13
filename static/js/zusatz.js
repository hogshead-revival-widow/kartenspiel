if (document.getElementById('egal')) {

  // wenn 'egal'-option geklickt ist, entklicke sie nach wahl einer anderen option
  var nicht_egal = document.querySelectorAll("input[type=checkbox][name^='zwei']")
  var egal = document.querySelector("input[type=checkbox][id='egal']")
  nicht_egal.forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
      if (checkbox.checked == true) {
        egal.checked = false
      }
    })
  });
  egal.addEventListener('change', function () {
    if (egal.checked == true) {
      nicht_egal.forEach(function (checkbox) {
        checkbox.checked = false
      })
    }
  });
}

// automatisch zur karte scrollen
if (document.getElementById('fokus')) {
  window.location.hash = '#fokus';
}

// kopiere in clipboard
function kopiere(zuKopieren) {
  zuKopieren.select();
  document.execCommand('copy');
};

// andere darstellung der karten
function karten_ansicht_aendern() {
  fetch('/ansichtsweise_aendern')
    .then(
      function (antwort) {
        if (antwort.status !== 200) {
          console.log('Fehler. Statuscode: ' + antwort.status);
          return;
        }
        // Geänderte Ansichtsweise übernehmen; wir refreshen der Einfachheit halber...
        location.reload();
      }
    )
    .catch(function (fehler) {
      console.log('Fetch-Fehler: ', fehler);
    });
};

// Wenn vorhanden, Toasts initalisieren
var toastsVorhanden = document.getElementsByClassName('toast');
if(toastsVorhanden){
  var toastsElemente = [].slice.call(toastsVorhanden)
  var toastListe = toastsElemente.map(function (toastElement) {
    return new bootstrap.Toast(toastElement)
  });
  toastListe.forEach(toast => toast.show()); // Toasts zeigen
};
