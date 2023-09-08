let editMode = false;

window.electronAPI.requestNetworks();

document.addEventListener("DOMContentLoaded", () => {
    // Add methods that can only happen when DOM is loaded in here.
    document.getElementById("new-network-button").onclick = () => {
        window.location.href = "../processing/processing.html";
    };

    //Handles the Drag and Drop functionality for the network list
    setTimeout(() => {
        const networkBoxes = document.querySelectorAll(".network-box");
        const networkContainer = document.querySelector(".network-container");

        networkBoxes.forEach((box) => {
            box.addEventListener("dragstart", () => {
                //adds a class flag for which element is being dragged
                setTimeout(() => {
                    box.classList.add("dragging");
                });
            });
            box.addEventListener("dragend", () =>
                box.classList.remove("dragging")
            );
        });

        const initContainer = (e) => {
            if (!editMode) {
                return;
            }

            e.preventDefault();
            //identifies the box being dragged
            const draggingBox = networkContainer.querySelector(".dragging");

            //identifies the other boxes
            const siblings = [
                ...networkContainer.querySelectorAll(
                    ".network-box:not(.dragging)"
                ),
            ];

            //finds the sibling that is being hovered over
            let nextSibling = siblings.find((sibling) => {
                return (
                    e.clientY <= sibling.offsetTop + sibling.offsetHeight / 2
                );
            });

            //adds the box in that spotxm
            networkContainer.insertBefore(draggingBox, nextSibling);
        };

        networkContainer.addEventListener("dragover", initContainer);
        //this is for the lost space between each box
        networkContainer.addEventListener("dragenter", (e) => {
            e.preventDefault();
        });
    }, 100);
});

// window.electronAPI.recieveDevices((_event, data) => {

// })

function createNetworkBox(filename, name, ssid) {
    let networkBoxWrapper = document.createElement("div");
    networkBoxWrapper.setAttribute("class", "network-box-wrapper");

    let removeButton = document.createElement("button");
    removeButton.setAttribute("class", "remove-button");
    networkBoxWrapper.appendChild(removeButton);
    removeButton.innerHTML = "-";

    let networkBox = document.createElement("button");
    networkBox.setAttribute("class", "network-box");
    networkBox.setAttribute("draggable", "true");
    networkBoxWrapper.appendChild(networkBox);

    let networkInfo = document.createElement("div");
    networkInfo.setAttribute("class", "network-info");
    networkBox.appendChild(networkInfo);

    let networkName = document.createElement("div");
    networkName.setAttribute("class", "network-name");
    networkName.innerText = name;
    networkInfo.appendChild(networkName);

    let networkType = document.createElement("div");
    networkType.setAttribute("class", "network-type");
    networkType.innerText = "SSID: " + ssid;
    networkInfo.appendChild(networkType);

    let arrowButton = document.createElement("div");
    arrowButton.setAttribute("class", "arrow-button");
    arrowButton.innerHTML = '<i class="fa fa-arrow-right"></i>';
    arrowButton.onclick = () => {
        // We want to request data from the backend and load the corresponding page.
        window.electronAPI.loadNetwork(filename);
    };

    removeButton.onclick = () => {
        window.electronAPI.requestRemoveNetwork(name);
    };

    networkBox.appendChild(arrowButton);

    document.querySelector(".network-container").appendChild(networkBoxWrapper);
}

function editModeToggle() {
    editMode = !editMode;

    // Set edit button to accurate colour
    let button = document.getElementById("edit-button");
    if (editMode) {
        button.style.backgroundColor = "#6bff70";
    } else {
        button.style.backgroundColor = "#eb4034";
    }

    // Show remove buttons
    let removeButtons = document.getElementsByClassName("remove-button");
    for (let i = 0; i < removeButtons.length; i++) {
        if (editMode) {
            removeButtons[i].style.display = "flex";
        } else {
            removeButtons[i].style.display = "none";
        }
    }

    return editMode;
}

window.electronAPI.networkList((_event, data) => {
    // Remove all existing wrappers. This is so the list is refreshed when a box is removed.
    let wrappers = document.getElementsByClassName("network-box-wrapper");
    while (wrappers.length != 0) {
        wrappers[0].parentNode.removeChild(wrappers[0]);
    }

    // Loop through all network ids and create a box for each network containing name and SSID.
    for (let network of Object.keys(data)) {
        createNetworkBox(
            data[network]["name"],
            data[network]["name"],
            data[network]["ssid"]
        );
    }
});
