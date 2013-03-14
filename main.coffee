express = require "express"
socketio = require "socket.io"

app = do express
io = socketio.listen 3001

io.on "connection", (socket) -> 
  socket.emit "news",
    hello: "world"
  socket.on "my other event", (data) ->
    console.log data


app.configure ->
  app.set "views", "#{__dirname}/views"
  app.set "view engine", "jade"
  app.use express.static "#{__dirname}/public"

  app.get "/", (req, res) -> 
    res.render "index"
    title: "Välkommen"

  app.get "/:msg/heatmap.png", (req, res) ->
    res.render "say", 
    msg: req.params.msg + "'s heatmap!"
    title: "Heatmap"
  # content-type img, hitta rätt heatmap, skicka!

  app.get "/:msg/stats.json", (req, res) ->
    res.render "say", 
    msg: req.params.msg + "'s stats!"
    title: "Stats"

  app.get "/:msg/calibrate", (req, res) ->
    res.render "say", 
    msg: req.params.msg + "'s calibration page!"
    title: "Calibrate"


  app.get "/test", (req, res) ->
    res.render "test",
    title: "test"


port  = 3000

app.listen port, -> 
  console.log process.cwd()
  console.log "Listening on #{port}"




  # ./node_modules/.bin/nodemon ../nodeProjekt/