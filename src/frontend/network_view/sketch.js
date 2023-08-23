var allDevices = []
let deviceFound = undefined;
let offset = [0, 0];
let circleOffset = [];
let newCircle = false;


// A sigmoid interpolation function to draw curved lines rather than linear ones.
function sigmoidInterp(x1, x2, t){ 
    let sigt = 1/(1+Math.pow(Math.E, 10*(t-0.5)));
    return x2+ sigt*(x1-x2)
}


class Device {
    constructor(x, y, radius, data, name=''){
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.colour = [255,100,100];
        this.data = data
        this.links = []
        this.linkLines = []
        this.name = name
        this.infoBox = Device.createInfoBox();
    }

     //Creates The popup infoBox to be used
     static createInfoBox() {
        if (document.getElementById('infoBox')){
            return;
        } 
        let infoBox = document.createElement('div');
        infoBox.id = 'infoBox';
        infoBox.classList.add('infoBox');
    
        let fields = ['IP', 'MAC Address', 'Parent'];
        for (let field of fields) {
            let p = document.createElement('p');
        
            let strong = document.createElement('strong');
            strong.textContent = field + ': ';
            p.appendChild(strong);

            let span = document.createElement('span');
            span.id = 'device' + field.replace(/\s+/g, ''); 
            p.appendChild(span);

            infoBox.appendChild(p);
            document.body.appendChild(infoBox);
        }
    }
     //Hides the infoBox
     static hideInfoBox() {
        let infoBox = document.getElementById('infoBox');
        if (infoBox) {
            infoBox.style.display = 'none';
        }
    }

    // Visualise the links with curved lines. Increase line segments for a potentially smoother look.
    addLink(device){
        this.links.push(device);
        let newLine = []
        let lineSegments = 10;
        for (let i = -1; i <= lineSegments+1; i++){
            newLine.push([lerp(this.x, device.x, i/lineSegments), sigmoidInterp(this.y, device.y, i/lineSegments)])
        }
        this.linkLines.push(newLine);
    }

    refreshLinks(){
        this.linkLines = [];
        for (let device of this.links){
            let newLine = [];
            let lineSegments = 10;
            for (let i = -1; i <= lineSegments+1; i++){
                newLine.push([lerp(this.x, device.x, i/lineSegments), sigmoidInterp(this.y, device.y, i/lineSegments)])
            }
            this.linkLines.push(newLine);
        }
        
    }

    draw(){
        if (this.hoverCheck()){
            // Don't show infoBox if you're trying to move circle
            if (!keyIsDown(SHIFT)){
                // remove unneccesary suffix
                let name = this.data.name.replace(".in-addr.arpa.", "");
                let parent = this.data.parent.replace(".in-addr.arpa.", "");

                let infoBox = document.getElementById('infoBox');
                document.getElementById('deviceIP').innerText = name || 'N/A';
                document.getElementById('deviceMACAddress').innerText = this.data.mac || 'N/A';
                // document.getElementById('deviceLayerLevel').innerText = this.data.layer_level || 'N/A';
                document.getElementById('deviceParent').innerText = parent || 'N/A';

                infoBox.style.display = 'block';
                infoBox.style.left = `${this.x + offset[0] + 10}px`;
                infoBox.style.top = `${this.y + offset[1] + 10}px`;
            }
            strokeWeight(2);
            stroke(0, 0, 255);
        } else {
            noStroke();
        }
        fill(this.colour);
        ellipse(this.x,this.y,this.radius*2,this.radius*2);
    }

    drawLinks(){
        noFill();
        for (let i = 0; i < this.linkLines.length; i++){
            stroke(100, 200, 200);
            beginShape();
            for (let j = 0; j < this.linkLines[i].length; j++){
                curveVertex(this.linkLines[i][j][0], this.linkLines[i][j][1]);
            }
            endShape();
            // line(this.x, this.y, this.links[i].x, this.links[i].y);
        }
    }

    hoverCheck(){

        // Detect whether the object is being hovered.
        if (Math.pow(rmouseX() - this.x, 2) + Math.pow(rmouseY() - this.y, 2) < this.radius*this.radius){
            return true;
        }
        return false

    }
}


// Get relative mouse positions when accounting for the translation.
function rmouseX(){
    return mouseX - offset[0];
}

function rmouseY(){
    return mouseY - offset[1];
}

function setup(){
    createCanvas(windowWidth, windowHeight);
    frameRate(60);
}


function draw(){
    background(100);
    Device.hideInfoBox();
    translate(offset[0], offset[1])
    for (device of allDevices){
        device.drawLinks();
    }
    for (device of allDevices){
        device.draw();
    }

}

function mouseDragged(){
    if (keyIsDown(SHIFT)){
        if (deviceFound == undefined){
            for (device of allDevices){
                if (Math.pow(rmouseX()-device.x, 2) + Math.pow(rmouseY()-device.y, 2) < Math.pow(device.radius, 2)){
                    deviceFound = device;
                    circleOffset = [rmouseX()-device.x, rmouseY()-device.y];
                    break;
                }
            }
        } else {
            deviceFound.x = rmouseX() - circleOffset[0];
            deviceFound.y = rmouseY() - circleOffset[1];
            deviceFound.refreshLinks();
        }
    } else {
        offset[0] += mouseX-pmouseX;
        offset[1] += mouseY-pmouseY;
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
    device_list.sort((a, b) => {
        let diff = data[a].layer_level - data[b].layer_level;
        if (diff != 0){
            return diff;
        }

        return data[a].parent.localeCompare(data[b].parent) // Sort by parent name instead if on the same layer.
    
    }) // Sort by layer level

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

    for (let device of device_list){
        levels_array[data[device].layer_level].push(device);
    }

    let horizontal_width = width/(total_levels+1); // Give even spacing on left and right.

    for (let layer = 0; layer < levels_array.length; layer++){
        let x_pos = horizontal_width*(layer+1);
        let height_difference = height/(levels_array[layer].length+1);
        for (let i = 0; i < levels_array[layer].length; i++){
            let y_pos = height_difference*(i+1);
            allDevices.push(new Device(x_pos, y_pos, 10, data[levels_array[layer][i]], data[levels_array[layer][i]].name))
        }
    }


    for (device of allDevices){
        if (device.data.layer_level %2 != 0){ 
            // Dodgy, only adds lines to even layers.
            // This also means only even layer nodes can move and have their lines connected. 
            // A better solution MUST be found. However we are doing the same thing in the backend.
            continue;
        }
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
    offset = [0,0]
})