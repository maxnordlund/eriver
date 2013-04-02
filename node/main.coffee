express = require "express"
stylus = require "stylus"
socketio = require "socket.io"
etmanager = require "./etman.coffee"
config = require "../config_node.json"
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

app.get "/", (req, res) ->
  ets = ((etmanager.get id) for id in [0...config.ets.length])
  console.log ets
  res.render "status"
    ets: ets

app.get "/calibrate", (req, res) -> 
  ets = ((etmanager.get id) for id in [0...config.ets.length])
  console.log ets
  res.render "status"
    ets: ets

app.get "/calibrate/:num", (req, res) ->
  num = req.params.num
  et = etmanager.get num
  if et? && et.available
    if et.cal
      res.render "unavailable",
        et
    else
      res.render "calibrate",
        et
  else if et?
    et.id = num
    res.render "unavailable",
      et
  else
    et =
      id: num,
      cal: false
    res.render "unavailable",
      et

app.get "/heatmap/:num.png", (req, res) ->
  num = req.params.num
  if config.heatmapPath.indexOf('/') is 0
    path = "#{config.heatmapPath}/#{num}.png"
    res.sendfile path
  else
    path = "../#{config.heatmapPath}/#{num}.png"
    fs.realpath path, pathCache, (err, resolvedPath) ->
      if err?
        console.log err
        return
      res.sendfile resolvedPath

app.get "/stats/:num.json", (req, res) ->
  num = req.params.num
  if config.heatmapPath.indexOf('/') is 0
    path = "#{config.statsPath}/#{num}.json"
    res.sendfile path
  else
    path = "../#{config.statsPath}/#{num}.json"
    fs.realpath path, pathCache, (err, resolvedPath) ->
      if err?
        console.log err
        return
      res.sendfile resolvedPath

statusList = []

pushStatusUpdates = ->
  

io.of('/status').on 'connection', (socket) ->
  statusList.push socket
  
  socket.on 'disconnect', ->
    statusList.splice statusList.indexOf(socket), 1
    

io.of('/calibrate').on "connection", (socket) ->
  socket.on "name", (id) ->
    console.log "main: socket.on 'name'"
    et = etmanager.get id
    if et?
      success = etmanager.pair id, socket
      if success
        socket.emit "name", id
      else
        socket.emit "unavailable"
    else
      socket.emit "unavailable"
