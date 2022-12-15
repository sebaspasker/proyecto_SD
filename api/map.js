const express = require('express')
const fs = require('fs');
const router = express.Router()

module.exports = router;

const map_path = "../json/map.json"
var users = {}


router.get('/', (req, res) => {
	var	map = JSON.parse(fs.readFileSync(map_path,'utf8'))
	res.json(map);
})



