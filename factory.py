import argparse
#locals
import source
import finder
import controller

def get_cmd_args() :
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument( '--debug', help = 'Turn on debug mode',
                         action = 'store_true' )
    parser.add_argument( '--plot', help = 'Plot stuff',
                         action = 'store_true' )

    #input mode
    parser.add_argument( '--mode', help = 'mic, file or web',
                         type = str,
                         choices = [ 'mic', 'file', 'web' ] )

    parser.add_argument( '--micrate',
                         help = 'Rate to sample mic if mode is mic',
                         default = '22050', type = int )
    parser.add_argument( '--dtype',
                         help = 'dtype for sampling. int16 or float32',
                         default = 'int16', type = str )

    #input from wav file
    parser.add_argument( '--infile', help = 'File to process',
                         default = '' )
#    parser.add_argument( '--channel',
#                         help = 'Channel number. 0 will diff.',
#                         default = 0, type = int )

    #other options
    parser.add_argument( '--freq_base',
                         help = 'Hz. Base frequency for fft',
                         default = 5, type = int )
    parser.add_argument( '--pitch_start', help = 'Hz. value of A3',
                         default = 220, type = float )
    parser.add_argument( '--amp_lb',
                         help = 'Amplitude lower bound w.r.t max',
                         default = 0.2, type = float )
    parser.add_argument( '--n_octaves', help = 'Number of octaves',
                         default = 3, type = int )
    parser.add_argument( '--oct_wt_ratio',
                         help = 'Rel. wt of higher octaves',
                         default = 1.3, type = float )
    parser.add_argument( '--chords', help = 'Identify chords.',
                         action = 'store_true' )
    parser.add_argument( '--use_fft', help = 'Use fft instead of dct',
                         action = 'store_true' )
    parser.add_argument( '--carnatic_tonic',
                         help = 'Carnatic tonic (shadhjam)',
                         default = '', type = str )
    parser.add_argument( '--lesson', help = 'Lesson Name',
                         default = '', type = str )
    parser.add_argument( '--evaluate',
                         help = 'Evaluate on lesson. Needs --lesson.',
                        action = 'store_true' )
    #output
    parser.add_argument( '-o', '--outfile',
                         help = 'Output file. Default is stdout.',
                         default = '', type = str )

    return vars( parser.parse_args() )

def get_finder( args ) :

    if args[ 'chords' ] :
        ret = finder.Chord( pitch_start  = args['pitch_start'],
                            freq_base    = args['freq_base'],
                            amp_lb       = args['amp_lb'],
                            oct_wt_ratio = args['oct_wt_ratio'],
                            n_octaves    = args['n_octaves'],
                            use_fft      = args['use_fft'] )
    else :
        ret = finder.Note( pitch_start    = args['pitch_start'],
                           freq_base      = args['freq_base'],
                           amp_lb         = args['amp_lb'],
                           oct_wt_ratio   = args['oct_wt_ratio'],
                           n_octaves      = args['n_octaves'],
                           use_fft        = args['use_fft'] )
                           
    return ret
    
def get_source( mode, infile, micrate ) :
    
    if 'mic' == mode :
        ret = source.Mic( micrate )

    elif 'file' == mode :
        ret = source.Wavfile( infile )

    elif 'web' == mode :
        ret = source.WebSocket # return the class, not the object

    else :
        raise NameError( 'Unknown mode: %s' % mode )

    return ret

def get_controller( lesson, carnatic_tonic, evaluate ) :

    if lesson == '' :
        if evaluate :
            raise NameError( 'No --lesson to evaluate on.' )
        ret = controller.Controller( '', carnatic_tonic, False )
    else :
        ret = controller.Controller( lesson, carnatic_tonic, evaluate )
        
    return ret

