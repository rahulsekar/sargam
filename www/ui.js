var lessonPane = function( lesson, timed ) 
{
    var title_html = '<h2>Lesson Name: ' + lesson.name + ' </h2><br>';
    var score_html = '<h2 id="score">Score: </h2>';
    var sheet_html = '<div class="sheetPane">';
    var template = '<div class="square" id="tl_{id}">{swara}{res}</div>';
    var i = 0;
    var max_cols = lesson.thala;
    for( i = 0; i < lesson.swara.length; ++i )
    {
	if( i % max_cols == 0 )
	{
	    if( i > 0 )
		sheet_html += '</div>';
	    
	    sheet_html += '<div class="sheetRow">';
	}
	
	var elem = template.replace( '{id}', String(i) );
	elem = elem.replace( '{swara}', lesson.swara[i] );
	if( timed )
	{
	    elem = elem.replace( '{res}', '<div id="tlr_{id}"></div>' );
	    elem = elem.replace( '{id}', String(i) );
	}
	else
	    elem = elem.replace( '{res}', '' );

	sheet_html += elem;
    }

    if( i > 0 )
	sheet_html += '</div>';

    sheet_html += '</div>';

    if( timed == false )
	sheet_html += '<div id="res"></div>'

    var lp = document.getElementById( "lower_pane" );
    lp.innerHTML = title_html + sheet_html + score_html;
    this.current_index = -1;
    this.timed = timed;
}

lessonPane.prototype.updateResult = function( res )
{
    var id = 'res';
    if( this.timed )
	id = 'tlr_' + String( this.current_index );
    document.getElementById( id ).innerHTML += res;
}

lessonPane.prototype.setColor = function( idx, color )
{
    if( idx >= 0 )
    {
	var id = 'tl_' + String( idx );
	document.getElementById( id ).style.backgroundColor = color;
    }
}

lessonPane.prototype.startLesson = function()
{
    this.current_index = 0;
    this.setColor( this.current_index, 'aqua' );
}

lessonPane.prototype.updateLesson = function()
{
    this.setColor( this.current_index++, 'yellow' );
    this.setColor( this.current_index, 'aqua' );
}

lessonPane.prototype.endLesson = function()
{
    this.setColor( this.current_index, 'yellow' );
    this.current_index = -1;
}

lessonPane.prototype.setScore = function( score )
{
    document.getElementById( "score" ).innerHTML += score;
}

var freestylePane = function()
{
    var lp = document.getElementById( 'lower_pane' );
    lp.innerHTML = '<div id="res"></div>';
}

freestylePane.prototype.updateResult = function( res )
{
    document.getElementById( 'res' ).innerHTML += res;
}

var UI = {

    lower_pane : null,

    showMessage : function( message )
    {
	document.getElementById( "message" ).innerHTML = message;
    },
    
    setLessonOptions : function( lessons )
    {
	var select = document.getElementById( "lessonSelect" );
	for( var i = 0; i < lessons.length; ++i )
	{
	    select.options[ select.options.length ] =
		new Option( lessons[i].name, lessons[i].name );
	}
    },
    
    getSettings : function( key )
    {
	var elements = document.getElementById( "settings" ).elements
	for( var i = 0; i < elements.length; ++i )
	    if( elements[i].name == key )
		return elements[i].value;
	return '';
    },

    disableSettings : function()
    {
	var elements = document.getElementById( "settings" ).elements;
	for( var i = 0 ; i < elements.length; ++i )
	    elements[i].disabled = true;	
    },
    
    enableSettings : function()
    {
	var elements = document.getElementById( "settings" ).elements;
	for( var i = 0 ; i < elements.length; ++i )
	    elements[i].disabled = false;
    }
}
