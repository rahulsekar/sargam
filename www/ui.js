var UI = {
    
    res_row : null,
    res_col : null,
    res_max_cols : null,
    res_row_elem : null,
    
    lesson_table : document.getElementById( "lessonSheet" ),
    result_table : document.getElementById( "resultSheet" ),

    showMessage : function( message )
    {
	document.getElementById( "message" ).innerHTML = message;
    },
    
    setScore : function( scoreHTML )
    {
	document.getElementById( "score" ).innerHTML = scoreHTML;
    },
    
    setLesson : function( lesson )
    {
	document.getElementById( "lessonName" ).innerHTML = lesson.name;
	if( lesson.name == "N/A" )
	{
	    this.res_max_cols = 20;
	    this.res_col = this.res_max_cols;
	    return;
	}
	
	var max_cols = lesson.thala;
	this.res_col = this.res_max_cols = max_cols;

	var col = max_cols, row = 0;
	
	for( var i = 0; i < lesson.swara.length; ++i )
	{
	    if( col == max_cols )
	    {
		var row_elem = this.lesson_table.insertRow( row++ );
		col = 0;
	    }
	    var cell = row_elem.insertCell( col++ );
	    cell.innerHTML = lesson.swara[i];
	}
    },
    
    updateResult : function( res )
    {
	if( this.res_col == this.res_max_cols )
	{
	    this.res_row_elem = this.result_table.insertRow( this.res_row++ );
	    this.res_col = 0;
	}
	
	var cell = this.res_row_elem.insertCell( this.res_col++ );
	cell.innerHTML = res;
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
    },

    clean : function()
    {
	while( this.result_table.rows.length ) 
	    this.result_table.deleteRow( 0 );

	this.res_col = this.res_row = 0;

	while( this.lesson_table.rows.length )
	    this.lesson_table.deleteRow( 0 );

	this.setScore( "N/A" );
	this.setLesson( {"name":"N/A"} );
    },
}
