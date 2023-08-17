var allDevices = []
let deviceFound = undefined;
let offset = [];
let newCircle = false;


class Device {
    constructor(x, y, radius){
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.colour = [255,100,100];
        this.links = [];
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
    allDevices.push(new Device(100, 100, 20))
    allDevices.push(new Device(200, 300, 20));
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
        allDevices.push(new Device(mouseX, mouseY, 20));
        newCircle = false;
    }
}