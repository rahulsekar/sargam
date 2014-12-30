var isRecording = false, isPractising = false;

var wsh = new WebSocket( 'ws://' + window.location.href.split( '/' )[2] + '/ws' );
wsh.onmessage = onWsMessage;
var ap = new OpusEncoderProcessor( wsh );
var mh = new MediaHandler( ap );

var current_lesson = null, lessonidx = null;
var isFreestyle = true, lessons = null;
var interval = null, isTimedLesson = null;
var firstSpeed = 2000; // msec

startRecord = function()
{
    isRecording = true;
    UI.showMessage( 'In Progress' );
    console.log( 'started recording' );
}

stopRecord = function()
{
    isRecording  = false;
    console.log( 'ended recording' );    
}

sendSettings = function()
{
    var r = 'rate=' + String( mh.context.sampleRate / ap.downSample );
    var t = 'tonic=' + UI.getSettings( 'tonic' );
    var l = 'lesson=' + UI.getSettings( 'lesson' );
    var e = 'evaluate=';

    if( UI.getSettings( 'speed' ) != '' )
	e += '1';
    else
	e += '0';

    var msgArr = [ r, t, l, e ]
    if( UI.getSettings( 'encode' ) == 1 )
    {
	var o = 'op_rate=' + String( ap.opusRate );
	var f = 'op_frame_dur=' + String( ap.opusFrameDur );
	msgArr.push( o )
	msgArr.push( f );
	encode = true;
    }
    else
	encode = false;

    var message = 'msg:' + msgArr.join( ',' );

    console.log( message );
    wsh.send( message );
}

loadLessons = function()
{
    var xmlhttp = null;
    xmlhttp = new XMLHttpRequest();
    xmlhttp.open( 'GET', 'lessons.json', false );
    xmlhttp.send();
    lessons = JSON.parse( xmlhttp.responseText ).lessons;
    UI.setLessonOptions( lessons );
}

onSettingsChange = function()
{
    var lesson_name = UI.getSettings( 'lesson' );
    var timed = ( UI.getSettings( 'speed' ) > 0 );

    if( lesson_name != '' )
    {
	for( var i = 0; i < lessons.length; ++i )
	    if( lessons[i].name == lesson_name )
	{
	    UI.lower_pane = new lessonPane( lessons[i], timed );
	    current_lesson = lessons[i].swara;
	    isFreestyle = false;
	    break;
	}

	if( i == lessons.length )
	    alert( 'unknown lesson: ' + lesson_name );
    }	
    else
    {
	UI.lower_pane = new freestylePane();
	isFreestyle = true;
	current_lesson = '';
    }

    if( timed && isFreestyle == 0 )
	isTimedLesson = true;
    else
	isTimedLesson = false;
}

function updateLesson()
{
    lessonidx++;
    
    if( lessonidx == current_lesson.length )
    {
	stopPractice();
	UI.lower_pane.endLesson();
	UI.showMessage( 'Lesson Completed!' );
	
    }
    else
        UI.lower_pane.updateLesson();
}

function processResult( res )
{
    if( isFreestyle )
	UI.lower_pane.updateResult( res );
    else 
    {
	if( current_lesson[ lessonidx ] == res )
	    resHTML = '<font color="green">' + res + '</font>';
	else
	    resHTML = '<font color="red">' + res + '</font>';
	
	UI.lower_pane.updateResult( resHTML );
	
	if( !isTimedLesson && current_lesson[ lessonidx ] == res )
	    updateLesson();
    }
}

function serverReady()
{
    if( isTimedLesson )
        switch( UI.getSettings( 'speed' ) )
    {
    case '1':
	interval = setInterval( updateLesson, firstSpeed )
	break;
    case '2' :
	interval = setInterval( updateLesson, firstSpeed / 2.0 );
	break;
    case '3' :
	interval = setInterval( updateLesson, firstSpeed / 4.0 );
	break;
    case '' :
	break;
    default :
	alert( 'unknown speed' );
    }

    if( !isFreestyle ) 
    {
	UI.lower_pane.startLesson();
	lessonidx = 0 ;
    }

    startRecord();
}

function onWsMessage( evt )
{
    parts = evt.data.split( ',' )
    
    for( var i = 0; i < parts.length; ++i )
    {
	var keyval = parts[ i ].split( '=' )
	var key = keyval[0]
	switch( key )
	{
	case 'r' : // result
	    processResult( keyval[1] );
	    break;
	case 's' : // score
	    UI.lower_pane.setScore( keyval[1] );
	    break;
	case 'm' : // message
	    UI.showMessage( keyval[1] );
	    break;
	case 'e' : // server ready
	    serverReady();
	    break;
	case '' : // nothing to do
	    break;
	default :
	    alert( 'Unknown message key from server: ' + key );
	}
    }
}

function startPractice()
{
    isPractising = true;
    UI.disableSettings();
    onSettingsChange();
    sendSettings();
    UI.showMessage( 'Waiting for server' );
    document.getElementById( 'practice' ).innerHTML = 'Stop';
    console.log( 'started practice' );
}

function stopPractice()
{
    stopRecord();
    if( isTimedLesson )
	clearInterval( interval );
    wsh.send( 'msg:done' );
    isPractising = false;
    console.log( 'ended practice' );
    UI.showMessage( 'Stopped' );
    document.getElementById( 'practice' ).innerHTML = 'Start';
    UI.enableSettings();
}

function togglePractice()
{
    if( isPractising )
	stopPractice();
    else
	startPractice();
}

loadLessons();

