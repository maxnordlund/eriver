net = require "net"

ETManager = () ->
	@ips = []
	@list = []
	return @

ETManager::listen = (ips) ->
	@ips = ips;

	for ip in @ips
		console.log ip

	return @list;

#ETManager::

ETManager::test = () ->
	if list?
		list[0] =
			cal: true
		list[1] =
			cal: false
	else
		throw new Error 'No list!'

###
client = net.connect
	port: config.port, ->
	console.log 'connected'
###

exports.new = ETManager;