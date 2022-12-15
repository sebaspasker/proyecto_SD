const express = require('express')
const fs = require('fs');
const router = express.Router()

module.exports = router;

const users_path = "../json/users.json"
var users = {}

try {
	// Export database users
	users = JSON.parse(fs.readFileSync(users_path,'utf8'))
} catch(err) {
	console.log(`Error reading file: ${err}`)
}

router.get('/', (req, res) => {
	users = JSON.parse(fs.readFileSync(users_path,'utf8', (err) => {
		if(err) {
			throw err
		}
	}))

	res.json(users);
})


router.get('/:alias', (req, res) => {
	users = JSON.parse(fs.readFileSync(users_path,'utf8', (err) => {
		if(err) {
			throw err
		}
	}))

	var findAlias = false
	for(var alias in users) {
		if(alias == req.params.alias)
			findAlias = true;
	}

	if(findAlias) {
		res.status(200)
		res.json(users[req.params.alias])
	} else {
		res.status(404); // Alias not found
		res.json({message: "Not found"})
	}
}) 

router.post('/', (req, res) => {
	if(!req.body.alias || !req.body.password) {
		res.status(400)
		res.json({message: "Bad Request"});
	}	else {
		var alreadyExists = false;
		for(var alias in users) {
			if(alias == req.body.alias) {
				alreadyExists = true;	
				break
			}
		}


		if(!alreadyExists) {
			users[req.body.alias] = {
				alias : req.body.alias,
				pass : req.body.password,
				level: 0,
				ec: 0,
				ef: 0,
				dead: 0,
				active: 1
			}
	
			fs.writeFileSync(users_path, JSON.stringify(users), (error) => {
				if(error) throw error;
			})

			res.json({message: "User created"})
		} else {
			res.status(404); // Alias not found
			res.json({message: "Already Exists."})
		}
	}
})

router.put('/:alias', (req, res) => {
	users = JSON.parse(fs.readFileSync(users_path,'utf8'))
	if(!req.params.alias || !req.body.password) {
		res.status(400);
		res.json({message: "Bad request"})
	} else {
		var alreadyExists = false;
		for(var alias in users) {
			if(alias == req.params.alias) {
				alreadyExists = true;	
				break
			}
		}

		if(alreadyExists) {
			var user = users[req.params.alias]
			users[req.params.alias] = {
				alias : req.params.alias,
				pass : req.body.password,
				level: user.level,
				ec: user.ec,
				ef: user.ef,
				dead: user.dead,
				active: user.active 
			}
	
			fs.writeFileSync(users_path, JSON.stringify(users), (error) => {
				if(error) throw error;
			})

			res.json({message: "User modified"})
		} else {
			res.status(404); // Alias not found
			res.json({message: "Not found."})
		}
	}
})

router.delete('/:alias', (req, res) => {
	var aliasExists = false;

	var json_users = {}
	for(var alias in users) {
		if(req.params.alias  == alias) {
			aliasExists = true;
		} else {
			json_users[alias] = users[alias];
		}
	}
	
	users = json_users
	fs.writeFileSync(users_path, JSON.stringify(users))

	if(aliasExists) {
		res.json({message: "User deleted"})
	} else {
		res.status(404);
		res.json({Message: "Alias not found."})
	}

	var removeAlias
})

// api.get('/registry/users/:user', (req, res) => {
// 	var alias = req.params.user
// 	var keys = Object.keys(database_user)
// 	if (keys.includes(alias)) {
// 		res.send(database_user[alias])
// 	} else {
// 		console.log("No ha encontrado el usuario")
// 	}
// })
// api.get('/registry/create_user', (req,res) => {
// 	res.send("Create user page of the registry.")
// })

// // api.get('/registry/delete_user')


