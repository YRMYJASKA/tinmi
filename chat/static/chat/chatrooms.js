var chatSocket; // useless for now
var last_msg_time = new Date();
var current_id = "";


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function init_socket(){
	// WebSocket receives a message from connection
	chatSocket.onmessage = function(e) {
		var data = JSON.parse(e.data);
		var message = data['message'];
		var msg_type = data['type'];
		var sender = data['sender'];
		var colour = data['colour'];
		var d = new Date();

		console.log("Message received")
		console.log(data);

		if (msg_type == "user_msg"){
		var msg_formatted = "<b>["+d.toLocaleTimeString() + "]</b> <span style=\"color:" + colour + "\">"+ sender + "</span>: " + message + '\n';
			$('#chatbox').append($('<p class="chat-msg">' + msg_formatted + '</p>'));
		} else if (msg_type == "server_msg"){
		var msg_formatted = "<b>[" + d.toLocaleTimeString() + "]</b> <i>" + message + "</i>\n";
			$('#chatbox').append($('<p class="chat-msg">' + msg_formatted + '</p>'));
		}
		$("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);
		};

	chatSocket.onclose = function(e){
		console.log("Closed connection to " + chatSocket.url)
	};
};

function switch_sockets(roomid, room_title){
	console.log("Switching rooms...");
	if (chatSocket != undefined){
		console.log("Closing previous connection...")
		chatSocket.close();
		}
	chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + roomid + '/');
	init_socket();
	$("#chatbox").empty();
	$("#chat-room-title").text(room_title)
	console.log(chatSocket);
	$('#user-msg-input').focus();
	current_id = roomid;
}

$(document).ready(function(){
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});

	// Set initial value of chatbox
	$('#chatbox').append($('<p>Join or create a chatroom</p>'));
	
	// New connection
	$(document).on("click", ".chatroom-list-elem", function(event){
		var roomid = $(this).find(".room-id-hidden").text();
		var room_title= $(this).find(".room-list-title").text()
		
		// If already connected, do nothing
		if (roomid === current_id){
			return;
		}
		switch_sockets(roomid, room_title);
		$("#chat-room-title").text(room_title);
	});

	$(document).on("click", ".list-elem-remove", function(event){
		// Stop underlaying div from getting clicked
		event.stopPropagation();
		console.log("leaving room");
		var roomid = $(this).parent().find(".room-id-hidden").text();
		var list_elem = $(this).parent(); 
		$.ajax({
			type: "POST",
			url: "/ajax/leaveroom/", 
			data: {'room_id': roomid},
			dataType: 'json',
			success: function (data) {
			  	if (data.success) {
					console.log("Succesfully left the room!");
					// Check if leaving the same room as current connection
					// If so: close the connection 
					if(roomid === current_id){
						chatSocket.close();
						current_id = "";
					}
					
					list_elem.remove();
				} else {
					alert("Failed to leave room '" + roomid + "'!");
			  	}
			},
			error: function (xhr, ajaxOptions, thrownError, request, error){
				console.error("Error executing AJAX request!");
				console.log(this.url);
			}
		});
		console.log("moro");
		return false;
	});
	// Check for enter keypress
	$('#user-msg-input').keyup(function(e) {
		if (e.keyCode === 13) {  // enter, return
			$('#user-msg-submit').click();
		}
	});

	$('#user-msg-submit').click(function(e) {
		curr_time = new Date();
		if ((curr_time.getTime()-last_msg_time.getTime())/1000 < 0.5){
			console.log("Spam prevented! 0.5 seconds has not passed!");
			last_msg_time = curr_time;
			return;
		}
		last_msg_time = curr_time;
		var messageInputDom = document.querySelector('#user-msg-input');
		var message = messageInputDom.value;
		
		if (message == ""){
		   return;
		}

		chatSocket.send(JSON.stringify({
			'message': message
		}));

		messageInputDom.value = '';
	});

	// Dropdown menu for adding rooms
	$('#add-room-icon').click(function(){
		$('#add-room-content').toggle('slide', {
			duration: 100,
			easing: 'swing',
			direction: 'up'
		});
		$(this).toggleClass("add-room-icon-activated");
	});

	// When user clicks join room
	$('#join-room-submit').click(function(){
		var roomid = $('#join-room-id').val();
		// Check if the ID even exists
		$.ajax({
			type: "GET",
			url: "/ajax/validate_room/?room_id=" + roomid, 
			dataType: 'json',
			success: function (data) {
				console.log(data);
			  	if (data.is_valid) {
					// The chatroom exists 
					$("#join-room-id").val("");
					$("#add-room-icon").click();
					var room_title = data.room_title;
					$("#chatroom-list").append('<div class="chatroom-list-elem"> <span class="room-title-title">' + room_title +  '</span> <p hidden class="room-id-hidden">' + roomid + '</p><div class="list-elem-remove">&#10006;</div></div>');
					switch_sockets(roomid, room_title);
					$("#chatroom-list").scrollTop($("#chatroom-list")[0].scrollHeight);
				} else {
					alert("no available room with ID '" +roomid + "'");
			  	}
			},
			error: function (xhr, ajaxOptions, thrownError, request, error){
				console.error("Error executing AJAX request!");
				console.log(this.url);
			}
      	});
		return false;

	});
	// When creating a room
	// TODO: join the room when it is created
	$("#room-create-submit").click(function(e){
		var room_title = $("#id_room_title").val();
		$.ajax({
			type: "POST",
			url: "/ajax/create_room/",
			data: {'room_title': room_title},
			dataType: 'json',
			success: function (data) {
				console.log(data);
			  	if (data.success) {
					// Creation of chat room succeeded
					console.log("success!!");

					$("#id_room_title").val("");
					$("#add-room-icon").click();
					var room_title = data.room_title;
					var roomid = data.room_id;
					$("#chatroom-list").append('<div class="chatroom-list-elem"> <span class="room-title-title">' + room_title +  '</span> <p hidden class="room-id-hidden">' + roomid + '</p><div class="list-elem-remove">&#10006;</div></div>');
					switch_sockets(roomid, room_title);
					$("#chatroom-list").scrollTop($("#chatroom-list")[0].scrollHeight);
				} else {
					alert("Room creation failed!");
			  	}
			},
			error: function (xhr, ajaxOptions, thrownError, request, error){
				console.error("Error executing AJAX request!");
				console.error(request);
			}
      	});
		return false;
	});
});
