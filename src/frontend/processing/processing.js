// in millis
const progressPollingRate = 400;

const loadingBarTotalSteps = 3;

const getLoadingBarWidth = (stepNumber, currentProgress) => {
    console.log(currentProgress);
    return 100 * ((currentProgress + stepNumber) / loadingBarTotalSteps);
};

document.addEventListener("DOMContentLoaded", () => {
    // Add methods that can only happen when DOM is loaded in here.

    const loadingBar = document.getElementById("bar-info");
    const barLabel = document.getElementById("bar-label");
    window.electronAPI.getNewNetwork();
    console.log("getting Devices");

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
            window.electronAPI.loadNetworkFromData(data);
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
