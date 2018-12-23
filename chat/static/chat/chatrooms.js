var chatSocket; // useless for now
var last_msg_time = new Date();



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
		console.log("Closed connection to" + chatSocket.url)
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
}

$(document).ready(function(){
	// Set initial value of chatbox
	$('#chatbox').append($('<p>Join or create a chatroom</p>'));
	
	// New connection
	$(document).on("click", ".chatroom-list-elem", function(event){
		var roomid = $(this).find(".room-id-hidden").text();
		var room_title= $(this).find(".room-list-title").text()
		switch_sockets(roomid, room_title);
		console.log("Switching rooms...");
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
					$("#chatroom-list").append('<div class="chatroom-list-elem"> <span class="room-title-title">' + room_title +  '</span> <p hidden class="room-id-hidden">' + roomid + '</p></div>');
					switch_sockets(roomid, room_title);
		

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
		//switch_sockets(roomid, room_title);
	});
});
