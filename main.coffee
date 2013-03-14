express = require 'express'
stylus = require 'stylus'
socketio = require 'socket.io'
config = require './config.json'

app = do express

server = app.listen config.port, -> 
  console.log process.cwd()
  console.log 'Listening on #{config.port}'

io = socketio.listen server

app.configure ->
  app.set 'views', '#{__dirname}/views'
  app.set 'view engine', 'jade'
  app.use express.static '#{__dirname}/public'
  app.use stylus.middleware
    src: '#{__dirname}/public'

  app.get '/', (req, res) -> 
    res.send 'index'

  app.get '/calibrate/:msg', (req, res) ->
    res.render 'calibrate'
    #msg: req.params.msg + ''s calibration page!'

io.sockets.on 'connection', (socket) ->

  socket.on 'startCal', (angle) ->
    socket.emit 'started'

  ###socket.on 'endCal' ->
    return

  socket.on 'getPoint' ->
    return

  socket.on 'addPoint', (point) ->
    return

  socket.on 'clear' ->
    return

  socket.on 'unavalible' ->
    return

  socket.on 'disconnect' ->
    return
  ###