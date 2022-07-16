import logging as l
from pyramid.view import view_config

from .lib import to_ymd, reterr, check_date_format
from .memory import get_analytics

routes = [
    ('daily', '/chart/daily/{day}'),
    ('averages', '/chart/averages/{which}'),
]


@view_config(
    route_name='daily',
    renderer='json'
)
def daily(req):
    l.info("ms_analytics/daily, day=%s" % req.matchdict["day"])
    day = req.matchdict["day"]
    a = get_analytics(req.registry.octocfg)
    if not a.ok:
        return reterr("No analytics")

    if day == "last":
        i = len(a.days_dates) - 1
        d = a.days[a.days_dates[i]]
        while not d.is_full_day() and i > 0:
            i -= 1
            d = a.days[a.days_dates[i]]
    elif check_date_format.match(day):
        if day in a.days:
            d = a.days[day]
            i = a.days_dates.index(day)
        else:
            return reterr("Day not available")
    else:
        return reterr("Invalid date format: %s" % day)

    l.info("returning %s" % day)

    _prev = None
    _next = None

    if i > 0:
        _prev = a.days_dates[i - 1]
    if i < len(a.days_dates) - 1:
        _next = a.days_dates[i + 1]

    ymd = to_ymd(d.date)
    base_load = None
    base_load_total = None
    base_load_days = None
    if ymd in a.baseaverages[a.average_days[0]]:
        base_load_total = a.baseaverages[a.average_days[0]][ymd]
        base_load = [base_load_total / 48] * len(d.times)
        base_load_days = a.average_days[0]
    ret = {
        "ok": True,
        "day": ymd,
        "chart": {
            "times": d.times,
            "half_hour_consumption": d.consumption,
            "base_load": base_load,
        },
        "stats": {
            "day_total": sum(d.consumption),
            "base_load_total": base_load_total,
            "is_full_day": d.is_full_day(),
        },
        "meta": {
            "first_day": to_ymd(a.first_time),
            "last_day": to_ymd(a.last_time),
            "first_full_day": a.first_full_day,
            "last_full_day": a.last_full_day,
            "new_day_start": a.new_day_start,
            "base_load_days": base_load_days,
            "min": a.min,
            "max": a.max,
            "prev": _prev,
            "next": _next,
        }
    }
    return ret


@view_config(
    route_name='averages',
    renderer='json'
)
def averages(req):
    l.info("ms_analytics/averages")
    which = req.matchdict["which"]
    a = get_analytics(req.registry.octocfg)
    if not a.ok:
        return reterr("No analytics")

    if which not in ['total', 'base', 'max']:
        return reterr("Unknown %s" % which)

    _chart = {
        "days": a.full_days,
    }

    _source = a.averages
    if which == 'total':
        _chart["daily"] = list(map(lambda d: a.days[d].total, a.full_days))
    elif which == 'base':
        _chart["daily"] = list(map(lambda d: a.days[d].base, a.full_days))
        _source = a.baseaverages
    elif which == 'max':
        _chart["daily"] = list(map(lambda d: a.days[d].max, a.full_days))
        _source = a.maxaverages

    for ad in a.average_days:
        k = "%d-day average" % ad
        data = []
        for d in a.full_days:
            if d in _source[ad]:
                data.append(_source[ad][d])
            else:
                data.append(None)
        _chart[k] = data

    ret = {
        "ok": True,
        "kind": which,
        "chart": _chart,
        "meta": {
            "first_day": to_ymd(a.first_time),
            "last_day": to_ymd(a.last_time),
            "first_full_day": a.first_full_day,
            "last_full_day": a.last_full_day,
            "new_day_start": a.new_day_start,
            "min": a.min,
            "max": a.max,
        }
    }
    return ret
