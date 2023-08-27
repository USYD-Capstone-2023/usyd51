

window.electronAPI.requestNetworks();

document.addEventListener("DOMContentLoaded", () => { // Add methods that can only happen when DOM is loaded in here.
    document.getElementById('new-network-button').onclick = () =>{
        window.location.href = "../processing/processing.html";
    }

    //Handles the Drag and Drop functionality for the network list
    setTimeout(() => {
        const networkBoxes = document.querySelectorAll(".network-box");
        const networkContainer = document.querySelector(".network-container");

        networkBoxes.forEach(box => {
            box.addEventListener("dragstart", () => {
                //adds a class flag for which element is being dragged
                setTimeout(()=> box.classList.add("dragging"));
            });
            box.addEventListener("dragend", () => box.classList.remove("dragging"));
        });

        const initContainer = (e) => {
            e.preventDefault();
            //identifies the box being dragged
            const draggingBox = networkContainer.querySelector(".dragging");

            //identifies the other boxes
            const siblings = [...networkContainer.querySelectorAll(".network-box:not(.dragging)")];

            //finds the sibling that is being hovered over
            let nextSibling = siblings.find(sibling => {
                return e.clientY <= sibling.offsetTop + sibling.offsetHeight/2;
            })
            
            //adds the box in that spot
            networkContainer.insertBefore(draggingBox, nextSibling);
        }   
    

    networkContainer.addEventListener("dragover", initContainer);
    //this is for the lost space between each box
    networkContainer.addEventListener("dragenter", e => e.preventDefault());
    }, 100);

})


// window.electronAPI.recieveDevices((_event, data) => {

// })


function createNetworkBox(filename, name, ssid){

    let networkBox = document.createElement('button');
    networkBox.setAttribute("class", "network-box");
    networkBox.setAttribute("draggable", "true");

    
    let networkInfo = document.createElement('div');
    networkInfo.setAttribute('class', 'network-info');
    networkBox.appendChild(networkInfo);

    let networkName = document.createElement('div');
    networkName.setAttribute('class', 'network-name');
    networkName.innerText = name;
    networkInfo.appendChild(networkName);

    let networkType = document.createElement('div');
    networkType.setAttribute('class', 'network-type');
    networkType.innerText = "SSID: " + ssid;
    networkInfo.appendChild(networkType);

    let arrowButton = document.createElement('div');
    arrowButton.setAttribute('class', 'arrow-button');
    arrowButton.innerText = '→';
    arrowButton.onclick = () => {
        // We want to request data from the backend and load the corresponding page.
        window.electronAPI.loadNetwork(filename);
    }
            
            
    networkBox.appendChild(arrowButton);


    document.querySelector(".network-container").appendChild(networkBox);
}




window.electronAPI.networkList((_event, data) => {
    for (let network of Object.keys(data)){
        createNetworkBox(network, data[network]["name"], data[network]['ssid']);
    }
});