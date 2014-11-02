import math

def notes() :
    return ( 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#' )

def swaras() :
    return ( 'S', 'r', 'R', 'g', 'G', 'm', 'M', 'P', 'd', 'D', 'n', 'N' )

def get_frequency_for_note( note, pitch_start ) :
    return pitch_start * pow( 2.0, notes().index( note ) / 12.0 ) 

def get_frequency_for_swara( swara, carnatic_tonic, pitch_start ) :
    return get_frequency_for_note( notes()[ ( notes().index( carnatic_tonic ) + swaras().index( swara ) ) % 12 ], pitch_start )

def note_boundaries( n_octaves ) :
    #  | A3 | A3# | B3 | C3 | C3# | D3
    #  ^    ^     ^    ^    ^     ^
    # identifying the pitch class with BSearch on pre-computed
    # boundaries is *probably* more efficient than a log() call
    ratio = pow( 2.0, 1.0 / 12.0 )
    nxt   = 1.0 / math.sqrt( ratio )
    ret   = ( nxt, )
    for i in range( n_octaves * 12 ):
        nxt *= ratio
        ret = ret + ( nxt, )
    return ret
