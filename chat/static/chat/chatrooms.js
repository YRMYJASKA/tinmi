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


$(document).ready(function(){
	// Set initial value of chatbox
	$('#chatbox').append($('<p>Join or create a chatroom</p>'));

	// New connection
	$(".chatroom-list-elem").click(function(){
		if (chatSocket != undefined){
			console.log("Closing previous connection...")
			chatSocket.close();
		}
		var roomid = $(this).find(".room-id-hidden").text();
		chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + roomid + '/');
		init_socket();
		$("#chatbox").empty();
		$("#chat-room-title").text($(this).find(".room_title").text())
		console.log(chatSocket);
		$('#user-msg-input').focus();
	});
	
	// Check for enter keypress
	$('#user-msg-input').keyup(function(e) {
		if (e.keyCode === 13) {  // enter, return
			document.querySelector('#user-msg-submit').click();
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

});


