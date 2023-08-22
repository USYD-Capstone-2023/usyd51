const { app, BrowserWindow, Menu, ipcMain } = require('electron')
const path = require('path')
const fs = require('fs')

function createWindow () {
  const win = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  const menu = Menu.buildFromTemplate([
    {
      label: app.name,
      submenu: [
        {
          click: () => {
            let data = JSON.parse(fs.readFileSync("../backend/clients.json"))
            win.webContents.send('update-data', data);
          },
          label: "Update data"
        },
        {
          click: () => win.webContents.openDevTools(),
          label: "Developer Tools"
        }
        
      ]
    }
  ])
  Menu.setApplicationMenu(menu);

  win.loadFile('home/home.html')
  // win.webContents.openDevTools(); // Uncomment to have dev tools open on startup.
}

function loadNetwork(event, data){
  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  win.loadFile('network_view/index.html');
  let networkData = JSON.parse(fs.readFileSync("../cache/" + data))
    // Wait until dom has loaded to send data
  win.webContents.once('dom-ready', () => win.webContents.send('update-data', networkData));
}


function sendNetworks(event, data){
  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  let networkData = JSON.parse(fs.readFileSync('../cache/index.json')) // Load file data from index.json
  win.webContents.send("network-list", networkData)
}

app.whenReady().then(() => {
  ipcMain.on('load-network', loadNetwork)
  ipcMain.on('request-networks', sendNetworks)

  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  // if (process.platform !== 'darwin') {
    app.quit()
  // }
})