$(function(){
  $("h1")[0].style.color = "grey";
  $("h1").text("No connection");
  var socket = io.connect(location.protocol + "//" + location.host + "/status");

  window.socket = socket;

  socket.emit("subscribe"); // subscribing to news

  socket.on("update", function(data) {
    console.log("update", data);
    var element, index;
    for(index in data) {
      obj = data[index];
      element = $("#" + index);
      element.find(".id").text(obj.id);
      element.find(".info").text(obj.info).css("color", obj.color);
      element.find(".ip").text(obj.ip);
      if(obj.available) {
        element.removeClass("unavailable");
        element.attr("href", "/calibrate/" + obj.id + "#");
      } else {
        element.addClass("unavailable");
        element.attr("href", "#");
      }
    }
    /*switch(data.what)
    {
    case "connecting":
      break;
    case "new":
      element = $("#" + data.id);
      element.find(".id").text(data.id);
      element.find(".ip").text(data.ip);
      element.removeClass("unavailable");
      element.attr("href", "/calibrate/" + data.id + "#");
      break;
    case "calibrating":
      element = $("#" + data.id);
      element.find(".info").text("Calibrating").css("color", "maroon");
      break;
    case "inuse":
      element = $("#" + data.id);
      element.addClass("unavailable");
      element.attr("href", "#");
      element.find(".info").text("In use").css("color", "maroon");
      break;
    case "done":
      element = $("#" + data.id);
      element.removeClass("unavailable");
      element.attr("href", "/calibrate/" + data.id + "#");
      //element.find(".info").text("");
      break;
    case "calibrated":
      element = $("#" + data.id);
      element.find(".info").text("Calibrated").css("color", "green");
      break;
    case "disconnect":
      element = $("#" + data.id);
      element.find(".id").text("?");
      element.find(".ip").text("unknown");
      element.find(".info").text("");
      element.addClass("unavailable");
      element.attr("href", "#");
      break;
    default:
      //code to be executed if n is different from case 1 and 2
    }*/
  });

  socket.on("subscribe", function() {
    $("h1").text("ET Status");
    $("h1")[0].style.color = "white";
  });
});
