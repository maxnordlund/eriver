$(function(){
  $("h1").text("No connection").css('color', 'gray');

  var socket = io.connect(location.protocol + "//" + location.host + "/status");

  window.socket = socket;

  socket.on("update", function(data) {
    console.log("update", data);
    var element, index, obj;
    for(index in data) {
      obj = data[index];
      element = $("#" + index);
      element.find(".id").text(obj.id);
      element.find(".info").text(obj.info).css("color", obj.color);
      element.find(".ip").text(obj.ip);
      if(obj.available) {
        element.removeClass("unavailable").attr("href", "/calibrate/" + obj.id + "#");
      } else {
        element.addClass("unavailable").attr("href", "#");
      }
    }
  });

  socket.on('connect', function () {
    $("h1").text("ET Status").css('color', 'white');
    socket.emit("subscribe"); // subscribing to news
  });

  socket.on('disconnect', function () {
    $('h1').text('Reconnecting...').css('color', 'gray');

    var els = $('.etStatus').addClass('unavailable').attr('href', '#');
    els.find('.info').text('');
    els.find('.ip').text('unknown');
  });
});
