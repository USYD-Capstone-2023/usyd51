let currentLayout = "breadthfirst";

var cy = cytoscape({
    container: document.getElementById("cy"),

    elements: [],

    style: [
        {
            selector: "node",
            style: {
                "background-color": "#666",
            },
        },
        {
            selector: "node:selected",
            style: {
                "background-color": "blue",
            },
        },
        {
            selector: "edge",
            style: {
                width: 3,
                "line-color": "rgb(94, 254, 238)",
                "curve-style": "taxi",
                "taxi-direction": "vertical",
            },
        },
        {
            selector: "edge:selected",
            style: {
                "line-color": "blue",
                "z-index": 9999,
            },
        },
    ],

    layout: {
        name: "grid",
    },

    wheelSensitivity: 0.3,
});

function loadData(data) {
    let device_list = Object.keys(data);
    for (let device of device_list) {
        let info = data[device];
        let mac = device;
        let ip = info.ip;
        let parent = info.parent;
        let hostname = info.hostname;
        cy.add({
            group: "nodes",
            data: {
                id: ip,
                mac: mac,
                parentIP: parent,
                hostname: hostname,
            },
        });
    }
    let nodes = cy.nodes();
    for (let node of nodes) {
        let parent = cy.getElementById(node.data("parentIP"));
        if (parent.data("id")) {
            cy.add({
                group: "edges",
                data: {
                    source: parent.data("id"),
                    target: node.data("id"),
                },
            });
            parent.style("background-color", "orange");
            parent.data("isParent", true);
        }
    }
    breadthLayout();
}

function breadthLayout() {
    var layout = cy.layout({
        name: "breadthfirst",

        fit: true,
        padding: 20,
        componentSpacing: 60,
        nodeOverlap: 60,
    });
    cy.edges().style("curve-style", "taxi");
    layout.run();
    currentLayout = "breadthfirst";
}
function coseLayout() {
    var layout = cy.layout({
        name: "cose",

        fit: true,
        padding: 20,
        componentSpacing: 60,
        nodeOverlap: 60,
        nodeRepulsion: function (node) {
            return node.data("isParent") ? 80000 : 100000;
        },
        animate: false,
    });
    cy.edges().style("curve-style", "bezier");
    layout.run();
    currentLayout = "cose";
}

function updateInfoBox(nodeData) {
    //THIS NEEDS TO BE UPDATE WHEN WE HAVE THE PROPER JSONS
    document.getElementById("node_type").textContent = "Device";
    document.getElementById("node_hostname").textContent = nodeData.hostname;
    document.getElementById("node_IP").textContent = nodeData.id;
    document.getElementById("node_MAC").textContent = nodeData.mac;
}

cy.on("tap", "node", function (evt) {
    var clickedNode = evt.target;
    updateInfoBox(clickedNode.data());
});

document.getElementById("toggleStyle").addEventListener("click", function () {
    if (currentLayout == "cose") {
        breadthLayout();
    } else {
        coseLayout();
    }
});

window.electronAPI.updateData((_event, value) => {
    console.log("Attempting to visualise!");
    loadData(value);
});
