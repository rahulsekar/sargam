class Speaker :

    def __init__( self, output_rate, frame_rate ) :

        self.buffer      = ''
        self.output_rate = output_rate
        self.frame_rate  = frame_rate

    def callback_speaker( self, data, time_count, time_info, status ) :
        if self._stop :
            return( '', pyaudio.paComplete )

        return( self.buffer, pyaudio.paContinue )

    def set_frequency( self, frequency ) :
        
        data = [ int( math.sin( ( i * frequency * math.pi * 2.0 ) / self.output_rate ) * 127 ) for i in range( int( self.output_rate / self.frame_rate ) ) ]
        self.buffer = np.array( data, dtype = np.int8 ).tostring()

    def run( self ) :
        p = pyaudio.PyAudio()
        fpb = int( self.output_rate / self.frame_rate )
        stream = p.open( format = pyaudio.paInt8,
                         channels = 1,
                         output   = True,
                         rate = self.output_rate,
                         stream_callback = self.callback_speaker,
                         frames_per_buffer = fpb )
        self._stop = False
        stream.start_stream()
        signal.signal( signal.SIGINT, self.stop )

    def stop( self, signal = 0, frame = 0 ) :
        self._stop = True

    def is_running( self ) :
        return ( self._stop == False )

