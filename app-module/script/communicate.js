let webSocket = null; 

function connectToServers() {
    let ip = document.getElementById("ip-address-textarea").value
    webSocket = new WebSocket("ws://" + ip + ":8765/")

    let cam = document.getElementById("camera-iframe");
    //cam.src = "http://" + ip + ":8000/index.js"

    let ip_container = document.getElementById("ip-address-container");
    let ip_textarea = document.getElementById("ip-address-textarea");
    let ip_button = document.getElementById("ip-address-button");

    // hide ip_container, ip_textarea and ip_button
    ip_container.style.display = "none";
    ip_textarea.style.display = "none";
    ip_button.style.display = "none";

    
    webSocket.onmessage = (event) => {
        console.log("Rcvd: " + event.data);
    
        if (event.data.includes("telemetry:")) {
            let values = event.data.split(':')
            values.shift()
            //console.log(values)

            values.forEach(value => {
            //console.log(value)
                value = value.split("=")
            //console.log(value)

            //console.log(status_table)
                status_table[value[0]] = value[1]
            //console.log(status_table)
            });

            updateTable()

            addDataToGraph(status_table[1], status_table[2])
            //addDataToGraph(status_table["speed"], 0)
        
        }
    }

    webSocket.onopen = (event) => {
        console.log("[STATUS] Websocket connecting...")
        webSocket.send("[webapp]|Connected");

        console.log("Sending Keys")
        keepSendingKeys()
    };
}

let status_table = {
    "speed": 'N/A',
    "steering": 'N/A',
    "error": 'N/A'
}

function sendMessage(message) {
    webSocket.send(message)
}

function emergencyStop() {
    sendMessage("es:1:")
}

function updateTable() {

    let table = document.getElementById("telemetry-table")
    
    //console.log(table)
    
    table.innerHTML = "<tr>" + 
        "<th>Variable</th>" +
        "<th>Value</th>" +
        "</tr>" +
        "<tr>" +
        "<td>Speed</td>" +
        "<td>" + status_table["speed"] + "</td>" +
        "</tr>" +
        "<tr>" +
        "<td>Steering</td>" +
        "<td>" + status_table["steering"] + "</td>" +
        "</tr>" +
        "<tr>" +
        "<td>Error</td>" +
        "<td>" + status_table["error"] + "</td>"
        "</tr>"
}
/*
webSocket.onmessage = (event) => {
    console.log("Rcvd: " + event.data);
    
    if (event.data.includes("telemetry:")) {
        let values = event.data.split(':')
        values.shift()
        //console.log(values)

        values.forEach(value => {
            //console.log(value)
            value = value.split("=")
            //console.log(value)

            //console.log(status_table)
            status_table[value[0]] = value[1]
            //console.log(status_table)
        });

        updateTable()

        //addDataToGraph(status_table[1], status_table[2])
        addDataToGraph(status_table["speed"], 0)
    }
}

webSocket.onopen = (event) => {
    console.log("[STATUS] Websocket connecting...")
    webSocket.send("[webapp]|Connected");
};*/

function setupApp() {
    console.log("[STATUS] Starting application...")
    updateTable()
    setupChart()
    drawMap()
}

document.addEventListener("DOMContentLoaded", function() {
    setupApp()
});
