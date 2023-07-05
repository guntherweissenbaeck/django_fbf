
function showHideAviary() {
    let statusField = document.getElementById("id_status");
    let aviaryField = document.getElementById("div_id_aviary"); 
    let statusText = statusField.options[statusField.selectedIndex].text;

    if (statusText == 'In Auswilderung') {
        aviaryField.hidden = false
    } else {
        aviaryField.hidden = true
    }
}


// Load function on windows load.
(showHideAviary)();

// Load function on change.
document.getElementById("id_status").addEventListener("change", (event) => {
    showHideAviary()
});
