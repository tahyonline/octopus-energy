import logging as l
from sys import stdout
from json import load as jsonload

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config

from . import ms_acquisition
from . import ms_analytics
from .defaults import SPA_PATH, SRV_LISTEN_ADDRESS, SRV_LISTEN_PORT, LOGGING_FORMAT

@view_config(
    route_name='hello',
    renderer='json'
)
def hello_world(request):
    return {"hello": "Hello World!"}


def main(global_config, **settings):
    _logging = l.getLogger()
    _logging.setLevel(l.DEBUG)

    _log_to_stdout = l.StreamHandler(stdout)
    _log_to_stdout.setLevel(l.DEBUG)
    formatter = l.Formatter(LOGGING_FORMAT)
    _log_to_stdout.setFormatter(formatter)
    if (_logging.hasHandlers()):
        _logging.handlers.clear()
    _logging.addHandler(_log_to_stdout)

    l.info("Octopus Energy Consumption Analyser")

    # read `config.json`
    with Configurator() as config:
        # --------------------------------------- Load configuration
        with open("../config.json", "r") as F:
            octocfg = jsonload(F)
        # find any missing parameters
        missing = []
        for required_config in ["url", "apikey", "mpan", "serial"]:
            if required_config not in octocfg:
                missing.append(required_config)
        if len(missing):
            # abort if any missing
            missing = ", ".join(missing)
            l.error("ERROR: missing required configuration %s" % missing)
            return
        config.registry.octocfg = octocfg

        # --------------------------------------- Set up routes
        config.add_route('hello', '/hello')

        # Microservices:
        # data acquisition
        for _route_name, _route_path in ms_acquisition.routes:
            config.add_route(_route_name, _route_path)
        for _route_name, _route_path in ms_analytics.routes:
            config.add_route(_route_name, _route_path)

        config.scan()

        # Static files for the SPA
        config.add_static_view(name='/', path=SPA_PATH)
        app = config.make_wsgi_app()

    # ------------------------------------------- Run the server
    server = make_server(SRV_LISTEN_ADDRESS, SRV_LISTEN_PORT, app)
    l.info("Listening on http://%s:%d/" % (SRV_LISTEN_ADDRESS, SRV_LISTEN_PORT))
    server.serve_forever()
