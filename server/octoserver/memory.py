import logging as l

from .analytics import Analytics
from .data_acquisition import OctoReader

_analytics = None
_octoreader = None


def get_analytics(cfg):
    global _analytics
    octoreader = get_octoreader(cfg)
    if _analytics is None or not _analytics.same_period(octoreader):
        _analytics = Analytics(cfg, octoreader)

    if _analytics.ok:
        l.info("Analytics initialised")
    else:
        l.warning("Analytics was not initialised")

    return _analytics


def get_octoreader(cfg) -> OctoReader:
    global _octoreader
    if _octoreader is None:
        _octoreader = OctoReader(cfg)
        if not _octoreader.ok:
            l.error("OctoReader could not be initialised.")
            sysexit(1)
        l.info("OctoReader initialised")

    return _octoreader
