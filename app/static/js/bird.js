function showBirdEditFields() {
    let statusField = document.getElementById("id_status");
    if (!statusField) return; // Sicherheitscheck
    
    let statusText = statusField.options[statusField.selectedIndex].text;
    let aviaryField = document.getElementById("div_id_aviary");
    let sentToField = document.getElementById("div_id_sent_to");
    let releaseLocationField = document.getElementById("div_id_release_location");

    // Alle Felder erstmal verstecken
    if (aviaryField) aviaryField.style.display = 'none';
    if (sentToField) sentToField.style.display = 'none';
    if (releaseLocationField) releaseLocationField.style.display = 'none';

    // Je nach Status entsprechende Felder anzeigen
    if (statusText == 'In Auswilderung') {
        if (aviaryField) aviaryField.style.display = 'block';
    } else if (statusText == 'Übermittelt') {
        if (sentToField) sentToField.style.display = 'block';
    } else if (statusText == 'Ausgewildert') {
        if (releaseLocationField) releaseLocationField.style.display = 'block';
    }
    
    console.log(`Status: ${statusText}, Aviary visible: ${aviaryField ? aviaryField.style.display !== 'none' : 'not found'}, SentTo visible: ${sentToField ? sentToField.style.display !== 'none' : 'not found'}, ReleaseLocation visible: ${releaseLocationField ? releaseLocationField.style.display !== 'none' : 'not found'}`);
}

// DOM-bereit warten
document.addEventListener('DOMContentLoaded', function() {
    // Initialer Aufruf nach kurzer Verzögerung, damit das Form vollständig geladen ist
    setTimeout(function() {
        showBirdEditFields();
    }, 100);
    
    // Event listener für Status-Änderungen
    const statusField = document.getElementById("id_status");
    if (statusField) {
        statusField.addEventListener("change", function(event) {
            showBirdEditFields();
        });
    }
});
