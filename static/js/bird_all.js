let sel = document.getElementById("id_status");
let text = sel.options[sel.selectedIndex].text;

if (text === 'In Auswilderung') {
    console.log("Yes");
}