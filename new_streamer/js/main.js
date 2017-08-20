'use strict';

var socket=io.connect();//'http://localhost:8080',{'sync disconnect on unload':true});
var pcConfig = {
  'iceServers': [{
    'urls': 'stun:stun.l.google.com:19302'
  }]
};
var pc_receiverEnd;  //connection to receive from previous client/server
var pc_server_to_client=[];  //connection to forward stream to next joined client
var video=document.querySelector('#video');
var channelStream;


var n;
var temp_index;
////////////////////////////////
//telling the server that the client is connected
socket.emit('joined');
console.log("sent the signal to send stream");



            //Remember, the most important thing that signalling server will calculate the parent id of the node that is sending the 
            // message . That data must be attached to the message itself. 

//////////////////////////////////////
var message_next_callback = function(message){
if(message=='send_join_again_signal'){
  console.log("sending joined signal again");

  socket.emit('joined_again',temp_index);                          //this is when some previous client has been disconnected. 
}
else if(message=="startService"){
  console.log('received message for starting service on client');
start();
}
else if (message.type === 'candidate' ) {
    var candidate = new RTCIceCandidate({
      sdpMLineIndex: message.label,
      candidate: message.candidate
    });
    pc_receiverEnd.addIceCandidate(candidate);}
    else if (message.type === 'offer' ) {
    pc_receiverEnd.setRemoteDescription(new RTCSessionDescription(message));
    doAnswer();
  }
}

socket.on('message_next',message_next_callback);

function start(){
if(pc_receiverEnd){pc_receiverEnd.close();pc_receiverEnd=null;console.log("Closing current connection and starting a new one");}
try{
		pc_receiverEnd=new RTCPeerConnection(pcConfig);
		pc_receiverEnd.onicecandidate=handler_IceCandidate;  
		pc_receiverEnd.onaddstream=handler_remoteStreamAdded;
		console.log("created peer connection");
	}
	catch(e){
		console.log('Failed to create PeerConnection, exception: ' + e.message);
    	alert('Cannot create RTCPeerConnection object.');
	}

}
////////////////////////////////////
//now if a client is deleted
// make sure that stream is forwarded to other clients in an organised way
//so for that. If got the stream then we will send the message to the next client if it is present
//make that client send the joined signal again and start the connection.


///////////////////////////////////////////////////
//create peer connection on signal 
function handler_remoteStreamAdded(event) {
  console.log('Remote stream added.');
  video.src = window.URL.createObjectURL(event.stream);
  channelStream = event.stream;

  //
  console.log("sending send_join_signal");
//  
                   // work here
 /// socket.emit('message_next',{temp_index:temp_index,data:'send_join_again_signal'});
//
}

function handler_IceCandidate(event){
	console.log('icecandidate event: ', event);													
	//sending info about network candidate to first client
  if (event.candidate) {
    socket.emit('message',{temp_index:temp_index,data:{
      type: 'candidate',
      label: event.candidate.sdpMLineIndex,
      id: event.candidate.sdpMid,
      candidate: event.candidate.candidate
    }});
  } else {
    console.log('End of candidates.');
  }
}

function doAnswer() {
  console.log('Sending answer to peer.');
  pc_receiverEnd.createAnswer().then(
    setLocalAndSendMessage,
    function(error){
    	console.log('Failed to create session description: ' + error.toString());
    }
  );
}

function setLocalAndSendMessage(sessionDescription){
  pc_receiverEnd.setLocalDescription(sessionDescription);
  console.log('setLocalAndSendMessage sending message', sessionDescription);
  socket.emit('message',{temp_index:temp_index,data:sessionDescription});																			//work here

}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// to make the connected client act as a server to next client we proceed

//messaging service listening for messages from next sockets

var message_callback = function(message){
if(message.type=='n_value'){
  n=message.value;
}


  if(message.data=='startService'){
  console.log("starting service and sending signal to client");
temp_index=message.index;                                                                        //added
  socket.emit('message_next',{temp_index:temp_index,data:"startService"});
  maybeStartForNextClient();
}
 else if (message.data.type === 'candidate' ) {
    var candidate = new RTCIceCandidate({
      sdpMLineIndex: message.data.label,
      candidate: message.data.candidate
    });

    temp_index=message.index;                                                                     //added
    pc_server_to_client[temp_index].addIceCandidate(candidate);}
else if (message.data.type === 'answer') {

    temp_index=message.index;                                                                     //added
    pc_server_to_client[temp_index].setRemoteDescription(new RTCSessionDescription(message.data));
  } 
}

socket.on('message',message_callback);



function maybeStartForNextClient(){
  console.log("may be start called now creating peer connection");
  //peer connection
  if(pc_server_to_client[temp_index][temp_index]){pc_server_to_client[temp_index].close();pc_server_to_client[temp_index]=null;console.log("Closing current connection and starting a new one");}
  try{
    pc_server_to_client[temp_index]=new RTCPeerConnection(pcConfig);
    pc_server_to_client[temp_index].onicecandidate=handler_next_IceCandidate;  //no onaddstream handler

    console.log("created peer connection");
    pc_server_to_client[temp_index].addStream(channelStream);
    //sending offer to client
    pc_server_to_client[temp_index].createOffer(next_setLocalAndSendMessage, function(event){console.log("cannont create offer:"+event);});

  }
  catch(e){
    console.log('Failed to create PeerConnection, exception: ' + e.message);
      alert('Cannot create RTCPeerConnection object.');
  }


}

function handler_next_IceCandidate(event){
    console.log('icecandidate event: ', event);                         //work here
  //sending info about network candidate to first client
  if (event.candidate) {
    socket.emit('message_next',{temp_index:temp_index,data:{
      type: 'candidate',
      label: event.candidate.sdpMLineIndex,
      id: event.candidate.sdpMid,
      candidate: event.candidate.candidate
    }});
  } else {
    console.log('End of candidates.');
  }
}

function next_setLocalAndSendMessage(sessionDescription){
  pc_server_to_client[temp_index].setLocalDescription(sessionDescription);
  console.log('next_setLocalAndSendMessage sending message', sessionDescription);
  socket.emit('message_next',{temp_index:temp_index,data:sessionDescription});                                      //work here

}