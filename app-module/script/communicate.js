let webSocket = new WebSocket("ws://192.168.240.128:8765/")

let status_table = {
    "speed": 'N/A',
    "steering": 'N/A',
    "error": 'N/A'
}

function sendMessage(message) {
    webSocket.send(message)
}

function emergencyStop() {
    sendMessage("emergencystop:1")
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
        

/*
<tr>
    <th>Variable</th>
    <th>Value</th>
</tr>
<tr>
    <td>Speed</td>
    <td>100 m/s</td>
</tr>
<tr>
    <td>Steering</td>
    <td>-15%</td>
</tr>
<tr>
    <td>Error</td>
    <td>5.7%</td>
</tr>
*/
}

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
};

function setupApp() {
    console.log("[STATUS] Starting application...")
    updateTable()
    setupChart()
}

document.addEventListener("DOMContentLoaded", function() {
    setupApp()
    drawMap()
    keepSendingKeys()
});
