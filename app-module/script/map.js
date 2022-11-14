var canvas = null;
var ctx = null;
var height = null;
var width = null;

function updateMap(from, to) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawBaseMap()
    drawCar(from, to)
}

function drawMap() {
    canvas = document.getElementById('map-canvas');
    ctx = canvas.getContext('2d');

    height = canvas.getBoundingClientRect().height;
    width = canvas.getBoundingClientRect().width;

    drawBaseMap()
}

function drawBaseMap() {
    let course = new Path2D("" +
        "M 97.2 21.6 L 112.752 21.6 Q 143.856 21.6 128.304 43.2 T 128.304 86.4 T 97.8065 108.7776 L 34.992 108 A 21.6 15.552 90 0 1 34.992 21.6 L 97.2 21.6 M 66.096 21.6 L 66.096 108 M 66.9669 76.2264 L 79.9217 76.2264 M 66.3604 58.2552 L 51.4782 58.3675 M 38.2544 21.9284 L 38.2544 7.2353 M 102.3166 21.9284 L 102.3166 5.1782 M 103.3586 108.7776 L 103.4099 94.4752 M 37.9935 108.7776 L 38.0565 92.5711"
    + "");

    ctx.fillStyle = "gray"
    ctx.strokeStyle = "gray"

    ctx.scale(2,2);
    ctx.rotate(Math.PI/2)
    ctx.translate(5,-130)
    ctx.lineWidth = 4;
    ctx.stroke(course)

    ctx.resetTransform()

    ctx.font = '30px sans';
    ctx.fillText("A", 255, 97)
    ctx.fillText("B", 80, 97)
    ctx.fillText("C", 77, 227)
    ctx.fillText("D", 255, 225)
    ctx.fillText("E", 133, 108)
    ctx.fillText("F", 99, 198)

    ctx.font = '20px sans';
    ctx.fillText("1", 230, 150)
    ctx.fillText("2", 20, 150)
}
function drawCircle(cx, cy, r) {
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, 2 * Math.PI, false);
    ctx.fill();
    ctx.lineWidth = 5;
    ctx.stroke();
}
function drawCar(from, to) {
    ctx.fillStyle = "white";
    ctx.strokeStyle = "white";
    
    if ((from == 'A' && to == 'B') || (to == 'A' && from == 'B')) {
        drawCircle(130, 20, 8)
    }
    if ((from == 'A' && to == null) || (to == 'A' && from == null)) {
        drawCircle(217, 87, 8)
    }
    if ((from == 'A' && to == '1') || (to == 'A' && from == '1')) {
        drawCircle(217, 115, 8)
    }
    if ((from == '1' && to == null) || (to == '1' && from == null)) {
        drawCircle(217, 142, 8)
    }
    if ((from == '1' && to == 'D') || (to == '1' && from == 'D')) {
        drawCircle(217, 180, 8)
    }
    if ((from == 'D' && to == null) || (to == 'D' && from == null)) {
        drawCircle(217, 215, 8)
    }
    if ((from == 'D' && to == 'C') || (to == 'D' && from == 'C')) {
        drawCircle(130, 252, 8)
    }
    if ((from == 'C' && to == null) || (to == 'C' && from == null)) {
        drawCircle(43, 217, 8)
    }
    if ((from == 'C' && to == '2') || (to == 'C' && from == '2')) {
        drawCircle(43, 180, 8)
    }
    if ((from == '2' && to == null) || (to == '2' && from == null)) {
        drawCircle(43, 142, 8)
    }
    if ((from == '2' && to == 'F') || (to == '2' && from == 'F')) {
        drawCircle(75, 142, 8)
    }
    if ((from == 'F' && to == null) || (to == 'F' && from == null)) {
        drawCircle(107, 142, 8)
    }
    if ((from == 'F' && to == 'E') || (to == 'F' && from == 'E')) {
        drawCircle(125, 142, 8)
    }
    if ((from == 'E' && to == null) || (to == 'E' && from == null)) {
        drawCircle(144, 142, 8)
    }
    if ((from == '1' && to == 'E') || (to == '1' && from == 'E')) {
        drawCircle(180, 142, 8)
    }
    if ((from == '2' && to == 'B') || (to == '2' && from == 'B')) {
        drawCircle(43, 115, 8)
    }
    if ((from == 'B' && to == null) || (to == 'B' && from == null)) {
        drawCircle(43, 86, 8)
    }
}
