let info_panel = document.getElementById("info_panel_container");

let back_button = document.getElementById("back_button");
back_button.onclick = () => {
    window.electronAPI.loadHome();
};

let close_button = document.getElementById("close_symbol");
close_button.onclick = () => {
    info_panel.style.display = "none";
};

let settings_button = document.getElementById("settings_symbol");
settings_button.onclick = () => {
};

let map_button = document.getElementById("map_button");
let list_button = document.getElementById("list_button");
let history_button = document.getElementById("history_button");

map_button.onclick = () => {
    map_button.className = "pill-selected pill-left pill-element";
    list_button.className = "pill-unselected pill-element";
    history_button.className = "pill-unselected pill-right pill-element";
    document.getElementById("cy").style.display = 'block';
};

list_button.onclick = () => {
    map_button.className = "pill-unselected pill-left pill-element";
    list_button.className = "pill-selected pill-element";
    history_button.className = "pill-unselected pill-right pill-element";
    document.getElementById("cy").style.display = 'none';
};
