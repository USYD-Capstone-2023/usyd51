let info_panel = document.getElementById('info_panel_container');

let back_button = document.getElementById('back_button');
back_button.onclick = () => {
    window.electronAPI.loadHome();
}

let close_button = document.getElementById('close_symbol');
close_button.onclick = () => {
    info_panel.style.display = 'none';
}

let settings_button = document.getElementById('settings_symbol');
settings_button.onclick = () => {
    info_panel.style.display = 'flex';
    updateSSID();
}

let con_name = document.getElementById('con_name');
window.electronAPI.onSSIDUpdate((event, value) => {
    con_name.innerText = value[0].ssid;
})