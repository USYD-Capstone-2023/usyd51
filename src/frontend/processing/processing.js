const loadingBarWidth = 40;
// in millis
const progressPollingRate = 400;

document.addEventListener("DOMContentLoaded", () => { // Add methods that can only happen when DOM is loaded in here.
    
    const loadingBar = document.getElementById("bar-info");
    const barLabel = document.getElementById("bar-label");
    window.electronAPI.getNewDevices();
    console.log("getting Devices");

    let polling = true;
    
    window.electronAPI.isReady((_event, data) => {
        polling = false;
        loadingBar.style.width = 100 + "%";
        barLabel.innerHTML = "DONE!";

        let target = document.getElementById('ready-button');
        target.textContent = "Ready";
        target.classList.remove("not-ready");
        target.classList.add("ready");
        document.getElementById("loading-icon").style.display = "none";
        document.getElementById("create-network").innerText = "Finished Processing";
        target.onclick = () => {window.electronAPI.loadNetworkFromData(data)}
    });

    // Handles IPC with node, updates progress bar with info from backend
    window.electronAPI.sendRequestProgress((_event, data) => {

        if (data["flag"]) {

            let done = data["progress"];
            let total = data["total"];
            let percentage = (done / total) * 100;
            loadingBar.style.width = percentage + "%";
            barLabel.innerHTML = data["label"] + " (" + done + " / " + total + ")";
            
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

