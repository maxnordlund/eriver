express = require 'express'
stylus = require 'stylus'
socketio = require 'socket.io'

# etListener = require 

app = do express
###
io.on "connection", (socket) -> 
  socket.emit "news",
    hello: "world"
  socket.on "my other event", (data) ->
    console.log data
###

app.configure ->
  app.set "views", "#{__dirname}/views"
  app.set "view engine", "jade"
  app.use express.static "#{__dirname}/public"
  app.use stylus.middleware
    src: "#{__dirname}/public"

  app.get "/", (req, res) -> 
    res.send 'index'

  app.get "/calibrate/:msg", (req, res) ->
    res.render 'calibrate'
    #msg: req.params.msg + "'s calibration page!"

port = 3000

server = app.listen port, -> 
  console.log process.cwd()
  console.log "Listening on #{port}"

io = socketio.listen server