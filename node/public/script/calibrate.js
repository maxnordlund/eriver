$(function() {
	var OrbCount = 0;
	//var midX = window.innerWidth/2;
	//var xScale = 1;

	var Orb = function(x, y) {
		this.x = x || -100;
		this.y = y || 100;
		this.scale = 0.2;
		
		this.moveTime = 500;
		this.time = 300;
		
		var dom = $('<div>', {id: 'orb' + (OrbCount++)}).addClass('orb').css('transition', 'all 0.' + this.moveTime/1000 +'s');
		var after = $('<div>').css('transition', 'all 0.' + this.time/1000 +'s');

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
			//this.moveToPix(x * window.innerWidth, y * window.innerHeight);
			this.moveToPix(x * window.screen.width, y * window.screen.height);
		},
		contract : function() {
			this.after.css('transform', 'scale(' + this.scale + ')');
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
		},
		flex : function() {
			this.contract();
			setTimeout(function() {
				this.expand();
			}, 50);
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
	
	// Dialog window and controls.
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
				return this;
			},
			sideContent: function(string) {
				side.css('background-image', 'url('+string+')');
				this.sidePeek()
				side.css('height', popup.innerHeight());
			},
			showSide: function() {
				side.css('width', 300);
				sideVisible = true;
				return this;
			},
			sidePeek: function() {
				side.css('width', 20);
				sideVisible = false;
				return this;
			},
			hideSide: function() {
				side.css('width', 0);
				sideVisible = false;
				return this;
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

	// Focus Orb
	var orb = new Orb();

	// List of points to use for calibration.
	var calibrationPoints = [{x:0.1, y:0.1},
		{x:0.9, y:0.1}, {x:0.5, y:0.5}, {x:0.9, y:0.9},
		{x:0.1, y:0.9}];

	// A point used to check calibration accuracy.
	var testPoint = {x: 0.5, y: 0.5};

	// List of points used during the recursive calibration.
	var _currPoints;

	/* HASH EXTRAS */
	var hashMod = function() {
		orb.after.attr('class', location.hash.slice(1));
		/*
		if (location.hash.indexOf("#david") == 0) {
			orb.after.addClass('davido');
		} else {
			orb.after.removeClass('davido');
		}

		if (location.hash.indexOf("#andreas") == 0) {
			orb.after.addClass('andreaso');
		} else {
			orb.after.removeClass('andreaso');
		}

		if (location.hash.indexOf("#andr") == 0) {
			orb.after.addClass('andreaso');
		} else {
			orb.after.removeClass('andreaso');
		}
		*/
	}
	window.onhashchange = hashMod;
	hashMod();

	var timeouts = [];

	var socket = io.connect(location.protocol+'//'+location.host+'/calibrate');

	// On an established connection, inform server of target ET. 
	socket.on('connect', function() {
		parts = location.pathname.split("/");
		num = parts[parts.length-1];
		socket.emit('name', num);
	});

	// Once the ET is known, tell the user to prepare.
	socket.on('name', function() {
		popup.content('prepare');
		popup.sideContent('/img/eriver_logo.png');
	});

	// Set the "Calibrate" button to initiate calibration.
	// Informs the server of the screen angle.
	$('#contents input[type="button"]').click(function(e) {
		e.stopPropagation();
		popup.hideSide();
		popup.hide();

		// Once the server approves the calibration request,
		// "calibrate" is called to initiate the process.
		socket.on('startCal', calibrate);
		var val = parseFloat($('#angle').val());
		if (val === NaN) {
			val = 15;
		}
		socket.emit('startCal', {angle: val});
	});

	// Shows the orb, and sets the calibration points.
	// Initial call to "updateOrb".
	var calibrate = function() {
		$(orb.dom).show();

		_currPoints = calibrationPoints.slice();

		updateOrb(_currPoints);
	}

	// Is called recursively to move the Orb and send
	// "addPoint" commands. Reduces the size of the list
	// by one at each iteration. Sends "enCal" command
	// if the list is empty.
	var updateOrb = function(list) {
		if (list.length == 0) {
			orb.moveTo(testPoint.x, testPoint.y);
			socket.emit('endCal');
		} else {
			point = _currPoints.shift();

			orb.moveTo(point.x, point.y);

			setTimeout(function() {
				orb.contract();
				setTimeout(function() {
					socket.emit('addPoint', point);
				}, orb.moveTime);
			}, orb.moveTime*2);
		}
	}

	// Once the server confirms the "addPoint", 
	// the "updateOrb" is called, and the process continues.
	socket.on('addPoint', function() {
		orb.expand();
		setTimeout(function() {
			updateOrb(_currPoints);
		}, orb.moveTime);
	});

	// Once the server responds that calibration is completed
	// a "getPoint" request is sent to validate calibration.
	socket.on('endCal', function() {
		orb.contract();
		//setTimeout(function() {
			socket.emit('getPoint'); //start getPoint
		//}, orb.moveTime);
	});

	// Once the server sends a "getPoint", with data,
	// another "getPoint" request is sent to terminate flow.
	// The error is calculated and displayed to the user,
	// in as well as a prompt to restart the process if the
	// calibration wasn't accurate.
	socket.on('getPoint', function(point) {
		socket.emit('getPoint'); //end getPoint
		orb.expand();
		setTimeout(function() {
			orb.dom.hide();
			popup.content('complete'); //$('#complete').show();
			var err = Math.round(Math.sqrt(Math.pow((point.x - testPoint.x)*16/9, 2) + Math.pow(point.y - testPoint.y, 2))*window.innerHeight);
			
			err = Math.min(err, 250);
			$('#errorRing').css('width', err+'px').css('height', err+'px').show();
			
			if (err < 80) {
				$('#errorRing').css('border-color', '#00cc66');
				$('#errortext').text("Calibrated. Good to go.");
			} else {
				$('#errorRing').css('border-color', 'red');
				$('#errortext').html("Large calibration error.<br>Please press F5 to recalibrate.").css('color', '#cc0000');
			}
		}, orb.moveTime);
	});

	// PROBLEM HANDLERS
	// If the ET was to become unavailable.
	socket.on('unavailable', function() {
		orb.reset();

		popup.content('unavailable');

		timeouts.forEach(function(v) {
			clearTimeout(v);
		});
	});	

	// If the connection was lost.
	socket.on('disconnect', function() {
		orb.reset();

		popup.content('reconnecting');
		popup.hideSide();
		timeouts.forEach(function(v) {
			clearTimeout(v);
		});
	});

	// Sets global variables. 
	window.orb = orb;
	window.popup = popup;
	window.socket = socket;
})(window);
