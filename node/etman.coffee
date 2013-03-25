net = require "net"

###

et = {
	tcp: [object TCPSocket],
	num: 1,
	cal: true
	getting: false
	socket: [object Socket.io]
	onclose: null
}
###

ipList = []
etList = []

CMD =
	getPoint : 1
	startCal : 2
	addPoint : 3
	clear : 4
	endCal : 5
	unavailable : 6
	name : 7

cmdList = [
	'unused'
	'getPoint'
	'startCal'
	'addPoint'
	'clear'
	'endCal'
	'unavailable'
	'name'
]

establishConnections = (ips) ->
	ipList = ips
	for ip in ipList
		connectTo ip

test = () ->
	etList[0] =
		cal: true
		getting: false
	etList[1] =
		cal: false
		getting: false
	return etList

connectTo = (ip) ->
	[host, port] = ip.split ":"
	if port is undefined
		port = "3031"

	socket = net.connect port, host, () ->
		console.log "Connection established to #{ip}"
		socket.on 'data', dataHandler socket

	socket.on 'close', () ->
		console.log "Connection to #{ip} closed, retrying..."
		setTimeout (() -> connectTo ip), 10000

	socket.on 'error', () ->
		return

###
	socket.setTimeout 5000, ()->
		do socket.destroy
		console.log "Retrying #{ip}..."
		connectTo ip
###

get = (num) ->
	if etList[num]?

		o = {
			id: num
			cal: etList[num].cal
		}
		console.log o
		return o
	else
		return null

dataHandler = (tcp) ->
	sObj =
		tcp: tcp
		id: 0
		cal: false
		getting: false
		socket: null


	return (data) ->
		cmd = data.readUInt8 0

		switch cmd
			when CMD.getPoint
				x = data.readDoubleBE 1
				y = data.readDoubleBE 9
				console.log cmdList[cmd], (x), (y)
				if sObj.socket?
					sObj.socket.emit 'getPoint', {x: x, y: y}

			when CMD.startCal
				console.log cmdList[cmd], (data.readDoubleBE 1)
				sObj.cal = true
				if sObj.socket?
					sObj.socket.emit 'startCal'

			when CMD.addPoint
				x = data.readDoubleBE 1
				y = data.readDoubleBE 9
				console.log cmdList[cmd], (x), (y)
				if sObj.socket?
					sObj.socket.emit 'addPoint', {x: x, y: y}
				
			when CMD.clear
				console.log cmdList[cmd]
				if sObj.socket?
					sObj.socket.emit 'clear'
				
			when CMD.endCal
				console.log cmdList[cmd]
				sObj.cal = false
				if sObj.socket?
					sObj.socket.emit 'endCal'
				
			when CMD.unavailable
				console.log cmdList[cmd]
				if sObj.socket?
					sObj.socket.emit 'unavailable'
				
			when CMD.name
				id = data.readUInt8 1
				console.log cmdList[cmd], (id)
				sObj.id = id
				etList[id] = sObj

			else
				console.error 'Error: Unknown data packet.'



pair = (num, socket) ->
	sObj = etList[num]
	if sObj? and sObj.socket is null
		console.log "Pairing"
		sObj.socket = socket

		socket.on 'disconnect', () ->
			sObj.socket = null

		socket.on "startCal", (data) ->
			buf = new Buffer 9
			buf.writeUInt8 CMD.startCal, 0
			buf.writeDoubleBE data.angle, 1
			sObj.tcp.write buf

		socket.on "endCal", ->
			buf = new Buffer 1
			buf.writeUInt8 CMD.endCal, 0
			sObj.tcp.write buf

		socket.on "getPoint", ->
			buf = new Buffer 25
			buf.writeUInt8 CMD.getPoint, 0
			buf.writeDoubleBE 0, 1
			buf.writeDoubleBE 0, 9
			buf.writeUInt32BE 0, 17
			buf.writeUInt32BE 0, 21

			sObj.tcp.write buf

			sObj.getting = !sObj.getting

		socket.on "addPoint", (point) ->
			console.log "addPoint", point.x, point.y

			buf = new Buffer 17
			buf.writeUInt8 CMD.addPoint, 0
			buf.writeDoubleBE point.x, 1
			buf.writeDoubleBE point.y, 9
			sObj.tcp.write buf

		socket.on "clear", ->
			buf = new Buffer 1
			buf.writeUInt8 CMD.clear, 0
			sObj.tcp.write buf

		socket.on "unavailable", ->
			socket.emit "unavailable"
			buf new Buffer 1
			buf.writeUInt8 CMD.unavailable, 0
			sObj.tcp.write buf

		socket.on "name", (data) ->
			buf new Buffer 1
			buf.writeUInt8 CMD.name, 0
			sObj.tcp.write buf
			socket.emit "name", data.id

		sObj.tcp.on 'close', ->
			delete etList[num]
			if sObj.socket?
				sObj.socket.emit 'unavailable'

	else
		console.log "No such ET, or already paired..."

###
client = net.connect
	port: config.port, ->
	console.log 'connected'
###


exports.test = test
exports.connect = establishConnections
exports.pair = pair
exports.get = get

###

etman.listen ips

etman.available 1



###