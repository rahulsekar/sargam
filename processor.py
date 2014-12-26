import numpy as np

#locals
import factory
import destination
from opus.decoder import Decoder as OpusDecoder
#import wave

class Processor :
    
    def __init__( self ) :
        
        self.config = factory.get_cmd_args()
        self.update()

    def update_dtype( self, dtype_str ) :
        
        if dtype_str == 'int16' :
            self.dtype = np.int16
        elif dtype_str == 'float32' :
            self.dtype = np.float32
        else :
            raise NameError( 'unknown dtype: ' + dtype_str )

    def update_decoder( self, op_rate, op_frame_dur, rate ) :

        if op_rate > 0 :
            self.is_encoded = True
            self.decoder = OpusDecoder( op_rate, 1 )
            self.op_frame_size = op_rate * op_frame_dur
            '''
            self.wave_write = wave.open( 'blah.wav', 'wb' );
            self.wave_write.setnchannels( 1 )
            self.wave_write.setsampwidth( 2 )
            self.wave_write.setframerate( rate )
            '''
        else :
            self.is_encoded = False

    def update_rate( self, sampling_rate, freq_base ) :
        
        self.window_size = sampling_rate / freq_base
        self.window_size_by_2 = int( self.window_size / 2.0 ) + 1

    def update( self ) :

        self.inProgress = True
        self.is_encoded = False
        self.debug      = self.config[ 'debug' ]
        self.plot       = self.config[ 'plot' ]
        self.times      = []
        self.finder     = factory.get_finder( self.config )
        self.controller = factory.get_controller( self.config )

        if 'rate' in self.config :
            self.update_rate( self.config[ 'rate' ], self.config[ 'freq_base' ] )

        self.update_dtype( self.config[ 'dtype' ] )

        if 'op_rate' in self.config :
            self.update_decoder( self.config[ 'op_rate' ],
                                 self.config[ 'op_frame_dur' ],
                                 self.config[ 'rate' ] )

        self.buffer = np.array( [], dtype = self.dtype )

        self.dbgScbr = destination.File()
        self.pltScbr = destination.Plot()

    def connect( self, subscriber ) :
        self.subscriber = subscriber

    def process_message( self, message ) :

        parts = message.split( ',' )        
        keys_int = [ 'rate', 'evaluate', 'op_rate', 'op_frame_dur' ]
        keys_str = [ 'lesson', 'tonic', 'dtype' ]

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
            elif key in keys_str : 
                args[ key ] = value # TODO: check value!
            elif key in keys_int :
                args[ key ] = int( value )
            else :
                raise NameError( 'unknown message key: %s' % key )
        
        self.config.update( args )
        self.update()
        
        self.subscriber.write_message( self.controller.initialize() )

    def consume_audio( self, data, t ) :
                              
        if self.is_encoded :
            pcm = self.decoder.decode( data, self.op_frame_size, False )
            self.consume_audio_np_array(
                np.frombuffer( pcm, dtype = np.int16 ), t )
#            self.wave_write.writeframes( pcm )
        else :
            self.consume_audio_np_array( 
                np.frombuffer( data, dtype = self.dtype ), t )

    def consume_audio_np_array( self, data, t ) :

        self.times.append( t )

        self.buffer = np.append( self.buffer, data )

        if len( self.buffer ) >= self.window_size :
            ( RES, pcs, val ) = self.finder.find(
                self.buffer[ - self.window_size :  ],
                ret_pcs = self.debug or self.plot )
            
            out = self.controller.process_tone( RES, pcs, val )

            self.subscriber.write_message( out )

            self.buffer = self.buffer[ - self.window_size_by_2  : ]
            
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
