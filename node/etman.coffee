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
getList = ->
	for o in etList
		if 
###

get = (num) ->
	if num > ipList.length or num < 0
		return null

	o =
		id: '?'
		ip: 'unknown'
		cal: false
		available: false

	if etList[num]?
		et = etList[num]
		o.id = et.id
		o.ip = et.tcp.remoteAddress
		o.cal = et.cal
		o.available = true
		return o
	else
		return o

# Function to remember indexing
# Write number of wanted bytes,
# index is returned
byteMemory = ->
	i = 0
	return (int) ->
		tmp = i
		i += int
		return tmp

dataHandler = (tcp) ->
	sObj =
		tcp: tcp
		id: -1
		cal: false
		getting: false
		socket: null

	tcp.on 'close', ->
		delete etList[sObj.id]
		if sObj.socket?
			sObj.socket.emit 'unavailable'
		else
			console.log "E: No one to inform."

	cmdOnly = false

	return (data) ->
		bytes = do byteMemory

		cmd = data.readUInt8 bytes(1)

		switch cmd
			when CMD.getPoint
				x = data.readDoubleBE bytes(4)
				y = data.readDoubleBE bytes(4)
				console.log "from TCP:", cmdList[cmd], (x), (y)
				if sObj.socket?
					sObj.socket.emit 'getPoint', {x: x, y: y}

			when CMD.startCal
				if data.length > 4
					console.log "from TCP:", cmdList[cmd], (data.readDoubleBE bytes(1))
				else
					console.log "from TCP:", cmdList[cmd]
				sObj.cal = true
				if sObj.socket?
					sObj.socket.emit 'startCal', {}

			when CMD.addPoint
				x = data.readDoubleBE bytes(4)
				y = data.readDoubleBE bytes(4)
				#x = data.readDoubleBE 1
				#y = data.readDoubleBE 9
				console.log "from TCP:", cmdList[cmd], (x), (y)
				if sObj.socket?
					sObj.socket.emit 'addPoint', {x: x, y: y}
				
			when CMD.clear
				console.log "from TCP:", cmdList[cmd]
				if sObj.socket?
					sObj.socket.emit 'clear'
				
			when CMD.endCal
				console.log "from TCP:", cmdList[cmd]
				sObj.cal = false
				if sObj.socket?
					sObj.socket.emit 'endCal'
				
			when CMD.unavailable
				console.log "from TCP:", cmdList[cmd]
				if sObj.socket?
					sObj.socket.emit 'unavailable'
				
			when CMD.name
				#id = data.readUInt8 1
				id = data.readUInt8 bytes(1)
				console.log "from TCP:", cmdList[cmd], (id)
				sObj.id = id
				if etList[id] is undefined
					etList[id] = sObj
				else
					console.log "from TCP:", 'ET already exists.'

			else
				console.error "from TCP:", 'Error: Unknown data packet.'

pair = (num, socket) ->
	sObj = etList[num]
	if sObj? and sObj.socket is null
		console.log "Pairing"
		sObj.socket = socket

		socket.on 'disconnect', ->
			sObj.cal = false
			sObj.getting = false
			sObj.socket = null

		socket.on "startCal", (data) ->
			buf = new Buffer 9
			buf.writeUInt8 CMD.startCal, 0
			buf.writeDoubleBE data.angle, 1
			console.log "socket.io:", 'startCal', data
			sObj.tcp.write buf

		socket.on "endCal", ->
			buf = new Buffer 1
			buf.writeUInt8 CMD.endCal, 0
			console.log "socket.io:", 'endCal'
			sObj.tcp.write buf

		socket.on "getPoint", ->
			buf = new Buffer 25
			buf.writeUInt8 CMD.getPoint, 0
			buf.writeDoubleBE 0, 1
			buf.writeDoubleBE 0, 9
			buf.writeUInt32BE 0, 17
			buf.writeUInt32BE 0, 21

			console.log "socket.io:", 'getPoint'

			sObj.tcp.write buf

			sObj.getting = !sObj.getting

		socket.on "addPoint", (point) ->
			console.log "socket.io:", "addPoint", point.x, point.y

			buf = new Buffer 17
			buf.writeUInt8 CMD.addPoint, 0
			buf.writeDoubleBE point.x, 1
			buf.writeDoubleBE point.y, 9

			console.log "socket.io:", 'addPoint', point

			sObj.tcp.write buf

		socket.on "clear", ->
			buf = new Buffer 1
			buf.writeUInt8 CMD.clear, 0

			console.log "socket.io:", 'clear'

			sObj.tcp.write buf

		socket.on "unavailable", ->
			socket.emit "unavailable"
			buf new Buffer 1
			buf.writeUInt8 CMD.unavailable, 0

			console.log "socket.io:", 'unavailable'
			sObj.tcp.write buf

		socket.on "name", (data) ->
			buf new Buffer 1
			buf.writeUInt8 CMD.name, 0
			sObj.tcp.write buf

			console.log "socket.io:", 'name', data.id
			socket.emit "name", data.id

		return true
	else
		console.log "socket.io:", "No such ET, or already paired..."
		return false

log = console.log

exports.connect = establishConnections
exports.pair = pair
exports.get = get
