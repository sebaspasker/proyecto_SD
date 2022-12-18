const express = require('express')
const fs = require('fs')
const md5 = require('md5')
const winston = require('winston')
const router = express.Router()

module.exports = router
const {
  combine,
  timestamp,
  printf,
  align
} = winston.format

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: combine(
    timestamp({
      format: 'YYYY-MM-DD hh:mm:ss.SSS A'
    }),
    align(),
    printf((info) => `[${info.timestamp}] ${info.level}: ${info.message}`)
  ),
  transports: [
    // TODO No funciona los archivos
    new winston.transports.File({
      filename: '../logs/api_registry.log'
    }),
    new winston.transports.File({
      filename: '../logs/api_registry_error.log',
      level: 'error'
    }),
    new winston.transports.Console()
  ]
})

const usersPath = '../json/users.json'
let users = {}

try {
  // Export database users
  users = JSON.parse(fs.readFileSync(usersPath, 'utf8'))
} catch (err) {
  console.log(`Error reading file: ${err}`)
}

router.get('/', (req, res) => {
  logger.info(`Request to GET registry/. IP: ${req.socket.remoteAddress}`)
	try {
		users = JSON.parse(fs.readFileSync(usersPath, 'utf8'))
	} catch(err) {
		res.status(404)
		logger.error(`!! ERROR 404 !!  GET registry/. IP: ${req.socket.remoteAddress}, ERR: ${err.message}, usersPath: ${usersPath}.`)
		res.json({message: "Error reading file."})
		return
	}

	logger.info(`Process SUCCESS. Request to GET registry/. IP: ${req.socket.remoteAddress}`)
	res.status(200)
	res.json(users)
	return;
})

router.get('/:alias', (req, res) => {
  logger.info(`Request to GET registry/:alias IP: ${req.socket.remoteAddress}, alias: ${req.params.alias}`)
	try {
		users = JSON.parse(fs.readFileSync(usersPath, 'utf8'))
	} catch(err) {
		logger.error(`!! error 404 !! GET registry/:alias. ip: ${req.socket.remoteaddress}, users path: ${usersPath}, ERR: ${err.message}`)
		res.json("Error reading file.")
		return
	}
	

  let findAlias = false
  for (const alias in users) {
    if (alias === req.params.alias) {
      findAlias = true
    }
  }

  if (findAlias) {
    logger.info(`Process SUCCESS. Request to GET registry/:alias. IP: ${req.socket.remoteAddress}, alias: ${req.params.alias}`)
    res.status(200)
    res.json(users[req.params.alias])
  } else {
    logger.error(`!! ERROR 404 !! In GET registry/:alias, IP: ${req.socket.remoteAddress}, usersPath: ${usersPath}, ERR: Alias not found.`)
    res.status(404) // Alias not found
    res.json({
      message: 'Not found'
    })
  }
})

router.post('/', (req, res) => {
  logger.info(`Request to POST registry/ IP: ${req.socket.remoteAddress}, Alias: ${req.body.alias}, Password: ${req.body.password}`)
  if (!req.body.alias || !req.body.password) {
    logger.error(`!! ERROR 400 !! In POST registry/. IP: ${req.socket.remoteAddress}, alias: ${req.body.alias}, password: ${req.body.password}, ERR: ${err.message}`)
    res.status(400)
    res.json({
      message: 'Bad Request'
    })
		return;
  } else {
    let alreadyExists = false
    for (const alias in users) {
      if (alias === req.body.alias) {
        alreadyExists = true
        break
      }
    }

    if (!alreadyExists) {
      users[req.body.alias] = {
        alias: req.body.alias,
        pass: md5(req.body.password),
        level: 0,
        ec: 0,
        ef: 0,
        dead: 0,
        active: 1
      }

			try {
				fs.writeFileSync(usersPath, JSON.stringify(users), (error) => {
					if (error) throw error
				})
			} catch(err) {
				logger.error(`!! error 404 !! GET registry/:alias. ip: ${req.socket.remoteaddress}, userspath: ${usersPath}, ERR: ${err.message}`)
				res.json("Error reading file.")
				return;
			}

      logger.info(`Process SUCCESS. Request to POST registry/. IP: ${req.socket.remoteAddress}, alias: ${req.body.alias}, password: ${req.body.password}`)
      res.status(200)
      res.json({
        message: 'User created'
      })
    } else {
      logger.error(`!! ERROR 404 !! In POST registry/, IP: ${req.socket.remoteAddress}, alias: ${req.body.alias}, ERR: User already exists.`)
      res.status(404)
      res.json({
        message: 'Already Exists.'
      })
    }
  }
})

router.put('/:alias', (req, res) => {
  logger.info(`Request to PUT registry/:alias IP: ${req.socket.remoteAddress}, alias: ${req.params.alias}, password: ${req.body.password}`)
  users = JSON.parse(fs.readFileSync(usersPath, 'utf8'))
  if (!req.params.alias || !req.body.password) {
    logger.error(`!! ERROR 400 !! In PUT registry/:alias. IP: ${req.socket.remoteAddress}, alias: ${req.params.alias}, password: ${req.body.passowrd}, ERR: Alias or password empty.`)
    res.status(400)
    res.json({
      message: 'Bad request'
    })
  } else {
    let alreadyExists = false
    for (const alias in users) {
      if (alias === req.params.alias) {
        alreadyExists = true
        break
      }
    }

    if (alreadyExists) {
      const user = users[req.params.alias]
      users[req.params.alias] = {
        alias: req.params.alias,
        pass: md5(req.body.password),
        level: user.level,
        ec: user.ec,
        ef: user.ef,
        dead: user.dead,
        active: user.active
      }

			try {
				fs.writeFileSync(usersPath, JSON.stringify(users), (error) => {
					if (error) throw error
				})
			} catch (err) {
				logger.error(`!! error 404 !! PUT registry/:alias. ip: ${req.socket.remoteaddress}, userspath: ${usersPath}, ERR: ${err.message}`)
				res.json("Error reading file.")
				return;
			}

      res.status(200)
      logger.info(`Process SUCCESS. Request to PUT registry/:alias. IP: ${req.socket.remoteAddress}, alias: ${req.params.alias}, password: ${req.body.password}.`)
      res.json({
        message: 'User modified'
      })
    } else {
			logger.error(`!! error 404 !! PUT registry/:alias. ip: ${req.socket.remoteaddress}, alias: ${req.params.alias}, password: ${req.body.password}, ERR: Alias not found.`)
      res.status(404) // Alias not found
      res.json({
        message: 'Not found.'
      })
    }
  }
})

router.delete('/:alias', (req, res) => {
  logger.info(`Request to DELETE registry/:alias IP: ${req.socket.remoteAddress}, alias: ${req.params.alias}.`)
  let aliasExists = false

  const jsonUsers = {}
  for (const alias in users) {
    if (req.params.alias === alias) {
      aliasExists = true
    } else {
      jsonUsers[alias] = users[alias]
    }
  }

  users = jsonUsers
  fs.writeFileSync(usersPath, JSON.stringify(users))

  if (aliasExists) {
    res.status(200)
    logger.info(`Process SUCCESS. Request to DELETE registry/. IP: ${req.socket.remoteAddress}, alias: ${req.params.alias}.`)
    res.json({
      message: 'User deleted'
    })
  } else {
		logger.error(`!! error 404 !! DELETE registry/:alias. ip: ${req.socket.remoteaddress}, alias: ${req.params.alias}, ERR: Alias not found.`)
    res.status(404)
    res.json({
      message: 'Alias not found.'
    })
  }
})
