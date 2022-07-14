from urllib.parse import quote_plus
from datetime import datetime, timezone

# ---------------------------------------------------------------------- LIB

def _to_octo8601(dt: datetime) -> str:
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


def _from_octo8601(s) -> datetime:
    """
    New datetime object from an Octopus Energy date-time stamp

    It is nearly an ISO8691 string.

    :param s: the date and time as a string
    :return: datetime object
    """
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def _urlencode(x) -> str:
    """
    Convenience method to URL encode a string
    :param x: string to encode
    :return: the encoded string
    """
    return quote_plus(str(x).encode('utf-8'))