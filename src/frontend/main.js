const { app, BrowserWindow, Menu, ipcMain } = require("electron");
const http = require("http");
const path = require("path");
const fs = require("fs");

function saveDataToFile(event, ping_data, traceroute_data) {
  console.log("Traceroute completed. Combining data and saving file.");

  let all_data = {};
  for (item of Object.keys(ping_data)) {
    all_data[item] = {}; // Add by mac address
    all_data[item]["mac"] = ping_data[item];
    all_data[item]["neighbours"] = []; //traceroute_data[item];
    all_data[item]["name"] = item;
    all_data[item]["layer_level"] = traceroute_data[item].length - 1;
    all_data[item]["parent"] =
      traceroute_data[item][traceroute_data[item].length - 1];
  }

  for (let traceroute of Object.values(traceroute_data)) {
    for (let i = 0; i < traceroute.length - 1; i += 1) {
      if (all_data[traceroute[i]] == undefined) {
        all_data[traceroute[i]] = {};
        all_data[traceroute[i]]["mac"] = "undefined";
        all_data[traceroute[i]]["neighbours"] = [];
        all_data[traceroute[i]]["name"] = traceroute[i];
        all_data[traceroute[i]]["layer_level"] = 0;
        all_data[traceroute[i]]["parent"] = "undefined";
      }
    }
  }

  for (let traceroute of Object.values(traceroute_data)) {
    for (let i = 0; i < traceroute.length - 1; i += 1) {
      all_data[traceroute[i]]["neighbours"].push(traceroute[i + 1]);
      all_data[traceroute[i + 1]]["parent"] = traceroute[i];
    }
  }

  let filename = (Math.random() + 1).toString(36).substring(10) + ".json"; // random filename
  fs.writeFileSync("../cache/" + filename, JSON.stringify(all_data));
  console.log("Saved to file");
  console.log("Updating index.json");

  let file = JSON.parse(fs.readFileSync("../cache/index.json")); // Add new file to index.json.
  file[filename] = { name: "New Network", ssid: "TestNetwork" };
  fs.writeFileSync("../cache/index.json", JSON.stringify(file));

  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  win.webContents.send('is-ready',all_data);


}

function loadNetworkFromData(event, data){
  console.log("Loading network tab from load network from data");
  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  win.loadFile('network_view/index.html');
    // Wait until dom has loaded to send data
  win.webContents.once('dom-ready', () => win.webContents.send('update-data', data));
}

function tracerouteDevices(event, ping_data) {
  let traceroute_data = undefined;

  console.log("IP's grabbed. Now performing a traceroute.");

  let url = "http://127.0.0.1:5000/traceroute/";
  if (Object.keys(ping_data).length == 0) {
    console.log("Nothing to traceroute");
    return;
  }
  for (let item of Object.keys(ping_data)) {
    url += item + ",";
  }

  url = url.slice(0, -1);

  http.get(url, (resp) => {
    let data = "";
    resp.on("data", (chunk) => {
      data += chunk;
    });

    resp.on("end", () => {
      traceroute_data = JSON.parse(data);
      saveDataToFile(event, ping_data, traceroute_data);
    });
  });
}

function getNewDevices(event, data) {
  // Use the data variable to control whether to grab a new device list or load one from a json, etc.
  // Also to determine what data to return (ips, mac's etc)

  let ping_sweep_data = undefined;
  console.log("Getting all local ips.");
  http.get("http://127.0.0.1:5000/devices", (resp) => {
    let data = "";

    resp.on("data", (chunk) => {
      data += chunk;
    });

    resp.on("end", () => {
      ping_sweep_data = JSON.parse(data);
      tracerouteDevices(event, ping_sweep_data);
    });
  });
}

<<<<<<< HEAD
=======

>>>>>>> main
// Gets the progress of the current request from the backend
function checkRequestProgress(event) {

  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  let url = "http://127.0.0.1:5000/request_progress"
  
  let response = undefined
  http.get(url, (resp) => {
    let data = '';
    resp.on('data', (chunk)=>{
      data+=chunk;
    })
    
    resp.on('end', ()=>{
      response = JSON.parse(data);  
      win.webContents.send("send-request-progress", response);
    })
  });
}


function createWindow () {
  const win = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  const menu = Menu.buildFromTemplate([
    {
      label: app.name,
      submenu: [
        {
          click: () => {
            let data = JSON.parse(fs.readFileSync("../backend/clients.json"));
            win.webContents.send("update-data", data);
          },
          label: "Update data",
        },
        {
          click: () => win.webContents.openDevTools(),
          label: "Developer Tools",
        },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);

  win.loadFile("home/home.html");
  // win.webContents.openDevTools(); // Uncomment to have dev tools open on startup.
}

function loadHome(event) {
  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  win.loadFile("home/home.html");
}

function loadNetwork(event, data) {
  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  win.loadFile("network_view/index.html");
  let networkData = JSON.parse(fs.readFileSync("../cache/" + data));
  // Wait until dom has loaded to send data
  win.webContents.once("dom-ready", () =>
    win.webContents.send("update-data", networkData)
  );
}

function sendNetworks(event, data) {
  const webContents = event.sender;
  const win = BrowserWindow.fromWebContents(webContents);
  let networkData = JSON.parse(fs.readFileSync("../cache/index.json")); // Load file data from index.json
  win.webContents.send("network-list", networkData);
}

app.whenReady().then(() => {
  ipcMain.on('load-network', loadNetwork);
  ipcMain.on('request-networks', sendNetworks);
  ipcMain.on('load-home', loadHome);
  ipcMain.on('get-new-devices', getNewDevices);
  ipcMain.on('load-network-from-data', loadNetworkFromData);
  ipcMain.on('check-request-progress', checkRequestProgress);
  createWindow()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  // if (process.platform !== 'darwin') {
  app.quit();
  // }
});
