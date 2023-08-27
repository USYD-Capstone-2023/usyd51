const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  updateData: (callback) => ipcRenderer.on("update-data", callback),
  getNewDevices: () => ipcRenderer.send("get-new-devices"),

  processDataUpdate: (callback) => ipcRenderer.on("device-data", callback),
  requestNetworks: () => ipcRenderer.send("request-networks"),
  networkList: (data) => ipcRenderer.on("network-list", data),
  loadNetwork: (filename) => ipcRenderer.send("load-network", filename),
  loadHome: () => ipcRenderer.send("load-home"),
});
