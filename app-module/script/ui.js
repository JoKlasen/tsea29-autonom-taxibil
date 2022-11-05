var mode = 1; // 1 is manual, 0 is automatic

function switchMode() {
    mode++;
    if (mode == 2) {mode = 0}

    if (mode == 1) {
        document.getElementById("control-mode").innerHTML = "Manual"
        sendMessage("switchmode:mode=manual")
    }
    else {
        document.getElementById("control-mode").innerHTML = "Auto"
        sendMessage("switchmode:mode=auto")
    }
}

function sendPID() {
    let pidvalues = "sendpid" +
        ":p=" + document.getElementById("control-pid-p").value +
        ":i=" + document.getElementById("control-pid-i").value +
        ":d=" + document.getElementById("control-pid-d").value

    sendMessage(pidvalues)
}
