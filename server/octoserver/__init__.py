from json import load as jsonload

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config

from . import reloader
from .defaults import SPA_PATH, SRV_LISTEN_ADDRESS, SRV_LISTEN_PORT

@view_config(
    route_name='hello',
    renderer='json'
)
def hello_world(request):
    return {"hello": "Hello World!"}


def main(global_config, **settings):
    # read `config.json`
    with Configurator() as config:
        # --------------------------------------- Load configuration
        with open("config.json", "r") as F:
            octocfg = jsonload(F)
        # find any missing parameters
        missing = []
        for required_config in ["url", "apikey", "mpan", "serial"]:
            if required_config not in octocfg:
                missing.append(required_config)
        if len(missing):
            # abort if any missing
            missing = ", ".join(missing)
            print("ERROR: missing required configuration %s" % missing, False)
            return
        config.registry.octocfg = octocfg

        # --------------------------------------- Set up routes
        config.add_route('hello', '/hello')
        for _route_name, _route_path in reloader.routes:
            config.add_route(_route_name, _route_path)
        config.scan()
        config.add_static_view(name='/', path=SPA_PATH)
        app = config.make_wsgi_app()

    # ------------------------------------------- Run the server
    server = make_server(SRV_LISTEN_ADDRESS, SRV_LISTEN_PORT, app)
    print("Listening on http://%s:%d/" % (SRV_LISTEN_ADDRESS, SRV_LISTEN_PORT))
    server.serve_forever()
