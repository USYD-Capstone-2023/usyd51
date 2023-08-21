const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  updateData: (callback) => ipcRenderer.on('update-data', callback),
  getDataUpdate: (request) => ipcRenderer.send('get-data-update', request),
  processDataUpdate: (callback) => ipcRenderer.on('device-data', callback)
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