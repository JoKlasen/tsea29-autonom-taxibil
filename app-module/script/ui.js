var mode = 1; // 1 is manual, 0 is automatic

function switchMode() {
    mode++;
    if (mode == 2) {mode = 0}

    if (mode == 1) {
        document.getElementById("control-mode").innerHTML = "Manual"
        sendMessage("switchmode:mode=1:")
    }
    else {
        document.getElementById("control-mode").innerHTML = "Auto"
        sendMessage("switchmode:mode=0:")
    }
}

function sendPID() {
    let pidvalues = "sendpid" +
        ":p=" + document.getElementById("control-pid-p").value +
        ":i=" + document.getElementById("control-pid-i").value +
        ":d=" + document.getElementById("control-pid-d").value

    sendMessage(pidvalues)
}
