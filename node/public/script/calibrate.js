$(function() {
	var OrbCount = 0;
	var midX = window.innerWidth/2;
	var xScale = 1;

	var Orb = function(x, y) {
		this.x = x || -100;
		this.y = y || 100;
		this.scale = 0.2;
		
		this.time = 300;
		
		var dom = $('<div>', {id: 'orb' + (OrbCount++)}).addClass('orb');
		var after = $('<div>').css('transition', 'all 0.3s');

		dom.append(after);
		$(document.body).prepend(dom);
		
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
			console.log("height: "+window.innerHeight+", width: "+window.innerWidth);
			this.moveToPix(x * window.innerWidth, y * window.innerHeight);
		},
		contract : function() {
			this.after.css('transform', 'scale(0.2)');
		},
		expand : function() {
			this.after.css('transform', 'scale(1.0)');
		},
		show : function() {
			$(this.dom).show();
		},
		hide : function() {
			$(this.dom).hide();
		},
		reset : function() {
			this.hide();
			this.moveTo(-0.1, 0.1);
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
	
	var popup = (function() {
		var popup = $('#popup');
		var contents = popup.find('#contents');
		var side = popup.find('#side')
		var curr = contents.find('#connecting').toggleClass('template');
		var sideVisible = false;

		var obj = {
			content: function(string) {
				var replacement = contents.find('#'+string+'.template');
				curr.toggleClass('template');
				replacement.toggleClass('template');
				curr = replacement;
				
				this.show();
			},
			sideContent: function(string) {
				side.css('background-image', 'url('+string+')');
				this.sidePeek()
				side.css('height', popup.innerHeight());
			},
			showSide: function() {
				side.css('width', 300);
				sideVisible = true;
			},
			sidePeek: function() {
				side.css('width', 20);
				sideVisible = false;
			},
			hideSide: function() {
				side.css('width', 0);
				sideVisible = false;
			},
			hide: function() {
				this.hideSide();
				popup.css('height', 0);
				setTimeout(function() {
					popup.hide();
				}, 300);
				
			},
			show: function() {
				popup.show();
				popup.css('height', '100%');
			}
		};

		side.click(function(){
			if (sideVisible) {
				obj.sidePeek();
			} else {
				obj.showSide();
			}
		});
		return obj;
	})();

	var orb = new Orb();

	var testPoint = {x: 0.5, y: 0.5};
	var calibrationPoints = [{x:0.1, y:0.1},
	{x:0.9, y:0.1}, {x:0.5, y:0.5}, {x:0.9, y:0.9},
	{x:0.1, y:0.9}];
	var _currPoints;

	/* HASH EXTRAS */
	var hashMod = function() {
		if (location.hash.indexOf("#david") == 0) {
			orb.after.addClass('davido');
		} else {
			orb.after.removeClass('davido');
		}

		if (location.hash.indexOf("#andr") == 0) {
			orb.after.addClass('andreaso');
		} else {
			orb.after.removeClass('andreaso');
		}
	}
	window.onhashchange = hashMod;
	hashMod();

	var timeouts = [];

	var socket = io.connect(location.protocol+'//'+location.host+'/calibrate');

	socket.on('name', function() {
		popup.content('prepare');
		popup.sideContent('/img/eriver_logo.png');
	});

	socket.on('connect', function() {
		parts = location.pathname.split("/");
		num = parts[parts.length-1];
		socket.emit('name', num);
	});

	socket.on('unavailable', function() {
		orb.reset();

		popup.content('unavailable');

		timeouts.forEach(function(v) {
			clearTimeout(v);
		});
	});	

	socket.on('disconnect', function() {
		orb.reset();

		popup.content('reconnecting');

		timeouts.forEach(function(v) {
			clearTimeout(v);
		});
	});

	socket.on('getPoint', function(point) {
		socket.emit('getPoint'); //end getPoint
		setTimeout(function() {
			orb.expand();
			orb.dom.hide();
			popup.content('complete'); //$('#complete').show();
			var err = Math.round(Math.sqrt(Math.pow((point.x - testPoint.x)*16/9, 2) + Math.pow(point.y - testPoint.y, 2))*window.innerHeight);
			var str = 'Calibration error of ~' + err + ' pixels.';
			console.warn(str);
			if (err < 250) {
				$('.errorRing').css('width', err+'px').css('height', err+'px');
				$('.errorRing').show();
			}
			$('.errortext').text(str);
		},500);
		
	});

	socket.on('addPoint', function() {
		orb.expand();
		setTimeout(function() {
			updateOrb(_currPoints);
		}, 500);
	});

	socket.on('endCal', function() {
		orb.contract();
		setTimeout(function() {
			socket.emit('getPoint'); //start getPoint
		}, 500);
	});

	$('#contents input[type="button"]').click(function(e) {
		e.stopPropagation();
		popup.hideSide();
		popup.hide();

		socket.on('startCal', calibrate);
		socket.emit('startCal', {angle: parseFloat($('#angle').val())});
	});

	var updateOrb = function(list) {
		if (list.length == 0) {
			orb.moveTo(testPoint.x, testPoint.y);
			setTimeout(function() {
				socket.emit('endCal');
			}, 400);

		} else {
			point = _currPoints.shift();

			orb.moveTo(point.x, point.y);

			setTimeout(function() {
				orb.contract();
				setTimeout(function() {
					socket.emit('addPoint', point);
				}, 1000);
			}, 1000);
		}
	}

	/* DEMO function, DELETE */
	var calibrate = function() {
		$(orb.dom).show();

		_currPoints = calibrationPoints.slice();

		updateOrb(_currPoints);
	}
	
	window.orb = orb;
	window.popup = popup;
	window.socket = socket;
});
