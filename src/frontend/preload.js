const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld('electronAPI', {
  updateData: (callback) => ipcRenderer.on('update-data', callback),
  getNewDevices: () => ipcRenderer.send('get-new-devices'),
  sendRequestProgress: (data) => ipcRenderer.on('send-request-progress', data),
  checkRequestProgress: () => ipcRenderer.send('check-request-progress'),
  isReady: (data) => ipcRenderer.on('is-ready',data),
  loadNetworkFromData: (data) => ipcRenderer.send('load-network-from-data', data),
  onSSIDUpdate: (callback) => ipcRenderer.on('connection-update', callback),

  processDataUpdate: (callback) => ipcRenderer.on('device-data', callback),
  requestNetworks: () => ipcRenderer.send('request-networks'),
  networkList: (data) => ipcRenderer.on("network-list", data),
  loadNetwork: (filename) => ipcRenderer.send("load-network", filename),
  loadHome: () => ipcRenderer.send("load-home"),
});
