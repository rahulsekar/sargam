var WSHandler = new WebSocket( "ws://" + window.location.href.split( '/' )[2] + "/ws" );

var AudioHandler = {

    bufferSize : 4096,
    downSample : 2,
    int16Buffer : null,
    
    onAudioProcess : function( e )
    {
	if( isRecording )
	{
	    var data = e.inputBuffer.getChannelData( 0 );
	    var i = 0, ds = AudioHandler.downSample;
	    for( var idx = 0; idx < data.length; idx += ds )
		AudioHandler.int16Buffer[ i++ ] = data[ idx ] * 0xFFFF
	    WSHandler.send( AudioHandler.int16Buffer );
	}
    },
    
    init : function()
    {
	this.int16Buffer = new Int16Array( this.bufferSize / this.downSample );
    }
}

var MediaHandler = {

    context : new (window.AudioContext||window.webkitAudioContext)(),
    micSource : null,
    processor : null,
    userMediaConfig : {
	"audio": {
	    "mandatory": { 
		"googEchoCancellation": "false",
		"googAutoGainControl": "false",
		"googNoiseSuppression": "false",
		"googHighpassFilter": "false"
	    },
	    "optional": []
	}
    },
    
    callback : function( stream )
    {
	console.log( 'starting callback' );
	MediaHandler.micSource = MediaHandler.context.createMediaStreamSource( stream );
	MediaHandler.processor = MediaHandler.context.createScriptProcessor( AudioHandler.bufferSize, 1, 1 );
	MediaHandler.processor.onaudioprocess = AudioHandler.onAudioProcess;
	MediaHandler.micSource.connect( MediaHandler.processor );
	MediaHandler.processor.connect( MediaHandler.context.destination );
	console.log( 'ending callback' );
    },
    
    error : function( err ) { alert( "Problem" ); },
    
    init : function()
    {
	if( !this.context.createScriptProcessor )
	    this.context.createScriptProcessor = this.context.createJavaScriptNode;
	//initialize mic
	navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
	
	navigator.getUserMedia( this.userMediaConfig, this.callback, this.error );
    },	
}
