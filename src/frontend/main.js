const { app, BrowserWindow, Menu, ipcMain } = require("electron");
const { spawn } = require("child_process");
const http = require("http");
const path = require("path");
const fs = require("fs");
const winPlatforms = ["Win32", "Win64", "Windows", "WinCE"];
const winOS = winPlatforms.indexOf(process.platform);
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

function loadNetworkFromData(event, data) {
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

function getSSID() {
    return new Promise((resolve, reject) => {
        http.get("http://127.0.0.1:5000/ssid", (resp) => {
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

function renameNetwork(old_name, new_name) {
    return new Promise((resolve, reject) => {
        http.get(
            "http://127.0.0.1:5000/rename_network/" + old_name + "," + new_name,
            (resp) => {
                let data = "";

                resp.on("data", (chunk) => {
                    data += chunk;
                });

                resp.on("end", () => {
                    if (data == "success") {
                        resolve(true);
                    }
                    resolve(false);
                });

                resp.on("error", (err) => {
                    reject(err);
                });
            }
        );
    });
}

ipcMain.handle("set-new-network-name", async (event, arg) => {
    try {
        const SSID = await getSSID();
        const result = await renameNetwork(SSID, arg);
        return result;
    } catch (error) {
        console.log("Error");
        return false;
    }
});

ipcMain.handle("set-network-name", async (event, arg) => {
    try {
        const result = await renameNetwork(arg[0], arg[1]);
        return result;
    } catch (error) {
        console.log("Error");
        return false;
    }
});

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

function loadHome(event) {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    win.loadFile("home/home.html");
}

function loadNetwork(event, data) {
	const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    win.loadFile("network_view/index.html");
	http.get("http://127.0.0.1:5000/network/" + data, (resp) => {
        let data = "";
        resp.on("data", (chunk) => {
            data += chunk;
        });

        resp.on("end", () => {
            response = JSON.parse(data);
            win.webContents.send("network-list", response);
            win.webContents.once("dom-ready", () =>
                win.webContents.send("update-data", response)
            );
        });
    });
    // Wait until dom has loaded to send data
}

function sendNetworks(event) {
	const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
	
    http.get("http://127.0.0.1:5000/ssid", (resp) => {
        let data = "";
        resp.on("data", (chunk) => {
            data += chunk;
        });

        resp.on("end", () => {
            ssid = data;

            http.get("http://127.0.0.1:5000/network_names", (resp) => {
                let data = "";
                resp.on("data", (chunk) => {
                    data += chunk;
                });

                resp.on("end", () => {
                    response = {};
                    response["data"] = JSON.parse(data);
                    response["ssid"] = ssid;
                    win.webContents.send("network-list", response);
                });
            });
        });
    });
    // win.webContents.send("network-list", networkData);
}

function requestRemoveNetwork(event, data) {
    let url = "http://127.0.0.1:5000/delete_network/" + data;
    http.get(url, (resp) => {
        let data = "";
        resp.on("data", (chunk) => {
            data += chunk;
        });

        resp.on("end", () => {
            sendNetworks(event);
        });
    });
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
