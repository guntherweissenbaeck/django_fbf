
function showBirdEditFields() {
    let statusField = document.getElementById("id_status");
    let statusText = statusField.options[statusField.selectedIndex].text;
    let aviaryField = document.getElementById("div_id_aviary");
    let sentToField = document.getElementById("div_id_sent_to");


    if (statusText == 'In Auswilderung') {
        aviaryField.hidden = false
    } else if (statusText == 'Übermittelt') {
        sentToField.hidden = false
    }
    else {
        aviaryField.hidden = true
        sentToField.hidden = true
    }
}


// Load function on windows load.
(showBirdEditFields)();

// Load function on change.
document.getElementById("id_status").addEventListener("change", (event) => {
    showBirdEditFields()
});
