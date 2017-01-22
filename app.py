# # -*- coding: utf-8 -*-
from webApp import app

if __name__ == "__main__":
    import argparse

    def app_argsparse():
        parser = argparse.ArgumentParser(description="app params configuration")
        parser.add_argument("-p", "--port", help="the port of app server", type=int, default=8080)
        parser.add_argument("-d", "--debug", help="1: enable debug; 0: disable debug", type=int, default=0)
        parser.add_argument("-s", "--server", help="the wsgi server of app; default | gevent",
                            type=str, default="default")
        args = parser.parse_args()
        return args

    def run(args):
        host = "0.0.0.0"
        port = args.port
        debug = True if args.debug == 1 else False
        server = args.server
        print app.url_map
        if server == "gevent":
            from gevent.wsgi import WSGIServer
            from gevent.monkey import patch_all

            patch_all()
            WSGIServer(application=app, listener=(host, port)).serve_forever()
        else:
            app.run(host=host, port=port, debug=debug)

    run(app_argsparse())
