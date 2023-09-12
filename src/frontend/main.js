const { app, BrowserWindow, Menu, ipcMain } = require("electron");
const { spawn } = require("child_process");
const http = require("http");
const path = require("path");
const fs = require("fs");
const winPlatforms = ["win32", "win64", "windows", "wince"];
const winOS = winPlatforms.indexOf(process.platform.toLowerCase()) != -1;
let flaskProcess;

app.on("ready", () => {
    if (winOS) {
        flaskProcess = spawn("flask", ["run"], { cwd: "..\\backend\\" });
    } else {
        flaskProcess = spawn("sudo", ["flask", "run"], { cwd: "../backend/" });
    }
    flaskProcess.stdout.on("data", (data) => {
        console.log(`Flask data: ${data}`);
    });
});

async function makeRequest(extender) {
    return new Promise((resolve, reject) => {
        http.get("http://127.0.0.1:5000/" + extender, (resp) => {
            let data = "";

            resp.on("data", (chunk) => {
                data += chunk;
            });

            resp.on("end", () => {
                resolve(data);
            });
            resp.on("error", (err) => {
                reject(err);
            });
        });
    });
}

// Load a network utilising the data given as an argument
function loadNetworkFromData(event, data) {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    win.loadFile("network_view/index.html");
    // Wait until dom has loaded to send data
    win.webContents.once("dom-ready", () =>
        win.webContents.send("update-data", data)
    );
}

// Generate a new network
function getNewMap(event, data) {
    // Load new network map from map_network
    let incoming_data = undefined;
    makeRequest("map_network")
        .then((data) => {
            incoming_data = JSON.parse(data);
            const webContents = event.sender;
            const win = BrowserWindow.fromWebContents(webContents);
            win.webContents.send("is-ready", incoming_data);
        })
        .catch((err) => {
            console.log("Error: " + err);
        });
}

// Retrieve SSID
function getSSID() {
    return makeRequest("ssid");
}

// Rename network (returns true on success and false on failure)
function renameNetwork(old_name, new_name) {
    const result = makeRequest(
        "rename_network/" + old_name + "," + new_name
    ).then((data) => {
        return data == "success";
    });
    return result;
}

// Handle setting a new network name
ipcMain.handle("set-new-network-name", async (event, arg) => {
    try {
        const SSID = await getSSID();
        const result = renameNetwork(SSID, arg);
        return result;
    } catch (error) {
        console.log("Error");
        return false;
    }
});

// Handle changing an existing network's name
ipcMain.handle("set-network-name", async (event, arg) => {
    try {
        const result = renameNetwork(arg[0], arg[1]);
        return result;
    } catch (error) {
        console.log("Error");
        return false;
    }
});

ipcMain.handle("get-ssid", async (event, arg) => {
    const result = await getSSID().then((ssid) => ssid);
    return result;
});

// Gets the progress of the current request from the backend
function checkRequestProgress(event) {
    makeRequest("request_progress").then((data) => {
        const webContents = event.sender;
        const win = BrowserWindow.fromWebContents(webContents);
        response = JSON.parse(data);
        win.webContents.send("send-request-progress", response);
    });
}

// Load the home page (and request network list)
function loadHome(event) {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    win.loadFile("home/home.html");
}

// Load a network by name
function loadNetwork(event, data) {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    win.loadFile("network_view/index.html");
    makeRequest("network/" + data).then((network_data) => {
        response = JSON.parse(network_data);

        // Wait until dom has loaded to send data
        win.webContents.once("dom-ready", () =>
            win.webContents.send("update-data", response)
        );
    });
}

// Send a list of networks to the home page (along with ssid)
function sendNetworks(event) {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);

    makeRequest("network_names").then((names_data) => {
        response = {};
        response["data"] = JSON.parse(names_data);
        win.webContents.send("network-list", response);
    });
}

// Make a request to remove an existing network
function requestRemoveNetwork(event, data) {
    makeRequest("delete_network/" + data).then((data) => {
        sendNetworks(event);
    });
}

// Generates the window
function createWindow() {
    const win = new BrowserWindow({
        width: 1000,
        height: 800,
        minHeight: 500,
        minWidth: 500,
        webPreferences: {
            contextIsolation: true,
            preload: path.join(__dirname, "preload.js"),
        },
    });

    const menu = Menu.buildFromTemplate([
        {
            label: app.name,
            submenu: [
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

    // Request a network be deleted
    ipcMain.on("request-network-delete", requestRemoveNetwork);

    createWindow();

    app.on("activate", () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on("window-all-closed", () => {
    flaskProcess.kill();
    app.quit();
});
