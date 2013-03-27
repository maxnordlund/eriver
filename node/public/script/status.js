$(function(){
	var socket = io.connect(location.protocol+'//'+location.host+'/status');

	window.socket = socket;
});