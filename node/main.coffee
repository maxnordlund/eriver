express = require "express"
stylus = require "stylus"
socketio = require "socket.io"
etmanager = require "./etman"
config = require "./config"
fs = require "fs"
nib = require "nib"

app = do express

port = config.port

server = app.listen port, ->
  console.log process.cwd() # Current execution directory
  console.log "Listening on #{port}"

io = socketio.listen server

pathCache = {}

etmanager.connect config.ets # etmanager establishes connections to ips defined in config.ets

app.configure ->
  app.set "views", "#{__dirname}/views"
  app.set "view engine", "jade"
  app.use express.static "#{__dirname}/public"
  app.use stylus.middleware
    src: "#{__dirname}"
    dest: "#{__dirname}/public/style"
    compile: (str, path) ->
      return stylus(str)
        .set('filename', path)
      # .set('compress', true)
        .use(nib())
  app.use (err, req, res, next) ->
    console.error "A scary error:"
    console.error err.stack 
    res.send 500, "Error!!!"

app.get "/", (req, res) ->
  #ets = ((etmanager.get id) for id in [0...config.ets.length])
  res.render "status",
    n: config.ets.length
    #ets: ets

app.get "/calibrate", (req, res) ->
  #ets = ((etmanager.get id) for id in [0...config.ets.length])
  res.render "status",
    n: config.ets.length
    #ets: ets

app.get "/calibrate/:num", (req, res) ->
  num = req.params.num
  et = etmanager.get num
  if et? && et.available
    if et.cal
      res.render "unavailable", et
    else
      res.render "calibrate", et
  else if et?
    et.id = num
    res.render "unavailable", et
  else
    et =
      id: num,
      cal: false
    res.render "unavailable", et
  return et

safeSendFile = (type, extention) -> (req, res) ->
  num = req.params.num
  if config[type].indexOf('/') is 0
    path = "#{config[type]}/#{num}.#{extention}"
    res.sendfile path
  else
    path = "../#{config[type]}/#{num}.#{extention}"
    fs.realpath path, pathCache, (err, resolvedPath) ->
      if err?
        console.error err
        res.send 500, err.stack
      else
        res.sendfile resolvedPath

app.get "/heatmap/:num.png", safeSendFile "heatmapPath", 'png'

app.get "/statistics/:num.json", safeSendFile "statsPath", 'json'

io.of('/calibrate').on "connection", (socket) ->
  socket.on "name", (id) ->
    console.log "main: socket.on 'name'"
    if etmanager.get(id)?
      if etmanager.pair id, socket
        # success
        socket.emit "name", id
      else
        socket.emit "unavailable"
    else
      socket.emit "unavailable"

statusSockets = {}

etmanager.on 'update', (data) ->
  for i of statusSockets
  	statusSockets[i].emit 'update', do etmanager.statusList

io.of('/status').on 'connection', (socket) ->
  socket.on 'subscribe', ->
    statusSockets[socket.id] = socket
    socket.emit 'subscribe'
    socket.emit 'update', do etmanager.statusList

  socket.on 'disconnect', ->
    delete statusSockets[socket.id]

