from pyramid.view import view_config

routes = [
    ('hello2', '/hello2' ),
]

@view_config (
    route_name='hello2',
    renderer='json'
)
def hello_world(request):
    return {"hello2": "Hello World!"}