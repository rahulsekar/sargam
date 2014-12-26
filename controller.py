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

        if self.tonic != '' :
            notes = sound.notes()
            idx   = notes.index( self.tonic )
            if idx > 0 and idx < len( notes ):
                notes = notes[ idx : ] + notes[ 0 : idx ]
            self.carnatic_map = dict( zip( notes, sound.swaras() ) )
            self.carnatic_map[ '-' ] = '-';
            
        if '' == self.tonic and '' != self.lesson :
            return 'm=Tonic needed for %s' % self.lesson

        return 'e' # server ready

    def __init__( self, tonic, lesson, evaluate ) :
        
        self.tonic    = tonic
        self.evaluate = evaluate
        self.lesson   = lesson
        self.res      = ''

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
            score = lessons.distance(
                lessons.get_lesson( self.lesson ),
                self.res );
            return ','.join( [ 's=%.2f' % ( score ) ] )
        else :
            return ''
