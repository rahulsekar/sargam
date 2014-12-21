import sys
from scipy.io import wavfile
import numpy as np
#import pyaudio
import time
import math

import tornado.websocket

class SourceBase :

    def __init__( self ) :
        self.rate = 0

    def connect( self, subscriber, bufferRate ) :
        self.subscriber = subscriber
        self.bufferRate = bufferRate

    def start( self ) :
        return

    def is_running( self ) :
        return False

    def stop ( self ) :
        return

class Wavfile( SourceBase ) :

    def __init__( self, infile, channel = 1 ) :

        self.file_rate, data = wavfile.read( infile )
        if len( data.shape ) > 1 :
            self.data = data[ : , channel - 1 ]
        else :
            self.data = data

    def start( self ) :

        self.subscriber.process_message( 'rate=%d' % self.file_rate )
        bufferSize = self.file_rate / self.bufferRate
        idx        = 0
        n          = len( self.data )
        while idx < n :
            self.subscriber.consume_audio_np_array(
                self.data[ idx : idx + bufferSize ], time.time() )
            idx += bufferSize

    def stop( self ) :

        self.subscriber.process_message( 'done' )

class Mic( SourceBase ) :
    
    def __init__( self, micrate ) :
        self.micrate = micrate

    def connect( self, subscriber, bufferRate ) :

        SourceBase.connect( self, subscriber, bufferRate )
        self.isRunning  = False
        self._stop      = False

    def is_running( self ) :
        return self.isRunning
    
    def start( self ) :
        p   = pyaudio.PyAudio()
        self.stream = p.open(
            format = pyaudio.paInt16,
            channels = 1,
            rate     = self.micrate,
            input    = True,
            stream_callback   = self.callback_mic,
            frames_per_buffer = int( self.micrate / self.bufferRate ) )

        self.subscriber.process_message(
            'dtype=int16,rate=%d' % self.micrate )
        self.stream.start_stream()
        self.isRunning = True

        input() # keep open

    def stop( self ) :
        self._stop = True
        input() # one more time

    def callback_mic( self, data, frame_count, time_info, status ) :

        self.subscriber.consume_audio( data, time.time() )

        if self._stop :
            self._stop     = False
            self.isRunning = False
            self.subscriber.process_message( 'done' )

            return( '', pyaudio.paComplete )
        
        return ( '', pyaudio.paContinue )
            
    def is_running( self ) :
        return ( self._stop == False )

#source AND destination :(
class WebSocket( tornado.websocket.WebSocketHandler ):
    
    def open( self ):
        print( 'new connection' )
        self.write_message( '' )
      
    def initialize( self, subscriber ) :
        
        self.subscriber = subscriber 
        self.subscriber.connect( self ) #output!

    def on_message( self, data ) :
        if len( data ) < 1000 :
            self.subscriber.process_message( data )
        else : 
           self.subscriber.consume_audio( data, time.time() )

    def on_close(self):
      print( 'connection closed' )
