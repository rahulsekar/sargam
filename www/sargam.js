var base_url    = window.location.href.split( '/' )[2];
var isRecording = false;
var ws          = null;
var bufferSize  = 4096;
var userMediaConfig =
    { "audio":
      { "mandatory":
	{ "googEchoCancellation": "false",
	  "googAutoGainControl": "false",
	  "googNoiseSuppression": "false",
	  "googHighpassFilter": "false"
	},
	"optional": []
      }
    };

var lesson    = null;
var lessonidx = -1;
var context   = new (window.AudioContext||window.webkitAudioContext)();
var micSource = null;
var processor = null;

if( !context.createScriptProcessor )
    context.createScriptProcessor = context.createJavaScriptNode;

function updateLesson()
{
    var elem = document.getElementById( "lesson" );

    if( lessonidx < 0 )
    {
	elem.innerHTML = lesson
	return;
    }
    
    var done = lesson.substring( 0, lessonidx );
    var exp  = '', yet = '';
    
    if( lessonidx < lesson.length )
    {
	exp = lesson[ lessonidx ]
	yet = lesson.substring( lessonidx + 1 );
    }
    elem.innerHTML = "<font color=\"green\">" + done + "</font>";
    elem.innerHTML += "<font color=\"red\">" + exp + "</font>";
    elem.innerHTML += "<font color=\"black\">" + yet + "</font>";
}

function onWsMessage( evt )
{
    parts = evt.data.split( ',' )

    for( var i = 0; i < parts.length; ++i )
    {
	var keyval = parts[ i ].split( '=' )
	var key    = keyval[0]
	switch( key )
	{
	case 'r' : // result
	    document.getElementById( "res" ).innerHTML = keyval[1];
	    break;
	case 'b' : // bufferRate
	    bufferSize = context.sampleRate / parseInt( keyval[1] )
	case 'l' : // lesson
	    lesson = keyval[1];
	    updateLesson();
	    break;
	case 'n' : // next 
	    lessonidx = parseInt( keyval[1] );
	    updateLesson();
	    break;
	case 'd' : // done
	    console.log( 'msg: d ' );
	    stopRecord()
	    break;
	case 's' : // score
	    document.getElementById( "score" ).innerHTML = keyval[1];
	    break;
	case 'm' : // message
	    document.getElementById( "message" ).innerHTML = keyval[1];
	    break;
	}
    }
}

ws           = new WebSocket( "ws://" + base_url + "/ws" );
ws.onopen    = function(){};
ws.onmessage = onWsMessage;

function onAudioProcess( e )
{ if( isRecording ) ws.send( e.inputBuffer.getChannelData( 0 ) ); }

function callback( stream )
{
    console.log( 'starting callback' );
    micSource = context.createMediaStreamSource( stream );
    processor = context.createScriptProcessor( bufferSize, 1, 1 );
    processor.onaudioprocess = onAudioProcess;
    micSource.connect( processor );
    processor.connect( context.destination );
    console.log( 'ending callback' );
}

function error( err ) { alert( "Problem" ); }

navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

navigator.getUserMedia( userMediaConfig, callback, error);

function startRecord()
{
    var message  = 'rate=' + String( context.sampleRate );
    var elements = document.getElementById( "settings" ).elements;
    
    for( var i = 0 ; i < elements.length; ++i )
    {
	elements[i].disabled = true;	
	if( elements[i].checked )
	    message += ',' + elements[i].name + '=' + String( elements[i].value )
    }
    
    ws.send( message );
    isRecording = true;
    document.getElementById( "start" ).innerHTML = "Stop";
    console.log( 'started recording' );
}

function stopRecord()
{
    isRecording  = false;
    var elements = document.getElementById( "settings" ).elements;
    
    for( var i = 0 ; i < elements.length; ++i )
	elements[i].disabled = false;	
    
    document.getElementById( "start" ).innerHTML = "Start";
    ws.send( 'done' );
    console.log( 'ended recording' );
}

function toggleRecord()
{
    if( isRecording )
	stopRecord();
    else
	startRecord();
}
