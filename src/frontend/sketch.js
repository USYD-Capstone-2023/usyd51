
var allDevices = []
let deviceFound = undefined;
let offset = [];
let newCircle = false;



class Device {
    constructor(x, y, radius, data, name=''){
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.colour = [255,100,100];
        this.data = data
        this.links = []
        this.name = name
    }

    addLink(device){
        this.links.push(device);
    }

    draw(){
        noStroke();
        fill(this.colour);
        ellipse(this.x,this.y,this.radius,this.radius);
    }

    drawLinks(){
        for (let i = 0; i < this.links.length; i++){
            stroke(100, 200, 200);
            line(this.x, this.y, this.links[i].x, this.links[i].y);
        }
    }
}

function setup(){
    createCanvas(windowWidth, windowHeight);
    allDevices.push(new Device(100, 100, 20,{}))
    allDevices.push(new Device(200, 300, 20,{}));
    allDevices[0].addLink(allDevices[1]);
}


function draw(){
    background(100);
    for (device of allDevices){
        device.drawLinks();
    }
    for (device of allDevices){
        device.draw();
    }

}

function mouseDragged(){
    if (deviceFound == undefined){
        for (device of allDevices){
            if (Math.pow(mouseX-device.x, 2) + Math.pow(mouseY-device.y, 2) < Math.pow(device.radius, 2)){
                deviceFound = device;
                offset = [mouseX-device.x, mouseY-device.y];
                break;
            }
        }
    } else {
        deviceFound.x = mouseX - offset[0];
        deviceFound.y = mouseY - offset[1];
    } 
}

function mouseReleased(){
    deviceFound = undefined;
}

function keyPressed(){
    if (keyCode == 78){
        newCircle = true;
    }
}

function mouseClicked(){
    if (newCircle){
        allDevices.push(new Device(mouseX, mouseY, 20,{}));
        newCircle = false;
    }
}


function loadData(data){
    allDevices = [];

    let device_list = Object.keys(data)
    device_list.sort((a, b) => data[a].layer_level - data[b].layer_level) // Sort by layer level

    let total_levels = -1;
    for (device of device_list){
        if (data[device].layer_level > total_levels){
            total_levels = data[device].layer_level
        }
    }
    total_levels++; // Account for router being 0, not 1.
    if (total_levels == 0){
        console.log("Invalid data, cannot load.");
        return;
    }

    // Map all nodes into their levels
    
    let levels_array = []
    for (let i = 0; i < total_levels; i++){
        levels_array.push([])
    }

    for (device of device_list){
        levels_array[data[device].layer_level].push(device);
    }

    let horizontal_width = width/(total_levels+1); // Give even spacing on left and right.

    for (let layer = 0; layer < levels_array.length; layer++){
        let x_pos = horizontal_width*(layer+1);
        console.log("Width: ", horizontal_width, "Layer+1: ", layer+1)
        let height_difference = height/(levels_array[layer].length+1);
        console.log("Height: ", height_difference)
        for (let i = 0; i < levels_array[layer].length; i++){
            let y_pos = height_difference*(i+1);
            allDevices.push(new Device(x_pos, y_pos, 10, data[levels_array[layer][i]], data[levels_array[layer][i]].name))
            console.log(x_pos, y_pos)
        }
    }



    // for (device in data){
    //     allDevices.push(new Device(random()*width, random()*height, 10, data[device], data[device].name))
    // }


    for (device of allDevices){
        console.log(device)
        for (link of device.data.neighbours){
            for (other_device of allDevices){
                if (other_device.name == link){
                    device.addLink(other_device);
                    break;
                }
            }
        }
    }
}

window.electronAPI.updateData((_event, value) => {
    console.log("Attempting to visualise!");
    loadData(value);
})