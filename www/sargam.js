var isRecording = false, isPractising = false;
var ws          = null;

var current_lesson = null, lessonidx = null;
var  isFreestyle = true, lessons = null;
var interval = null, isUntimed = true;
var firstSpeed = 2000; // msec

function startRecord()
{
    isRecording = true;
    UI.showMessage( 'In Progress' );
    console.log( 'started recording' );
}

function stopRecord()
{
    isRecording  = false;
    console.log( 'ended recording' );    
}

function sendSettings()
{
    var message = 'rate=' + String( MediaHandler.context.sampleRate / AudioHandler.downSample );
    var keys    = [ 'tonic', 'lesson' ];
    
    for( var i = 0; i < keys.length; ++i )
	message += ',' + keys[ i ] + '=' + UI.getSettings( keys[ i ] );

    if( UI.getSettings( 'speed' ) != '' )
	message += ',evaluate=1';
    else
	message += ',evaluate=0';

    console.log( message );
    WSHandler.send( message );
}

function loadLessons()
{
    var xmlhttp = null;
    xmlhttp = new XMLHttpRequest();
    xmlhttp.open( "GET", "lessons.json", false );
    xmlhttp.send();
    lessons = JSON.parse( xmlhttp.responseText ).lessons;
    UI.setLessonOptions( lessons );
}

function changeLesson( lesson_name )
{
    UI.clean();
    if( lesson_name.length && lessons.length )
	for( var i = 0; i < lessons.length; ++i )
	    if( lessons[i].name == lesson_name )
    {
	current_lesson = lessons[i].swara;
	UI.setLesson( lessons[i] );
    }
}	

function updateLesson()
{
    lessonidx++;
    
//    var done = current_lesson.substring( 0, lessonidx );
//    var exp  = '', yet = '';
    
    if( lessonidx == current_lesson.length )
    {
	stopPractice();
	UI.showMessage( 'Lesson Completed!' );
    }
/*    else
    {
	exp = lesson[ lessonidx ]
	yet = lesson.substring( lessonidx + 1 );
	lessonHTML += "<font color=\"red\">" + exp + "</font>";
	lessonHTML += "<font color=\"black\">" + yet + "</font>";
    }*/
}

function processResult( res )
{
    if( isFreestyle )
	UI.updateResult( res );
    else 
    {
	if( current_lesson[ lessonidx ] == res )
	    resHTML = "<font color=\"green\">" + res + "</font>";
	else
	    resHTML = "<font color=\"red\">" + res + "</font>";
	
	UI.updateResult( resHTML );
	
	if( isUntimed && current_lesson[ lessonidx ] == res )
	    UI.updateLesson();
    }
}

function serverReady()
{
    isUntimed   = false;
    isFreestyle = true;
    
    if( UI.getSettings( 'lesson' ) != '' )
    {
	lessonidx   = -1;
	isFreestyle = false
	updateLesson();

        switch( UI.getSettings( 'speed' ) )
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
	case 's' : // score
	    UI.setScore( keyval[1] );
	    break;
	case 'm' : // message
	    UI.showMessage( keyval[1] );
	    break;
	case 'e' : // server ready
	    serverReady();
	    break;
	}
    }
}

function startPractice()
{
    isPractising = true;
    UI.disableSettings();
    sendSettings();
    UI.showMessage( 'Waiting for server' );
    document.getElementById( 'practice' ).innerHTML = 'Stop';
    console.log( 'started practice' );
}

function stopPractice()
{
    stopRecord();
    if( !isUntimed )
	clearInterval( interval );
    WSHandler.send( 'done' );
    isPractising = false;
    console.log( "ended practice" );
    UI.showMessage( "Stopped" );
    document.getElementById( "practice" ).innerHTML = "Start";
    UI.enableSettings();
}

function togglePractice()
{
    if( isPractising )
	stopPractice();
    else
	startPractice();
}

WSHandler.onmessage = onWsMessage;
MediaHandler.init();
AudioHandler.init();
loadLessons();
UI.clean();
