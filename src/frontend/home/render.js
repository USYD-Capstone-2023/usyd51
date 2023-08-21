

window.electronAPI.requestNetworks();

function createNetworkBox(name, ssid){
    let networkBox = document.createElement('div');
    networkBox.setAttribute("class", "network-box");
    
    let networkInfo = document.createElement('div');
    networkInfo.setAttribute('class', 'network-info');
    networkBox.appendChild(networkInfo);

    let networkName = document.createElement('div');
    networkName.setAttribute('class', 'network-name');
    networkName.innerText = name;
    networkInfo.appendChild(networkName);

    let networkType = document.createElement('div');
    networkType.setAttribute('class', 'network-type');
    networkType.innerText = "SSID: "+ssid;
    networkInfo.appendChild(networkType);

    let arrowButton = document.createElement('div');
    arrowButton.setAttribute('class', 'arrow-button');
    arrowButton.innerText = '→';
    networkBox.appendChild(arrowButton);


    document.body.appendChild(networkBox);
}


window.electronAPI.networkList((_event, data) => {
    for (let network of Object.values(data)){
        console.log(network)
        createNetworkBox(network["name"], network['ssid']);
    }
    console.log('h')
})