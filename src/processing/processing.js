// in millis
const progressPollingRate = 400;

const loadingBarTotalSteps = 3;

let newNetworkDefaultName;


const getLoadingBarWidth = (stepNumber, currentProgress) => {
    return 100 * ((currentProgress + stepNumber) / loadingBarTotalSteps);
};

document.addEventListener("DOMContentLoaded", () => {
    // Add methods that can only happen when DOM is loaded in here.

    window.electronAPI.getSSID().then((ssid) => {
        document.getElementById("current-network").innerHTML = ssid;
    });

    const loadingBar = document.getElementById("bar-info");
    const barLabel = document.getElementById("bar-label");
    window.electronAPI.getNewNetwork();

    let polling = true;

    window.electronAPI.isReady((_event, data) => {
        polling = false;
        loadingBar.style.width = 100 + "%";
        barLabel.innerHTML = "DONE!";
        loadingBar.style.borderRadius = "5px";

        let target = document.getElementById("ready-button");
        target.textContent = "Ready";
        target.classList.remove("not-ready");
        target.classList.add("ready");
        document.getElementById("loading-icon").style.display = "none";
        document.getElementById("create-network").innerText =
            "Finished Processing";
        target.onclick = () => {
            let new_name = document.getElementById("input-name").value;
            if (new_name == "") {
                window.electronAPI.loadNetworkFromData(data);
            } else {
                // If user has set a name then check if the network name is valid
                // If it is then load data and set name, otherwise set text colour to red.
                const result = window.electronAPI
                    .trySetNewNetworkName(new_name)
                    .then((res) => {
                        if (res) {
                            window.electronAPI.loadNetworkFromData(data);
                        } else {
                            document.getElementById(
                                "input-description"
                            ).style.color = "red";
                        }
                    });
            }

            // window.electronAPI.loadNetworkFromData(data);
        }; // I believe this can be done without a IPC call.
    });

    // Handles IPC with node, updates progress bar with info from backend
    let currentLabel = undefined;
    let stepNumber = 0;
    window.electronAPI.sendRequestProgress((_event, data) => {
        if (data["flag"]) {
            if (currentLabel == undefined) {
                currentLabel = data["label"];
            } else if (currentLabel != data["label"]) {
                currentLabel = data["label"];
                stepNumber++;
            }
            let done = data["progress"];
            let total = data["total"];
            let percentage = getLoadingBarWidth(stepNumber, done / total);
            loadingBar.style.width = percentage + "%";
            barLabel.innerHTML =
                data["label"] + " (" + done + " / " + total + ")";
        } else {
            if (polling) {
                barLabel.innerHTML = "Initialising...";
            }
        }
    });

    async function pollProgress() {
        window.electronAPI.checkRequestProgress();
        if (polling) {
            setTimeout(pollProgress, progressPollingRate);
        }
    }

    pollProgress();

    document.getElementById("settings-Form").addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent the default form submission
    
        // Get the input value
        var ports = document.getElementById("ports").value;
    
        // Create a JSON object with the data
        var data = {
            "ports": ports
        };
    
        window.electronAPI.sendSavedSettings(data);
    });
});

// function ready(event){
//     let text = event.target.textContent;
//     if (text === "Ready"){
//         window.location.href = "../home/home.html";
//     } else {
//         event.target.textContent = "Ready";
//         event.target.classList.remove("not-ready");
//         event.target.classList.add("ready");
//     }
// }

//add a function that recieves feedback from the backend and do this. once done, get rid of the else in the ready function. and change the href location to wherever the network modules is
//event.target.textContent = "Ready";
//event.target.classList.remove("not-ready");
//event.target.classList.add("ready");
