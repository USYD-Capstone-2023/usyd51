var cy = cytoscape({
    container: document.getElementById('cy'),
  
    elements: [
    ],
  
    style: [
    {
      selector: 'node',
      style: {
        'background-color': '#666',
      }
    },
    {
      selector: 'node:selected',
      style: {
        'background-color': 'blue'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 3,
        'line-color': 'rgb(94, 254, 238)',
        'curve-style': 'unbundled-bezier'
      }
    }
    ],

    layout: {
        name: 'grid',
    },

    wheelSensitivity : 0.3,
    
  });

  function loadData(data){
    let device_list = Object.keys(data)
    for (device of device_list){
        let info = data[device];
        let ip = info.name.replace(".in-addr.arpa.", "");
        let mac = info.mac;
        let parent = info.parent.replace(".in-addr.arpa.", "");
        let layer_level = info.layer_level;
        cy.add({
            group: 'nodes',
            data: { 
                id: ip,
                mac : mac,
                parentIP : parent,
                layer : layer_level
            },
        });
    }
    let nodes = cy.nodes();
    for (node of nodes){
        let parent = cy.getElementById(node.data('parentIP'));
        if (parent.data("id")){
            cy.add({
                group: 'edges',
                data: {
                    source : parent.data("id"),
                    target : node.data("id"),
                }
            }
            )
            parent.style('background-color', 'orange');
            parent.data('isParent', true );
        }
    }

    var layout = cy.layout({
      name: 'cose',
      
      fit: true,
      padding: 20,
      componentSpacing: 60,
      nodeOverlap: 60,
      nodeRepulsion: function( node ) {
        return node.data('isParent') ? 80000 : 100000;
    },
      animate: false
    });
    layout.run();
  }

// cy.on('tap', 'node', function(evt){
//     var node = evt.target;
//     if (node.isNode && node.isNode()) {
//         makeTippy(tgt, data.id + " (" + data.name + ")<br/>" + data.info);
//     }


// });

window.electronAPI.updateData((_event, value) => {
    console.log("Attempting to visualise!");
    loadData(value);
    
    offset = [0,0]
})