import numpy as np
from scipy.fftpack import rfft, dct
import collections
import math

#local
import sound

def generate_defs( notes, base_pcs ) :
    
    pcs   = [0] * len( notes )
    ret   = {}

    for key in base_pcs :
        c_np = np.array( base_pcs[ key ] )
        l    = math.sqrt( sum( c_np * c_np ) )
        d    = collections.deque( np.array( c_np ) / l )
        for i in range( len( notes ) ) :
            ret[ notes[ i ] + key ] = tuple( d )
            d.rotate( 1 )

    return ( list( ret.keys() ), list( ret.values() ) )

class Finder_Base:

    def __init__( self,
                  pitch_start,  # Hz. value of A3
                  freq_base,    # analyze intervals of 1 / freq_base seconds
                  amp_lb,       # filter amps above amp_max * amp_lb 
                  oct_wt_ratio, # rel. weight of notes in higher octaves
                  n_octaves,    # num octaves to analyze
                  use_fft       # fft instead of dct
                  ) :
 
        self.pitch_start  = pitch_start
        self.freq_base    = freq_base
        self.amp_lb       = amp_lb
        self.oct_wt_ratio = oct_wt_ratio
        self.use_fft      = use_fft

        # initialization based on the above
        self.note_bnds  = sound.note_boundaries( n_octaves )
        
        freq_lb    = self.note_bnds[ 0 ] * self.pitch_start #Hz
        freq_ub    = freq_lb * pow( 2, n_octaves ) #Hz
        
        self.oct_wts    = [ pow( self.oct_wt_ratio, i )\
                                for i in range( n_octaves ) ]
        
        #idx of freq_lb & freq_ub in fft, for filtering
        self.fr_lb_idx  = int( freq_lb / self.freq_base )
        self.fr_ub_idx  = int( freq_ub / self.freq_base )
        
        # filtered frequencies as a multiple of pitch_start
        self.fr = [ float( i + self.fr_lb_idx ) *
                    self.freq_base / self.pitch_start
                    for i in range( self.fr_ub_idx - self.fr_lb_idx + 1 ) ]

    def freq_spect_dct( self, data ) :
        
        freq_amp = dct( [ float(x) for x in data ] )[ 1 : ]
        n        = len( freq_amp )
        return ( freq_amp + freq_amp[::-1] )[ 0 : (n-1)/2 ]
        
    def freq_spect_fft( self, data ) :    
        
        fft       = rfft( data )
        np.insert( fft, 0 , 0 ) # add 0 as Re( y_0 )
        if fft.size % 2 : # append 0 as im( y_n/2 ) if necessary
            fft   = np.append( fft, 0 )
        fft      = fft.reshape( -1, 2 )
        freq_amp = np.apply_along_axis( np.linalg.norm, 1, fft )
        return freq_amp

    def filter_amps( self, framp ) :
        
        # freq of largest amp
        max_l_m = max( framp, key = lambda tup : tup[1] )[1]
        thres   = max_l_m * self.amp_lb # lower bound for amp
        framp   = [ tup for tup in framp if tup[1] > thres ]
        return framp
    
    def get_pcs( self, framp ) :
        
        pc  = 0
        idx = 0
        n   = len( self.note_bnds ) - 1
        pcs = [0] * n
        m   = len( framp )

        while idx < m and framp[ idx ][0] < self.note_bnds[ pc ] :
            idx += 1
        while pc <= n and idx < m :
            val = framp[ idx ][0]
            while self.note_bnds[ pc + 1 ] < val and pc <= n :
                pc += 1
            if pc <= n :
                pcs[ pc ] += framp[ idx ][1]
            idx += 1
    
        #log scale!
        for i in range( n ) :
            a = abs( pcs[ i ] )
            if a > 0 :
                pcs[ i ] = math.log( a )
            else :
                pcs[ i ] = 0

        #den = max( pcs )
        #eps = 1e-14
        #if den > eps :
        #    pcs = [ int(i) for i in pcs ]
        #else:
        #    pcs = [0] * n

        return np.array( pcs ).reshape( (12, -1), order = 'F' )

    def find( self, data, ret_pcs = False ) :
        
        if len( data ) < 2 * self.fr_ub_idx :
            return ( '', [], 0 )

        # [0,freq_lb)       is low
        # [freq_lb,freq_ub] is mid
        # (freq_ub,inf)     is high
        if self.use_fft :
            fs = self.freq_spect_fft( data )
        else :
            fs = self.freq_spect_dct( data )

        fs = fs[ self.fr_lb_idx : self.fr_ub_idx ] # drop the low & high freq
        
        #    low_amps.append( sum( freq_spect[ : freq_lb_idx - 1 ] ) )
        #    fs = fs[ freq_lb_idx : ] ) # drop the low freq

        framp = zip( self.fr, fs )
        framp = [ tup for tup in framp ] # python3 shit

        ( RES, val, pcs ) = self.find_from_framp( framp )
        
        if ret_pcs :
            return ( RES, pcs, val )
   
        return ( RES, [], val )

class Note( Finder_Base ) :
        
    __base_pcs__ = { ''  : [ 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] }

    ( __keys__, __vals__ ) = generate_defs( sound.notes(), __base_pcs__ )
    
    def __init__( self,
                  pitch_start,  # Hz. value of A3
                  freq_base,    # analyze intervals of 1 / freq_base seconds
                  amp_lb,       # filter amps above amp_max * amp_lb 
                  oct_wt_ratio, # rel. weight of notes in higher octaves
                  n_octaves,    # num octaves to analyze
                  use_fft,       # fft instead of dct
    ) :

        Finder_Base.__init__( self,
                              pitch_start = pitch_start,
                              freq_base   = freq_base,
                              amp_lb      = amp_lb,
                              oct_wt_ratio = oct_wt_ratio,
                              n_octaves    = n_octaves,
                              use_fft      = use_fft )
        
    def find_from_framp( self, framp ) :
   
        framp   = self.filter_amps( framp )
        pcs     = self.get_pcs( framp )
        res     = np.dot( self.__vals__, np.dot( pcs, self.oct_wts ) )
        max_idx = np.argmax( res )

        note_thres = res[ max_idx ] * 0.8
        
        if res[ max_idx ] == 0 or len ( [ i for i in res if i > note_thres ] ) > 1 :
        # more than 2 notes detected, classify as noise
            return ( '-', res[ max_idx ] , pcs )

        return ( self.__keys__[ max_idx ], res[ max_idx ], pcs )

class Chord( Finder_Base ) :

    __base_pcs__ = {
        # major chords
        ''  : [ 1, 0, 0, 0, 0.5, 0, 0, 1, 0, 0, 0, 0 ],
        '7' : [ 1, 0, 0, 0, 0.5, 0, 0, 1, 0, 0, 0.5, 0 ],
        #'M7': [ 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1 ],
        # minor
        'm': [ 1, 0, 0, 0.5, 0, 0, 0, 1, 0, 0, 0, 0 ],
        #'m7': [ 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0 ]
        }
    ( __keys__, __vals__ ) = generate_defs( sound.notes(), __base_pcs__ )
    
    def find_from_framp( self, framp ) :
        
        framp   = self.filter_amps( framp )
        pcs     = self.get_pcs( framp )
        res     = np.dot( self.__vals__, np.dot( pcs, self.oct_wts ) )
        max_idx = np.argmax( res )
        
        thres = 0.5
        if len ( [ i for i in res if i > thres ] ) > 1 :
            # more than 2 chords detected, classify as noise
            return ( '-', res[ max_idx ] , pcs )

        return ( self.__keys__[ max_idx ], res[ max_idx ], pcs )
