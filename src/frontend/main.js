const { app, BrowserWindow, Menu, ipcMain } = require("electron");
const { spawn } = require("child_process");
const http = require("http");
const path = require("path");
const fs = require("fs");

let flaskProcess;

app.on("ready", () => {
    flaskProcess = spawn("sudo", ["flask", "run"], { cwd: "../backend/" });
    flaskProcess.stdout.on("data", (data) => {
        console.log(`Flask data: ${data}`);
    });
});

function loadNetworkFromData(event, data) {
    console.log("Loading network tab from load network from data");
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    win.loadFile("network_view/index.html");
    // Wait until dom has loaded to send data
    win.webContents.once("dom-ready", () =>
        win.webContents.send("update-data", data)
    );
}

function getNewMap(event, data) {
    // Load new network map from map_network
    let incoming_data = undefined;
    http.get("http://127.0.0.1:5000/map_network", (resp) => {
        let data = "";

        resp.on("data", (chunk) => {
            data += chunk;
        });

        resp.on("end", () => {
            incoming_data = JSON.parse(data);
            const webContents = event.sender;
            const win = BrowserWindow.fromWebContents(webContents);
            win.webContents.send("is-ready", incoming_data);
        });
    });
}

// Gets the progress of the current request from the backend
function checkRequestProgress(event) {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    let url = "http://127.0.0.1:5000/request_progress";

    let response = undefined;
    http.get(url, (resp) => {
        let data = "";
        resp.on("data", (chunk) => {
            data += chunk;
        });

        resp.on("end", () => {
            response = JSON.parse(data);
            win.webContents.send("send-request-progress", response);
        });
    });
}

function createWindow() {
    const win = new BrowserWindow({
        width: 1000,
        height: 800,
        minHeight: 500,
        minWidth: 500,
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
                        let data = JSON.parse(
                            fs.readFileSync("../backend/clients.json")
                        );
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
    // Load network from json.
    ipcMain.on("load-network", loadNetwork);

    // Send all saved networks.
    ipcMain.on("request-networks", sendNetworks);

    // Load the home page
    ipcMain.on("load-home", loadHome);

    // Loads network tab then sends data from obj
    ipcMain.on("load-network-from-data", loadNetworkFromData);

    // Checks the progress of the data loading
    ipcMain.on("check-request-progress", checkRequestProgress);

    // Requests a new network map
    ipcMain.on("get-new-network", getNewMap);

    createWindow();

    app.on("activate", () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on("window-all-closed", () => {
    // if (process.platform !== 'darwin') {
    flaskProcess.kill();
    app.quit();
    // }
});
