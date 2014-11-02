import numpy as np
import scipy.stats as stats

def get_lessons() :

    lessons = {
        'sarali0'  : 'SPSPS',
        'sarali1'  : 'SrGmPdNSSNdPmGrS',
        'sarali2'  : 'SrSrSrGmSrGmPdNSSNSNSNdPSNdPmGrS',
        'sarali3'  : 'SrGSrGSrSrGmPdNSSNdSNdSNSNdPmGrS',
        'sarali4'  : 'SrGmSrGmSrGmPdNSSNdPSNdPSNdPmGrS',
        'sarali5'  : 'SrGmPPSrSrGmPdNSSNdPmmSNSNdPmGrS',
        'sarali6'  : 'SrGmPdSrSrGmPdNSSNdPmGSNSNdPmGrS',
        'sarali7'  : 'SrGmPdNNSrGmPdNSSNdPmGrrSNdPmGrS',
        'sarali8'  : 'SrGmPmGrSrGmPdNSSNdPmPdNSNdPmGrS',
        'sarali9'  : 'SrGmPmdPSrGmPdNSSNdPmPGmSNdPmGrS',
        'sarali10' : 'SrGmPPGmPPPPPPPPGmPdNdPmGmPGmGrS',
        'sarali11' : 'SSNdNNdPddPmPPPPGmPdNdPmGmPGmGrS',
        'sarali13' : 'SrGrGGGmPmPPdPddmPdPdNdPmPdPmGrS',
        'sarali14' : 'SrGmPPPPddPPmmPPdNSSSNdPSNdPmGrS',
        'datu1'    : 'SSmmrrGGSSrrGGmmrrPPGGmmrrGGmmPPGGddmmPPGGmmPPddmmNNPPddmmPPddNNPPSSddNNPPddNNSSSSPPNNddSSNNddPPNNmmddPPNNddPPmmddGGPPmmddPPmmGGPPrrmmGGPPmmGGrrmmSSGGrrmmGGrrSS',
        'datu2'    : 'SmGmrGSrSGrGSrGmrPmPGmrGrmGmrGmPGdPdmPGmGPmPGmPdmNdNPdmPmdPdmPdNPSNSdNPdPNdNPdNSSPdPNdSNSdNdSNdPNmPmdPNdNPdPNdPmdGmGPmdPdmPmdPmGPrGrmGPmPGmGPmGrmSrSGrmGmrGrmGrS',
        'datu3'    : '',
        'lambodhara' : 'mPdSSrrSdPmPrmPdmPdPmGrSSrmmGrSrGrSrmPdmPdPmGrS',
    }

    return lessons

def distance( lesson, results ) :

    n  = len( lesson )
    m  = len( results )
    dp = np.zeros( ( n + 1, m + 1 ) )
    for i in range( n ) :
        for j in range( m ) :
            dp[ i + 1 ][ j + 1 ] = max( dp[ i ][ j ] + ( lesson[ i ] == results[ j ] ), dp[ i + 1 ][ j ] )

    return dp[ n ][ m ] * 100.0 / len( lesson )
