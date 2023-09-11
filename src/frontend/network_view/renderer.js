/* Input:
ports_list: list of port numbers as strings
tcp_list: list of strings of tcp status on the ports in the same order
udp_list: list of strings of udp status on the ports in the same order
*/
function fillPortTable(ports_list, tcp_list, udp_list) {
    let port_col = document.getElementById('port_numbers');
    let tcp_col = document.getElementById('tcp_status');
    let udp_col = document.getElementById('udp_status');

    port_col.innerHTML = '<span class="port-title">Port #</span>';
    tcp_col.innerHTML = '<span class="port-title">TCP</span>';
    udp_col.innerHTML = '<span class="port-title">UDP</span>';

    for (index = 0; index < ports_list.length; index++) {
        let new_element = document.createElement("span");
        new_element.className = 'port-row';
        new_element.innerText = ports_list[index];
        port_col.appendChild(new_element);

        new_element = document.createElement("span");
        new_element.className = 'port-row';
        new_element.innerText = tcp_list[index];
        tcp_col.appendChild(new_element);

        new_element = document.createElement("span");
        new_element.className = 'port-row';
        new_element.innerText = udp_list[index];
        udp_col.appendChild(new_element);
    }
}

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
settings_button.addEventListener("click", function () {
    if (currentLayout == "cose") {
        breadthLayout();
    } else {
        coseLayout();
    }
});

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
