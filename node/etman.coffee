net = require "net"
# TODO TEST
ETManager = () ->
	@ips = []
	@list = []
	return @

ETManager::listen = (ips) ->
	@ips = ips;
	for ip in @ips
		console.log ip
	return @list;

ETManager::test = () ->
	if @list?
		@list[0] =
			cal: true
			getting: false
		@list[1] =
			cal: false
			getting: false
	else
		throw new Error 'No list!'

###
client = net.connect
	port: config.port, ->
	console.log 'connected'
###

exports.new = ETManager
exports.test = ETManager::test
exports.listen = ETManager::listen