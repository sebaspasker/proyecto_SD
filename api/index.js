const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const express = require('express');
const fs = require('fs');
const https = require('https');
const session = require('express-session');
const multer = require('multer');
const path = require('path');

const upload = multer();

const api = express();
port = 8080;

api.engine('html', require('ejs').renderFile)
api.set('port', (process.env.PORT || 8080))
api.use(cookieParser());
api.use(bodyParser.json());
api.use(bodyParser.urlencoded({extended : true }));
api.use(upload.array())
api.use(express.json())
api.use(express.urlencoded({extended : true}))
api.use(express.static(path.join(__dirname, './views/')))
api.set('views', path.join(__dirname, './views'))
api.set('view engine', 'ejs')
api.use(session({
	secret: 'secret',
	resave: true,
	saveUninitialized: true
}))

// Require the Router we defined in registry.js
var registry = require('./registry.js')
var map_api = require('./map.js')

// Use the router we defined in registry.js
api.use('/registry', registry)

api.use('/map', map_api)


api.get('/login', (req, res) => {
	res.sendFile(path.join(__dirname, './views/html/login.html'))
})

// Use the router we defined in registry.js
api.get('/', (req,res) => {
	res.send("Inicio.")
})


const request = require('request');
const md5 = require('md5');

api.post('/login', (req, res) =>{
	var username = req.body.username;
	var password = req.body.password;

	if(username && password) {
		request(`http://127.0.0.1:8080/registry/${username}`, (err, res1, body) => {
			if(!err) {
				var json = JSON.parse(body);
				var hash = md5(password)
				if(json.pass == hash) {
					req.session.loggedin = true;
					req.session.username = username;
					res.status(200)
					// TODO Error
					res.redirect('/game');
					return;
				}
			} else {
				console.log("ERRO");
				console.log(`${err}`);
				return;
			}
		})
	} else {
		console.log("Error");
		return;
	}
})

api.get('/game', (req,res) => {
	res.render(path.join(__dirname, './views/html/game.html'), {name:'name'})
	if(req.session.loggedin == true && req.session.username) {

		return;
	} else {
		// res.status(400)
		return;
	}
})

// api.listen(port, () => {
// 	console.log("Servidor corriendo en puerto " + port)
// })

https
	.createServer(
		{
			// key: fs.readFileSync("./pem/key.pem"),
			// cert: fs.readFileSync("./pem/cert.pem"),
			key: fs.readFileSync("./pem/certServ.pem"),
			cert: fs.readFileSync("./pem/certServ.pem"),
		},
		api
	)
	.listen(port, () => {
		console.log("Servidor corriendo en puerto " + port)
	})

