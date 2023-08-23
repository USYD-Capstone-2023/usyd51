const { app, BrowserWindow, Menu, ipcMain } = require('electron')
const http = require('http')
const path = require('path')
const fs = require('fs')

function handleDataUpdate(event, data){

  // Use the data variable to control whether to grab a new device list or load one from a json, etc.
  // Also to determine what data to return (ips, mac's etc)
  const webContents = event.sender;

  const win = BrowserWindow.fromWebContents(webContents);

  http.get("http://127.0.0.1:5000/devices", (resp) => {
    let data = '';
    
    resp.on('data', (chunk)=>{
      data+=chunk;
    })

    resp.on('end', ()=>{
      console.log(data);
      let output = JSON.parse(data);
      win.webContents.send("device-data", output)
    })
  });
  win.setTitle(data);
}

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

function loadHome(event) {
  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  win.loadFile('home/home.html');
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
  ipcMain.on('load-home', loadHome)
  ipcMain.on('get-data-update', handleDataUpdate)
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