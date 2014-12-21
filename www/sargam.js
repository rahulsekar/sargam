var base_url    = window.location.href.split( '/' )[2];
var isRecording = false, isPractising = false;
var ws          = null;

var bufferSize  = 4096;
var downSample  = 2;
var int16Buffer  = new Int16Array( bufferSize / downSample );

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

var lesson = null, lessonidx = -1, isFreestyle = true;
var interval = null, isUntimed = true;
var firstSpeed = 2000; // msec

var context   = new (window.AudioContext||window.webkitAudioContext)();
var micSource = null;
var processor = null;

var sheet_row=0, sheet_col=20, sheet_max_cols=20;
var table = document.getElementById( "sheet" );

if( !context.createScriptProcessor )
    context.createScriptProcessor = context.createJavaScriptNode;

function showMessage( message )
{
    document.getElementById( "message" ).innerHTML = message;
}

function setScore( scoreHTML )
{
    document.getElementById( "score" ).innerHTML = scoreHTML;
}

function setLesson( lessonHTML )
{
    document.getElementById( "lesson" ).innerHTML = lessonHTML;
}

function startRecord()
{
    isRecording = true;
    showMessage( 'In Progress' );
    console.log( 'started recording' );
}

function stopRecord()
{
    isRecording  = false;
    console.log( 'ended recording' );    
}

function getSettings( key )
{
    var elements = document.getElementById( "settings" ).elements
    for( var i = 0; i < elements.length; ++i )
	if( elements[i].name == key )
	    return elements[i].value;
    return '';
}

function disableSettings()
{
    var elements = document.getElementById( "settings" ).elements;
    for( var i = 0 ; i < elements.length; ++i )
	elements[i].disabled = true;	
}

function enableSettings()
{
    var elements = document.getElementById( "settings" ).elements;
    for( var i = 0 ; i < elements.length; ++i )
	elements[i].disabled = false;
}

function sendSettings()
{
    var message = 'rate=' + String( context.sampleRate / downSample );
    var keys    = [ 'carnatic_tonic', 'lesson' ];
    
    for( var i = 0; i < keys.length; ++i )
	message += ',' + keys[ i ] + '=' + getSettings( keys[ i ] );

    if( getSettings( 'speed' ) != '' )
	message += ',evaluate=1';
    else
	message += ',evaluate=0';

    console.log( message );
    ws.send( message );
}

function updateLesson()
{
    lessonidx++;

    var elem = document.getElementById( 'lesson' );
    var done = lesson.substring( 0, lessonidx );
    var exp  = '', yet = '';
    
    var lessonHTML = "<font color=\"green\">" + done + "</font>";

    if( lessonidx == lesson.length )
    {
	setLesson( lessonHTML );
	stopPractice();
	showMessage( 'Lesson Completed!' );
    }
    else
    {
	exp = lesson[ lessonidx ]
	yet = lesson.substring( lessonidx + 1 );
	lessonHTML += "<font color=\"red\">" + exp + "</font>";
	lessonHTML += "<font color=\"black\">" + yet + "</font>";
	setLesson( lessonHTML );
    }
}

function updateSheet( res )
{
    if( sheet_col == sheet_max_cols )
    {
	row = table.insertRow( sheet_row++ );
	sheet_col = 0
    }

    var cell = row.insertCell( sheet_col++ );
    cell.innerHTML = res;
}

function cleanSheet()
{
    while( table.rows.length ) 
	table.deleteRow( 0 );
    sheet_col = sheet_max_cols;
    sheet_row = 0;
    setScore( "N/A" );
    setLesson( "N/A" );
}

function processResult( res )
{
    if( isFreestyle )
	updateSheet( res );
    else 
    {
	if( lesson[ lessonidx ] == res )
	    resHTML = "<font color=\"green\">" + res + "</font>";
	else
	    resHTML = "<font color=\"red\">" + res + "</font>";
	
	updateSheet( resHTML );
	
	if( isUntimed && lesson[ lessonidx ] == res )
	    updateLesson();
    }
}

function serverReady()
{
    isUntimed   = false;
    isFreestyle = true;
    
    if( getSettings( 'lesson' ) != '' )
    {
	lessonidx   = -1;
	isFreestyle = false
	updateLesson();

        switch( getSettings( 'speed' ) )
	{
	case "1":
	    interval = setInterval( updateLesson, firstSpeed )
	    break;
	case "2" :
	    interval = setInterval( updateLesson, firstSpeed / 2.0 );
	    break;
	case "3" :
	    interval = setInterval( updateLesson, firstSpeed / 4.0 );
	    break;
	case "" :
	    isUntimed = true;
	}
    }
    startRecord();
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
	    processResult( keyval[1] );
	    break;
	case 'b' : // bufferRate
	    bufferSize = context.sampleRate / parseInt( keyval[1] )
	case 'l' : // lesson
	    lesson = keyval[1]
	    break;
	case 's' : // score
	    setScore( keyval[1] );
	    break;
	case 'm' : // message
	    showMessage( keyval[1] );
	    break;
	case 'e' : // server ready
	    serverReady();
	    break;
	}
    }
}

ws           = new WebSocket( "ws://" + base_url + "/ws" );
ws.onopen    = function(){};
ws.onmessage = onWsMessage;

function onAudioProcess( e )
{
    if( isRecording )
    {
	var data = e.inputBuffer.getChannelData( 0 );
	var i = 0;
	for( var idx = 0; idx < data.length; idx += downSample )
	    int16Buffer[ i++ ] = data[ idx ] * 0xFFFF
	ws.send( int16Buffer );
    }
}

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

function startPractice()
{
    isPractising = true;
    disableSettings();
    sendSettings();
    cleanSheet();
    showMessage( 'Waiting for server' );
    document.getElementById( 'practice' ).innerHTML = 'Stop';
    console.log( 'started practice' );
}

function stopPractice()
{
    stopRecord();
    if( !isUntimed )
	clearInterval( interval );
    ws.send( 'done' );
    isPractising = false;
    console.log( "ended practice" );
    showMessage( "Stopped" );
    document.getElementById( "practice" ).innerHTML = "Start";
    enableSettings();
}

function togglePractice()
{
    if( isPractising )
	stopPractice();
    else
	startPractice();
}
