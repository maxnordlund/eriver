$(function() {
	var OrbCount = 0;
	var midX = window.innerWidth/2;
	var xScale = 1;

	var Orb = function(x, y) {
		this.x = x || -100;
		this.y = y || 100;
		this.scale = 0.3;
		
		this.time = 300;
		
		var dom = $('<div>', {id: 'orb' + (OrbCount++)}).addClass('orb');
		var after = $('<div>').css('transition', 'all 0.3s');
		dom.append(after);
		$(document.body).append(dom);
		
		this.dom = dom;
		this.id = '#' + dom.id;
		this.after = after;
		this.moveToPix(this.x, this.y);
	};
	
	Orb.prototype = {
		moveToPix : function(x, y) {
			this.x = x;
			this.y = y;
			
			$(this.dom).css('transform', 'translate('+this.x+'px,'+this.y+'px)');
		},
		moveTo : function(x, y) {
			this.moveToPix(x * window.innerWidth, y * window.innerHeight);
		},
		contract : function() {
			this.after.css('transform', 'scale(0.3)');
		},
		expand : function() {
			this.after.css('transform', 'scale(1.0)');
		},
		show : function() {
			$(this.dom).show();
		},
		hide : function() {
			$(this.dom).hide();
		}
	};
	
	/* Mock-Socket.io-socket */
	if (typeof window.io !== 'object') {
		function Socket() {
			var _this = this;
			this.cb = {};

			this.getting = false;
			
			setTimeout(function() {
				if (typeof _this.cb['connect'] == 'function') {
					_this.cb['connect']();
				}
			}, 3000);
		}
		
		Socket.prototype = {
			emit: function(type, data) {
				if (typeof this.cb[type] === 'function') {
					if (type == 'getPoint') {
						this.getting = !this.getting;
						if (!this.getting) {
							return;
						}
						data = {x: 0.47, y: 0.51};
					}
					this.cb[type](data);
				}
			},
			on: function(type, func) {
				this.cb[type] = func;
			}
		}
		
		window.io = (function() {
			this.connect = function(addr) {
				return new Socket();
			};
			return this;
		})();
	}
	
	window.Orb = Orb;

	var orb = new Orb();
	var ready = true;

	var testPoint = {x: 0.5, y: 0.5};
	var calibrationPoints = [{x:0.1, y:0.1},
		{x:0.9, y:0.1}, {x:0.5, y:0.5}, {x:0.9, y:0.9},
		{x:0.1, y:0.9}];
	
	var socket = io.connect(location.protocol+'//'+location.host);

	socket.on('connect', function() {
		socket.emit('name', location.pathname.slice(-1));
	});

	socket.on('name', function() {
		$('.popup').hide();
		$('#prepare').show();
	});

	socket.on('unavailable', function() {
		/*
		setTimeout(function () {
			socket.emit('name', location.pathname.slice(-1));
		}, 2500); // TODO lower delay?
		*/
		location.reload();
	});	

	socket.on('disconnect', function() {
		$(orb.dom).hide();
		orb.moveTo(-0.1, 0.1);
		$('.popup').hide();
		var popup = $('#connecting');
		popup.find('h2').css('color', 'red').text('Reconnecting...');
		popup.show();

	});

	socket.on('getPoint', function(point) {
		var err = Math.round(Math.sqrt(Math.pow((point.x - testPoint.x)*16/9, 2) + Math.pow(point.y - testPoint.y, 2))*window.innerHeight);
		var str = 'Calibration error of ~' + err + ' pixels.';
		console.warn(str);
		$('.errorsize').show();
		$('.errorsize').css('width', err+'px').css('height', err+'px');
		$('.errortext').text(str);
	});

	/* DEMO method, DELETE */
	$('.popup input[type="button"]').click(function(e) {
		if (ready) {
			e.stopPropagation();
			$(this).parent().hide();
			
			socket.emit('startCal', {angle: parseFloat($('#angle').attr('value'))});
		
			socket.on('startCal', calibrate);
		}
	});
	
	/* DEMO function, DELETE */
	var calibrate = function() {
		var flexWait = orb.time * 6;
		var moveWait = 1000;
		var extra = 0;

		
		var totalTime = moveWait + flexWait + extra;

		//$('#back').hide();
		$(orb.dom).show();
		
		calibrationPoints.forEach(function(point, index) {
			setTimeout(function() {
				orb.moveTo(point.x, point.y);
				setTimeout(function() {
					socket.emit('addPoint', point);
					orb.contract();
					setTimeout(function() {
						orb.expand();
					}, 1000);
				}, 1000);
			}, totalTime*index);
		});

		setTimeout(function() {
			orb.moveTo(testPoint.x, testPoint.y);

			socket.emit('endCal');

			setTimeout(function() {
				socket.emit('getPoint'); //start getPoint
				socket.emit('getPoint'); //end getPoint
				$(orb.dom).hide();
				$('#complete').show();
				//$('#back').show();
			}, 1000);
		}, totalTime*5);
	}
	
	window.orb = orb;
});
