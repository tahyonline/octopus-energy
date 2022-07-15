import logging as l
from urllib.parse import quote_plus
from re import compile as re_compile
from datetime import datetime, timezone


# ---------------------------------------------------------------------- LIB

def to_octo8601(dt: datetime) -> str:
    """
    Return the ISO string representation of a datetime

    Seconds resolution only.

    Although the API doc says that the timezone should be included,
    it actually does not work.
    https://developer.octopus.energy/docs/api/#parameters

    Therefore the time is converted to UTC and
    returned as Z (zulu) time.

    :param dt: datetime object
    :return: date and time as string
    """
    return dt.astimezone(timezone.utc).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')


def from_octo8601(s) -> datetime:
    """
    New datetime object from an Octopus Energy date-time stamp

    It is nearly an ISO8691 string.

    :param s: the date and time as a string
    :return: datetime object
    """
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def to_ymd(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def from_ymd(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def to_hm(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def urlencode(x) -> str:
    """
    Convenience method to URL encode a string
    :param x: string to encode
    :return: the encoded string
    """
    return quote_plus(str(x).encode('utf-8'))


def to_utc(dt: datetime) -> datetime:
    return dt.astimezone(tz=timezone.utc)


def reterr(s: str):
    l.error(s)
    return {
        "ok": False,
        "error": s,
    }


check_date_format = re_compile(r"\d\d\d\d-\d\d-\d\d")
