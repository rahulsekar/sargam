import sys
import time
import difflib
import numpy as np
#locals
import lessons
import plotter
import sound

class Controller :
    
    def initialize( self ) :
        
        self.carnatic_map = dict()

        if self.carnatic_tonic != '' :
            notes = sound.notes()
            idx   = notes.index( self.carnatic_tonic )
            if idx > 0 and idx < len( notes ):
                notes = notes[ idx : ] + notes[ 0 : idx ]
            self.carnatic_map = dict( zip( notes, sound.swaras() ) )
            self.carnatic_map[ '-' ] = '-';
            
        if self.lesson_name in lessons.get_lessons() :
            self.lesson = lessons.get_lessons()[ self.lesson_name ]
        else :
            self.lesson = 'N/A'
            
        if '' == self.carnatic_tonic and self.lesson != 'N/A' :
            raise NameError( 'Lesson %s needs carnatic_tonic' % lesson_name )
        return ','.join( [ 'l=%s' % self.lesson, 'e' ] )

    def __init__( self, lesson_name, carnatic_tonic, evaluate ) :
        
        self.carnatic_tonic = carnatic_tonic
        self.evaluate       = evaluate
        self.lesson_name    = lesson_name
        self.res            = ''

    def process_tone( self, res, pcs, val ) :        
        
        if len( self.carnatic_map ) :
            r = self.carnatic_map[ res ]
        else :
            r = res;
            
        if self.evaluate :
            self.res += r
        
        return 'r=%s' % r
            
    def done( self ) :

        if self.evaluate :
            score = lessons.distance( self.lesson, self.res );
            return ','.join( [ 'r=-',
                            's=%.2f' % ( score ) ] )
        else :
            return 'r=-'
