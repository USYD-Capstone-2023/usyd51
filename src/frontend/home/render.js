

window.electronAPI.requestNetworks();

document.addEventListener("DOMContentLoaded", () => { // Add methods that can only happen when DOM is loaded in here.
    document.getElementById('new-network-button').onclick = () =>{
        //window.electronAPI.getNewDevices();

        //document.getElementById("processing-network").style.display = "Inherit";
        document.getElementById("create-network").innerText = "Processing...";
        document.getElementById("create-network-plus").style.display = "none";
        document.getElementById("create-network-loading").style.display = "inherit";

    }
})


// window.electronAPI.recieveDevices((_event, data) => {

// })

function createNetworkBox(filename, name, ssid){
    let networkBox = document.createElement('button');
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
    arrowButton.onclick = () => {
        // We want to request data from the backend and load the corresponding page.
        window.electronAPI.loadNetwork(filename);
    }
            
            
    networkBox.appendChild(arrowButton);


    document.body.appendChild(networkBox);
}




window.electronAPI.networkList((_event, data) => {
    for (let network of Object.keys(data)){
        createNetworkBox(network, data[network]["name"], data[network]['ssid']);
    }
})