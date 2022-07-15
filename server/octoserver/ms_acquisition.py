import logging as l
from threading import Thread

from pyramid.view import view_config

from .defaults import DATE_TIME_FORMAT
from .memory import get_octoreader

routes = [
    ('avail', '/data/avail'),
    ('update', '/data/update'),
]


@view_config(
    route_name='avail',
    renderer='json'
)
def avail(req):
    l.info("ms_acquisition/avail")
    octoreader = get_octoreader(req.registry.octocfg)
    ret = {
        "running": octoreader.running,
        "log": octoreader.log[-5:],
    }
    if octoreader.running:
        ret |= {
            "have_data": True,
            "records": "pending",
            "incomplete_days": "pending",
            "missing_days": "pending",
            "first_time": "pending",
            "last_time": "pending",
        }
    else:
        ret |= {
            "have_data": (len(octoreader.records) > 0),
            "records": len(octoreader.records),
            "incomplete_days": octoreader.incomplete_days,
            "missing_days": octoreader.missing_days,
            "first_time": (octoreader.first_time.strftime(DATE_TIME_FORMAT)
                           if octoreader.first_time else "n.a."),
            "last_time": (octoreader.last_time.strftime(DATE_TIME_FORMAT)
                          if octoreader.last_time else "n.a."),
        }
    return ret


@view_config(
    route_name='update',
    renderer='json',
)
def update(req):
    l.info("ms_acquisition/update")
    octoreader = get_octoreader(req.registry.octocfg)
    t = Thread(target=octoreader.update)
    t.start()
    return {"ok": True}
