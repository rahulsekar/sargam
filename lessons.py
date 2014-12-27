import numpy as np
import scipy.stats as stats
import json

def load_lessons() :
    return json.load( open( 'www/lessons.json' ) )[ 'lessons' ]

def get_lesson_names() :
    return [ l[ 'name' ] for l in load_lessons() ]
    
def get_lesson( lesson_name ) :

    res = load_lessons()
    idx = [ l[ 'name' ] for l in res ].index( lesson_name )
    return str( res[ idx ][ 'swara' ] )

'''
    lessons = {
        'sarali9'  : 'SrGmPmdPSrGmPdNSSNdPmPGmSNdPmGrS',
        'sarali10' : 'SrGmPPGmPPPPPPPPGmPdNdPmGmPGmGrS',
        'sarali11' : 'SSNdNNdPddPmPPPPGmPdNdPmGmPGmGrS',
        'sarali13' : 'SrGrGGGmPmPPdPddmPdPdNdPmPdPmGrS',
        'sarali14' : 'SrGmPPPPddPPmmPPdNSSSNdPSNdPmGrS',
        'datu1'    : 'SSmmrrGGSSrrGGmmrrPPGGmmrrGGmmPPGGddmmPPGGmmPPddmmNNPPddmmPPddNNPPSSddNNPPddNNSSSSPPNNddSSNNddPPNNmmddPPNNddPPmmddGGPPmmddPPmmGGPPrrmmGGPPmmGGrrmmSSGGrrmmGGrrSS',
        'datu2'    : 'SmGmrGSrSGrGSrGmrPmPGmrGrmGmrGmPGdPdmPGmGPmPGmPdmNdNPdmPmdPdmPdNPSNSdNPdPNdNPdNSSPdPNdSNSdNdSNdPNmPmdPNdNPdPNdPmdGmGPmdPdmPmdPmGPrGrmGPmPGmGPmGrmSrSGrmGmrGrmGrS',
        'datu3'    : '',
'''

def distance( lesson, results ) :

    n  = len( lesson )
    m  = len( results )
    dp = np.zeros( ( n + 1, m + 1 ) )
    for i in range( n ) :
        for j in range( m ) :
            dp[ i + 1 ][ j + 1 ] = max( dp[ i ][ j ] + ( lesson[ i ] == results[ j ] ), dp[ i + 1 ][ j ] )

    return dp[ n ][ m ] * 100.0 / len( lesson )
