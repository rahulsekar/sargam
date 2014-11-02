import os
import tornado.httpserver
import tornado.ioloop
import tornado.web

#locals
import factory
import processor
import destination

args = factory.get_cmd_args()
src  = factory.get_source( args['mode'], args['infile'], args['rate'] )
prsr = processor.Processor()
br   = 2 * args['freq_base']

if args['mode'] != 'web' :
    
    dstn   = destination.File( args['outfile'] )

    #connect the modules
    src.connect( prsr, bufferRate = br )
    prsr.connect( dstn )

    #go!
    src.start()

    #done
    src.stop()

    exit( 0 )

class MainHandler( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "www/index.html" )

app = tornado.web.Application( [
    ( r'/ws', src, { 'subscriber' : prsr  } ),
    ( r'/', MainHandler ),
    ( r'/(.*)', tornado.web.StaticFileHandler, { 'path' : './www' } )
] )

http_server = tornado.httpserver.HTTPServer( app )
http_server.listen( int( os.environ.get( 'PORT', 8888 ) ) )
print( 'http server started' )
tornado.ioloop.IOLoop.instance().start()
