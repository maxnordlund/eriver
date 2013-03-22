express = require "express"
stylus = require "stylus"
socketio = require "socket.io"
config = require "./config.json"

app = do express

port = config.port

server = app.listen port, -> 
  console.log process.cwd()
  console.log "Listening on #{port}"

io = socketio.listen server

app.configure ->
  app.set "views", "#{__dirname}/views"
  app.set "view engine", "jade"
  app.use express.static "#{__dirname}/public"
  app.use stylus.middleware
    src: "#{__dirname}/public"

  app.get "/", (req, res) -> 
    res.send "index"

  app.get "/calibrate/:msg", (req, res) ->
    res.render "calibrate"
    #msg: req.params.msg + "s calibration page!"

io.sockets.on "connection", (socket) ->

  socket.on "startCal", (angle) ->
    socket.emit "startCal"
    # ta vara på angle också!

  socket.on "endCal", ->
    socket.emit "endCal"

  socket.on "getPoint", ->
    socket.emit "getPoint", {x: 0.52, y: 0.45}

  socket.on "addPoint", (point) ->
    socket.emit "addPoint", point

  socket.on "clear", ->
    socket.emit "clear"

  ###
  socket.on "unavalible", ->
    socket.emit "unavalible"
  ###

  socket.on "disconnect", ->
    return