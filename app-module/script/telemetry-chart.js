var previousSpeed = [
    
]
var log_error = []
var log_steering = []

var telemetryChart;
function setupChart() {
    const ctx = document.getElementById('telemetry-chart').getContext('2d');
    telemetryChart = new Chart(ctx, {
	    type: 'line',
        options: {
            responsive: true,
            scales: {
                y: {
                    grid: {
                        color: "gray",
                        color: (context) => {
                            if (context.tick.$context.tick.value === 0) {
                                return '#DDDDDD'
                            }
                            else {
                                return 'gray'
                            }
                        }
                    },
                }
            }
        },
	    data: {
		    labels: 0,
		    datasets: [
			    {
				    label: 'Error',
                    fill: false,
                    borderColor: "#AA0000",
                    pointBackgroundColor: "#FFFFFF",
                    pointBorderColor: "#55bae7",
                    pointHoverBackgroundColor: "#54bae7",
                    pointHoverBorderColor: "#55bae7",
                    data: []
			    },
                {
                    label: 'Steering',
                    fill: false,
                    borderColor: "#00AA00",
                    pointBackgroundColor: "#FFFFFF",
                    pointBorderColor: "#55bae7",
                    pointHoverBackgroundColor: "#54bae7",
                    pointHoverBorderColor: "#55bae7",
                    data: []
                },
		    ],
	    },
    })
}

var timer_started = false
var initial_time = null
var logging_paused = false
function addDataToGraph(steering, error) {
    if (logging_paused) {
        return;
    }

    if (!timer_started) {
        initial_time = performance.now()
        timer_started = true;
    }

    let currentTime = performance.now()-initial_time
    currentTime = currentTime.toFixed(2);
    log_steering.push({
        time: currentTime,
        value: steering
    })
    log_error.push({
        time: currentTime,
        value: steering
    })

    telemetryChart.data.labels.push(currentTime);
    telemetryChart.data.datasets[0].data.push(steering)
    telemetryChart.data.datasets[1].data.push(error)
    
    //console.log("Labels: ")
    //console.log(telemetryChart.data.labels)

    telemetryChart.update()
}

function downloadChartData() {
    var row_width = 40;

    var content = "";
    
    content += "time,steering,error,\n"

    for (var i = 0; i < log_steering.length; i++) {
        content += log_steering[i].time + ",";
        content += log_steering[i].value + ",";
        //content += log_error[i].time + ",";
        content += log_error[i].value + ",";
        content += "\n";
    }

    let uri = "data:application/octet-stream," + encodeURIComponent(content);

    location.href = uri;
}

function resetTelemetryChart() {
    timer_started = false
    initial_time = null

    for (let c = 0; c < 10000; c++) {
        telemetryChart.data.labels.pop();
        telemetryChart.data.datasets.forEach((dataset) => {
            dataset.data.pop();
        });
    }
    
    log_steering = []
    log_error = []

    telemetryChart.update();
}

function toggleLogging() {
    logging_paused = !logging_paused
    
    var logging_button = document.getElementById("buttons-logging-button")
    if (logging_paused) {
        logging_button.innerHTML = "Toggle<br>Logging<br>Disabled"
    }
    else {
        logging_button.innerHTML = "Toggle<br>Logging<br>Enabled"
    }
}
