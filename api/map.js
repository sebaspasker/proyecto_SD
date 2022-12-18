const express = require('express')
const fs = require('fs');
const router = express.Router()

module.exports = router;

const map_path = "../json/map.json"
var users = {}

// TODO No hace falta que sea API REST ya que no se llama a los 5 métodos, 
// solo get

router.get('/', (req, res) => {
	var	map = JSON.parse(fs.readFileSync(map_path,'utf8'))
	res.json(map);
})

router.post('/', (req, res) => {
	if(!req.body.map) {
		res.status(400);
		res.json({message: "Bad request."})
	} else {
		var map_dict = JSON.parse(fs.readFileSync(map_path,'utf8'))
		map_dict['map'] = req.body.map
		fs.writeFileSync(map_path, map_dict, (error) => {
			if(error) throw error;
		})

		res.json({message: "MAP CREATED"})
	}
})


