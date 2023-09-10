const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
    // Update the data in the visualisation
    updateData: (callback) => ipcRenderer.on("update-data", callback),

    // Request new devices, deprecated
    // getNewDevices: () => ipcRenderer.send("get-new-devices"),

    // Send update on progress
    sendRequestProgress: (data) =>
        ipcRenderer.on("send-request-progress", data),

    // Ask for update on progress
    checkRequestProgress: () => ipcRenderer.send("check-request-progress"),

    // Update ready button when data is ready to be retrieved
    isReady: (data) => ipcRenderer.on("is-ready", data),

    // Request to load a network in from file
    loadNetworkFromData: (data) =>
        ipcRenderer.send("load-network-from-data", data),

    processDataUpdate: (callback) => ipcRenderer.on("device-data", callback),

    // Request a list of saved networks
    requestNetworks: () => ipcRenderer.send("request-networks"),

    // Recieve a list of saved networks
    networkList: (data) => ipcRenderer.on("network-list", data),

    // Load a saved network
    loadNetwork: (filename) => ipcRenderer.send("load-network", filename),
    // Load the home page
    loadHome: () => ipcRenderer.send("load-home"),

    // Request a new network
    getNewNetwork: () => ipcRenderer.send("get-new-network"),

    requestRemoveNetwork: (data) =>
        ipcRenderer.send("request-network-delete", data),

    // Set a new network's name
    trySetNewNetworkName: (newName) =>
        ipcRenderer.invoke("set-new-network-name", newName),

    // Re set an existing network's name
    trySetNetworkName: (names) => ipcRenderer.invoke("set-network-name", names),
});
