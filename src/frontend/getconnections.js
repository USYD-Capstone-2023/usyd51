const si = require('systeminformation');

setInterval(async () => {
    process.send(await si.wifiConnections());
}, 3000);