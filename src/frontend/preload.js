const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  updateData: (callback) => ipcRenderer.on('update-data', callback),
  requestNetworks: () => ipcRenderer.send('request-networks'),
  networkList: (data) => ipcRenderer.on("network-list", data),
  loadNetwork: (filename) => ipcRenderer.send("load-network", filename)
})


window.addEventListener('DOMContentLoaded', () => {
    const replaceText = (selector, text) => {
      const element = document.getElementById(selector)
      if (element) element.innerText = text
    }
  
    for (const type of ['chrome', 'node', 'electron']) {
      replaceText(`${type}-version`, process.versions[type])
    }
  })