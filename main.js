const port = 80;

const fs = require('fs');
const app = require('express')();
const http = require('http').createServer(app);
const io = require('socket.io')(http);

app.get('/', (req, res) => {
	res.sendFile(__dirname + '/web/index.html');
});

app.get('/socket.io.min.js', (req, res) => {
	res.sendFile(__dirname + '/web/socket.io.min.js');
});


app.get('/web.js', (req, res) => {
	res.sendFile(__dirname + '/web/web.js');
});

http.listen(port, () => {
	console.log('listening on *:'+port);
});


io.on('connection', (socket) => {
	console.log('a user connected');
	saveData();
	socket.on('disconnect', () => {
		console.log('user disconnected');
	});


	socket.on('getData', (stocks,callback) => {
		fs.readFile('weather.json', (err, data) => {
			if (err) {
				console.log("RACE CONDTION");
			}else{
				let sym = JSON.parse(data);
				callback(sym);
			}
		});
		// var back = new Object();
		// back.temp = 420;
		// back.pressure = "BIG";
		// back.uv = "COLD";
		// callback(back);
	});
});

function saveData(){
	var back = new Object();
	back.valid = false;
	back.temp = 60;
	back.pressure = 12;
	back.uv = 32;
	fs.writeFile('weather.json', JSON.stringify(back), err => {
	  if (err) {
	    console.error(err)
	    return
	  }
	});
}
