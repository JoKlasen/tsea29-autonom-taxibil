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

function sendPID() {
    let pidvalues = "sp" +
        ":p=" + document.getElementById("control-pid-p").value +
        ":i=" + document.getElementById("control-pid-i").value +
        ":d=" + document.getElementById("control-pid-d").value + ':'

    sendMessage(pidvalues)
}

function sendMission() {
    let mission = "mi" +
        ":s=" + document.getElementById("mi-s").value +
        ":p=" + document.getElementById("mi-p").value +
        ":e=" + document.getElementById("mi-e").value + ':'

    sendMessage(mission)
}
