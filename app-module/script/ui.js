var mode = 1; // 1 is manual, 0 is automatic

function switchMode() {
    mode++;
    if (mode == 2) {mode = 0}

    if (mode == 1) {
        document.getElementById("control-mode").innerHTML = "Manual"
        sendMessage("sm:m=1:")
    }
    else {
        document.getElementById("control-mode").innerHTML = "Auto"
        sendMessage("sm:m=0:")
    }
}
var detection = 1;
function switchDetection() {
    detection++;
    if (detection == 2) {detection = 0}

    if (detection == 1) {
        document.getElementById("toggle-detection-text").innerHTML = "Detect<br>On"
        sendMessage("td:d=1:")
    }
    else {
        document.getElementById("toggle-detection-text").innerHTML = "Detect<br>Off"
        sendMessage("td:d=0:")
    }
}

function sendPID() {
    let pidvalues = "stp" +
        ":p=" + document.getElementById("control-pid-p").value +
        ":i=" + document.getElementById("control-pid-i").value +
        ":d=" + document.getElementById("control-pid-d").value + ':'

    sendMessage(pidvalues)

    pidvalues = "spp" +
        ":p=" + document.getElementById("control-pid-ps").value +
        ":i=" + document.getElementById("control-pid-is").value +
        ":d=" + document.getElementById("control-pid-ds").value + ':'

    sendMessage(pidvalues)

}

function sendMission() {
    let mission = "mi" +
        ":s=" + document.getElementById("mi-s").value +
        ":p=" + document.getElementById("mi-p").value +
        ":e=" + document.getElementById("mi-e").value + ':'

    console.log(mission)
    sendMessage(mission)
}
