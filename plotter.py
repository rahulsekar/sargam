#import matplotlib.pyplot as plt
import numpy as np

#local
import sound

def plot( all_pcs, times ) :
    
    notes = sound.notes()
    times = np.asarray( times )
    dt    = times[ 1 ] - times[ 0 ];
    times = np.append( times, times[ -1 ] + dt )

    fig, ( top, bot ) = plt.subplots( 2, sharex = True )

    ztop = np.asarray( [ pcs.flatten( 'F' ) for pcs in all_pcs ] ).transpose()
    ytop = []
    for i in range( all_pcs[0].shape[1] ) :
        ytop += [ '%s%d' % ( n, i ) for n in notes ]
    xvtop, yvtop = np.meshgrid( times, np.arange( len( ytop ) + 1 ) )
    top.pcolormesh( xvtop, yvtop, ztop )
    top.set_yticks( np.arange( len( ytop ) ) + 0.5 )
    top.set_yticklabels( ytop )
    
    zbot         = np.asarray( [ np.sum( pcs, axis = 1 ) for pcs in all_pcs ] ).transpose()
    ybot         = notes
    xvbot, yvbot = np.meshgrid( times, np.arange( len( ybot ) + 1 ) )
    bot.pcolormesh( xvbot, yvbot, zbot )
    bot.set_yticks( np.arange( len( ybot ) ) + 0.5 )
    bot.set_yticklabels( ybot )
    bot.pcolormesh( xvbot, yvbot, zbot )
    
    plt.show()
