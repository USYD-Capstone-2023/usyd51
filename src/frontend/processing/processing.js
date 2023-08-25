

document.addEventListener("DOMContentLoaded", () => { // Add methods that can only happen when DOM is loaded in here.
    window.electronAPI.getNewDevices();
    console.log("getting Devices");

    window.electronAPI.isReady((_event, data) => {
        console.log("Hit ready");
        let target = document.getElementById('ready-button');
        target.textContent = "Ready";
        target.classList.remove("not-ready");
        target.classList.add("ready");
        target.onclick = () => {window.electronAPI.loadNetworkFromData(data)}
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

