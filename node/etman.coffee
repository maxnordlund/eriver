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
	endCal : 3
	clear : 4
	addPoint : 5
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

	# New connection to ET
	socket = net.connect port, host, ->
		console.log "Connection established to #{ip}"
		socket.on 'data', dataHandler socket
		do emitUpdate

	# Disconnected ET
	socket.on 'close', ->
		console.log "Connection to #{ip} closed, retrying..."
		setTimeout (-> connectTo ip), 10000

	socket.on 'error', ->
		return

get = (num) ->
	if num > ipList.length or num < 0
		return null

	object =
		id: '?'
		ip: 'unknown'
		cal: false
		available: false
		paired: false

	if etList[num]?
		et = etList[num]
		object.id = et.id
		object.ip = et.tcp.remoteAddress
		object.cal = et.cal
		object.available = true
		object.paired = et.socket?

	return object

# Function to remember indexing
# Write number of wanted bytes,
# index is returned
byteMemory = ->
	i = 0
	return (int) ->
		returnIndex = i
		i += int
		return returnIndex

dataHandler = (tcp) ->
	sObj =
		tcp: tcp
		id: -1
		cal: false
		calibrated: false
		getting: false
		socket: null

	tcp.on 'close', ->
		delete etList[sObj.id]
		if sObj.socket?
			sObj.socket.emit 'unavailable'
		else
			console.log "E: No one to inform."
		do emitUpdate

	cmdOnly = false

	return (data) ->
		bytes = do byteMemory

		cmd = data.readUInt8 bytes(1)

		switch cmd
			when CMD.getPoint
				x = data.readDoubleBE bytes(8)
				y = data.readDoubleBE bytes(8)
				console.log "from TCP:", cmdList[cmd], (x), (y)
				if sObj.socket?
					sObj.socket.emit 'getPoint', {x: x, y: y}

			when CMD.startCal
				if data.length > 4
					console.log "from TCP:", cmdList[cmd], (data.readDoubleBE bytes(8))
				else
					console.log "from TCP:", cmdList[cmd]
				sObj.cal = true
				if sObj.socket?
					sObj.socket.emit 'startCal', {}
				do emitUpdate

			when CMD.addPoint
				x = data.readDoubleBE bytes(8)
				y = data.readDoubleBE bytes(8)
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
				do emitUpdate

			when CMD.unavailable
				console.log "from TCP:", cmdList[cmd]
				if sObj.socket?
					sObj.socket.emit 'unavailable'

			when CMD.name
				id = data.readUInt8 bytes(1)
				console.log "from TCP:", cmdList[cmd], (id)
				sObj.id = id
				if etList[id] is undefined
					etList[id] = sObj
				else
					console.log "from TCP:", 'ET already exists.'
				do emitUpdate

			else
				console.error "from TCP:", 'Error: Unknown data packet.'

pair = (num, socket) ->
	sObj = etList[num]
	if sObj? and sObj.socket is null
		console.log "Pairing"
		sObj.socket = socket
		do emitUpdate

		socket.on 'disconnect', ->
			sObj.cal = false
			sObj.getting = false
			sObj.socket = null
			if sObj.cal
				buf = new Buffer 1
				buf.writeUInt8 CMD.endCal, 0
				sObj.tcp.write buf
			do emitUpdate

		socket.on "startCal", (data) ->
			bytes = do byteMemory
			buf = new Buffer 9
			buf.writeUInt8 CMD.startCal, bytes(1)
			buf.writeDoubleBE data.angle, bytes(8)
			console.log "socket.io:", 'startCal', data
			sObj.tcp.write buf

		socket.on "endCal", ->
			buf = new Buffer 1
			buf.writeUInt8 CMD.endCal, 0
			console.log "socket.io:", 'endCal'
			sObj.tcp.write buf
			sObj.calibrated = true

		socket.on "getPoint", ->
			bytes = do byteMemory

			buf = new Buffer 25
			buf.writeUInt8 CMD.getPoint, bytes(1)
			buf.writeDoubleBE 0, bytes(8)
			buf.writeDoubleBE 0, bytes(8)
			buf.writeUInt32BE 0, bytes(4)
			buf.writeUInt32BE 0, bytes(4)

			console.log "socket.io:", 'getPoint'

			sObj.tcp.write buf

			sObj.getting = !sObj.getting

		socket.on "addPoint", (point) ->
			console.log "socket.io:", "addPoint", point.x, point.y
			bytes = do byteMemory

			buf = new Buffer 17
			buf.writeUInt8 CMD.addPoint, bytes(1)
			buf.writeDoubleBE point.x, bytes(8)
			buf.writeDoubleBE point.y, bytes(8)

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

onUpdate = null

onFunc = (str, func) ->
	if str is "update"
		onUpdate = func

emitUpdate = ->
	if onUpdate?
		onUpdate(do statusList)

statusList = ->
	list = []

	for et in etList
		if et?
			info = ''
			color = 'maroon'
			available = true
			if et.cal
				info = 'Calibrating'
				available = false
			else if et.socket?
				info = 'In use'
				available = false
			else if et.calibrated
				info = 'Calibrated'
				color = 'green'

			list.push
				id: et.id
				ip: et.tcp.remoteAddress
				available: available
				info: info
				color: color
		else
			list.push
				id: '?'
				ip: 'unknown'
				info: ''
				color: 'black'
				available: false

	return list

exports.connect = establishConnections
exports.pair = pair
exports.get = get
exports.on = onFunc
exports.statusList = statusList
