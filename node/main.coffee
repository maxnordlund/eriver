express = require "express"
stylus = require "stylus"
socketio = require "socket.io"
etman = require "./etman.coffee"
config = require "../config.json"
fs = require "fs"
nib = require "nib"

app = do express

port = config.port

server = app.listen port, -> 
  console.log process.cwd()
  console.log "Listening on #{port}"

io = socketio.listen server

pathCache = {}
# TODO TEST START
etmanager = do etman.new
#console.log etmanager
etmanager.listen config.ets # TEST that config.ets works and listen prints them *WORKING*
do etmanager.test # FILL etmanager.list with testing values *WORKING*
ets = etmanager.list
#console.log ets

#do etmanager.test # TODO TEST STOP

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
  res.send "index"

app.get "/calibrate/:num", (req, res) ->
  num = req.params.num
  if ets[num]?
    if ets[num].cal
      res.render "unavailable",
        id: num,
        cal: true 
    else
      res.render "calibrate"
    #TODO
  else
    res.render "unavailable",
      id: num,
      cal: false
    #TODO

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

io.sockets.on "connection", (socket) ->

  socket.on "startCal", (angle) ->
    socket.emit "startCal"
    # ta vara på angle också!

  socket.on "endCal", ->
    socket.emit "endCal"

  socket.on "getPoint", ->
    ets[0].getting = !ets[0].getting  # TODO TEST
    if ets[0].getting                 # TODO TEST
      socket.emit "getPoint",
      x: Math.random()*0.2+0.45
      y: Math.random()*0.2+0.45
    

  socket.on "addPoint", (point) ->
    socket.emit "addPoint", point

  socket.on "clear", ->
    socket.emit "clear"

  socket.on "unavailable", ->
    socket.emit "unavailable"

  socket.on "disconnect", ->
    return