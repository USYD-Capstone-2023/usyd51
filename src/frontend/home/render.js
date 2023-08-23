

window.electronAPI.requestNetworks();

function createNetworkBox(filename, name, ssid){
    // let networkContainer = document.createElement('div');
    // networkContainer.setAttribute("class", "networkContainer");

    let networkBox = document.createElement('button');
    networkBox.setAttribute("class", "network-box");
    // networkBox.appendChild(networkContainer);
    
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
    arrowButton.onclick = () => {
        // We want to request data from the backend and load the corresponding page.
        window.electronAPI.loadNetwork(filename);
    }
            
            
    networkBox.appendChild(arrowButton);


    document.body.appendChild(networkBox);
}


window.electronAPI.networkList((_event, data) => {
    for (let network of Object.keys(data)){
        console.log(network)
        createNetworkBox(network, data[network]["name"], data[network]['ssid']);
    }
})