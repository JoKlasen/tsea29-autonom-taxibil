console.log("[STATUS] Initializing keyboard listeners...")

var keys = {
    "forward":0,
    "left":0,
    "back":0,
    "right":0
}

document.addEventListener('keydown', function(event) {
    if (event.repeat) { return; }
    
    if(event.keyCode == 87) {
        keys["forward"] = 1;
    }
    else if(event.keyCode == 65) {
        keys["left"] = 1;
    }
    else if(event.keyCode == 83) {
        keys["back"] = 1;
    }
    else if(event.keyCode == 68) {
        keys["right"] = 1;
    }

    //sendKeys()
});

document.addEventListener('keyup', function(event) {
    if(event.keyCode == 87) {
        keys["forward"] = 0;
    }
    else if(event.keyCode == 65) {
        keys["left"] = 0;
    }
    else if(event.keyCode == 83) {
        keys["back"] = 0;
    }
    else if(event.keyCode == 68) {
        keys["right"] = 0;
    }
    
    //sendKeys()
});

function updateKeyHighlighting() {
    document.getElementById("control-w").classList.remove("control-highlight")
    document.getElementById("control-a").classList.remove("control-highlight")
    document.getElementById("control-s").classList.remove("control-highlight")
    document.getElementById("control-d").classList.remove("control-highlight")

    if (keys["forward"] == 1) {
        document.getElementById("control-w").classList.add("control-highlight")
    }
    if (keys["left"] == 1) {
        document.getElementById("control-a").classList.add("control-highlight")
    }
    if (keys["back"] == 1) {
        document.getElementById("control-s").classList.add("control-highlight")
    }
    if (keys["right"] == 1) {
        document.getElementById("control-d").classList.add("control-highlight")
    }
}

function sendKeys() {
    updateKeyHighlighting()
    
    let tempkeys = structuredClone(keys);

    if (tempkeys["forward"] == 1 && tempkeys["back"] == 1)
    {
        tempkeys["forward"] = 0;
    }

    if (tempkeys["left"] == 1 && tempkeys["right"] == 1) {
        tempkeys["left"] == 0;
        tempkeys["right"] == 0;
    }

    sendMessage("keyspressed:" +
        "f=" + tempkeys["forward"].toString() +
        ":l=" + tempkeys["left"].toString() +
        ":b=" + tempkeys["back"].toString() +
        ":r=" + tempkeys["right"].toString() + ":"
    )
}

function keepSendingKeys() {
    sendKeys()

    setTimeout(keepSendingKeys, 100);
}

