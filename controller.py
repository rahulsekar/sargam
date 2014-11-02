import sys
import time
import difflib
import numpy as np
#locals
import lessons
import plotter

class Controller_Base :
    
    def process_tone( self, res, pcs, val ) :
        raise NameError( 'process_tone not implemented' )

    def done( self ) :
        return '\n'
        
    def initialize( self ) :
        return ''

class Freestyle( Controller_Base ) :

    def initialize( self ) :
        return ','.join( [ 'r=-',
                           'm=Practice makes perfect!',
                           'l=N/A',
                           's=N/A'] )
    def process_tone( self, res, pcs, val ) :
        return 'r=%s' % res

class Learn( Controller_Base ) :
    
    def __init__( self, lesson_name, carnatic_tonic ) :

        self.name    = lesson_name
        self.content = lessons.get_lessons()[ lesson_name ]
        self.idx     = -1 #not in progress
        if '' == carnatic_tonic :
            raise NameError( 'Lesson %s needs carnatic_tonic' % lesson_name )

    def initialize( self ) :
        
        self.idx = 0
        return( ','.join( [ 'r=-',
                            'l=%s' % self.content,
                            'n=0',
                            'm=%s' % self.name,
                            's=N/A' ] ) )

    def process_tone( self, res, pcs, val ) :
        
        if self.idx >= 0 and res == self.content[ self.idx ] :
            
            self.idx += 1
            if self.idx == len( self.content ) :
                return self.done()
            else :
                return ','.join( [ 'r=%s' % res, 'n=%d' % self.idx ] );

        return 'r=%s' % res

    def done( self ) :

        if self.idx == len( self.content ) :
            m = 'Lesson complete!'
        else :
            m = 'Lesson stopped.'

        ret = ( ','.join( [ 'd', 'm=%s' % m,
                            'n=%s' % self.idx ] ) )

        self.idx = -1
        
        return ret

            
class Evaluate( Controller_Base ) :
    
    def __init__( self, lesson_name, carnatic_tonic ) :
        
        self.name    = lesson_name
        self.content = lessons.get_lessons()[ lesson_name ]
        if carnatic_tonic == '' :
            raise NameError( 'Lesson %s needs carnatic_tonic.' % lesson_name )

    def initialize( self ) :
        return ','.join( [ 'r=-',
                           'm=Evaluation',
                           'l=%s' % self.content,
                           's=N/A' ] )
    def process_tone( self, res, pcs, val ) :
        
        self.res += res
        return ','.join( [ 'r=%s' % res ] )

    def done( self ) :

        score = lessons.distance( self.content, self.res );
        return ','.join( [ 'r=-',
                           's=%.2f' % ( score ) ] )
