import numpy as np

#locals
import factory
import destination

class Processor :
    
    def __init__( self ) :
        
        self.config = factory.get_cmd_args()
        self.update()

    def update( self ) :

        self.inProgress = True
        self.debug      = self.config[ 'debug' ]
        self.plot       = self.config[ 'plot' ]
        self.times      = []
        self.finder     = factory.get_finder( self.config )
        self.controller = factory.get_controller(
            lesson = self.config[ 'lesson' ],
            carnatic_tonic = self.config[ 'carnatic_tonic' ],
            evaluate = self.config[ 'evaluate' ] )

        if 'rate' in self.config :
            self.windowSize    = self.config[ 'rate' ] / self.config[ 'freq_base' ]
            self.windowSizeBy2 = int( self.windowSize / 2.0 ) + 1

        if self.config[ 'dtype' ] == 'int16' :
            self.dtype = np.int16
        elif self.config[ 'dtype' ] == 'float32' :
            self.dtype = np.float32
        else :
            raise NameError( 'unknown dtype: %s' % self.config[ 'dtype' ] )

        self.buffer = np.array( [], dtype = self.dtype )

        self.dbgScbr = destination.File()
        self.pltScbr = destination.Plot()

    def connect( self, subscriber ) :
        self.subscriber = subscriber

    def process_message( self, message ) :
        parts = message.split( ',' )
        
        args = {}
        for part in parts :

            subparts = part.split( '=' )
            if len( subparts ) > 2 :
                raise NameError( 'unknown message part: %s' % part )

            key = subparts[ 0 ]
            if len( subparts ) == 2 :
                value = subparts[ 1 ]
            
            if 'done' == key :
                if self.inProgress :
                    self.done()
                return

            if key in [ 'debug', 'plot', 'chords' ] :
                args[ key ] = True
            elif key in [ 'lesson', 'carnatic_tonic', 'dtype' ] : 
                args[ key ] = value # TODO: check value!
            elif key in [ 'rate', 'evaluate' ] :
                args[ key ] = int( value )
            else :
                raise NameError( 'unknown message key: %s' % key )
        
        self.config.update( args )
        self.update()
        
        self.subscriber.write_message( self.controller.initialize() )

    def consume_audio( self, data, t ) :
        self.consume_audio_np_array(
            np.frombuffer( data, dtype = self.dtype ), t )

    def consume_audio_np_array( self, data, t ) :

        self.times.append( t )

        self.buffer = np.append( self.buffer, data )

        if len( self.buffer ) >= self.windowSize :
            ( RES, pcs, val ) = self.finder.find(
                self.buffer[ - self.windowSize :  ],
                ret_pcs = self.debug or self.plot )
            
            out = self.controller.process_tone( RES, pcs, val )

            self.subscriber.write_message( out )

            self.buffer = self.buffer[ - self.windowSizeBy2  : ]
            
            if self.debug :
                self.dbgScbr.write_message( '\n'
                    + np.array_str( np.transpose( pcs ), precision = 1 )
                    + '\n' )

            if self.plot :
                self.pltScbr.write_message( pcs, t )

    def done( self ) :

        self.inProgress = False
        self.subscriber.write_message( self.controller.done() )

        if self.debug :
            self.dbgScbr.done()

        if self.plot :
            self.pltScbr.done()
