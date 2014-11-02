import sys

#locals
import plotter

class Destination_Base :

    def write_message( self ) :
        raise NameError( 'write_message not implemented' )
    def done( self ) :
        return

class File( Destination_Base ) :

    def __init__( self, filename = '' ) :
        
        if filename == '' :
            self.outfile = sys.stdout
        else :
            self.outfile = open( filename, 'w' )

    def write_message( self, message ) :
        self.outfile.write( message )
        self.outfile.flush()

class Plot :
    
    def __init__( self ) :
        self.pcss  = []
        self.times = []
        
    def write_message( self, pcs, t ) :
        self.pcss.append( pcs )
        self.times.append( t )
        
    def done( self ) :
        plotter.plot( self.pcss, self.times )
