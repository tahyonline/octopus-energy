from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config
from . import reloader

SRV_LISTEN_ADDRESS = '127.0.0.1'
SRV_LISTEN_PORT = 6543
SPA_PATH = '../../spa/build'

@view_config (
    route_name='hello',
    renderer='json'
)
def hello_world(request):
    return {"hello": "Hello World!"}

def main(global_config, **settings):
    with Configurator() as config:
        config.add_route('hello', '/hello')
        for _route_name, _route_path in reloader.routes:
            config.add_route(_route_name, _route_path)
        config.scan()
        config.add_static_view(name='/', path=SPA_PATH)
        app = config.make_wsgi_app()
    server = make_server(SRV_LISTEN_ADDRESS, SRV_LISTEN_PORT, app)
    print("Listening on http://%s:%d/" % (SRV_LISTEN_ADDRESS, SRV_LISTEN_PORT))
    server.serve_forever()