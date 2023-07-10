function showHideFindCircumstancesNew() {
    let circField = document.getElementById("id_find_circumstances");
    let circFieldNew = document.getElementById("id_find_circumstances_new");
    let circText = circField.options[circField.selectedIndex].text;

    if (circText == 'Neu') {
        circFieldNew.type = "show"
    } else {
        circFieldNew.type = "hidden"
    }
}

(showHideFindCircumstancesNew)();

document.getElementById("id_find_circumstances").addEventListener("change", (event) => {
    showHideFindCircumstancesNew()
});