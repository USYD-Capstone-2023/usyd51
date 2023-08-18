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

  win.loadFile('index.html')
  // win.webContents.openDevTools(); // Uncomment to have dev tools open on startup.

}

app.whenReady().then(() => {
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