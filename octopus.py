import sys
import json
import requests

from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------- LIB

TIME_DELTA = 90  # number of days to download in one call
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


def _quit(s, code):
    """
    Exit the program displaying a message

    :param s: message to display
    :param code: error code
    :return: no return
    """
    print(s)
    sys.exit(code)


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


def _urlencode(x):
    """
    Convenience method to URL encode a string
    :param x: string to encode
    :return: the encoded string
    """
    return quote_plus(str(x).encode('utf-8'))


# ---------------------------------------------------------------------- OCTOREADER

class OctoReader:
    """
    Class encapsulating the functionality to retrieve Octopus Energy readings
    """

    def __init__(self):
        """
        Sets up the new object

        Reads the configuration file,
        checks that required settings are in the configuration,
        initialises attributes.
        """
        try:
            # read `config.json`
            with open("config.json", "r") as F:
                cfg = json.load(F)

            self.accounts = []

            if "accounts" in cfg:
                for acfg in cfg["accounts"]:
                    missing = []
                    for required_config in ["url", "apikey", "csv", "name"]:
                        if required_config not in acfg:
                            missing.append(required_config)
                    if len(missing):
                        # abort if any missing
                        missing = ", ".join(missing)
                        _quit("Missing required configuration %s" % missing, 1)

                    self.accounts.append({
                        "name": acfg["name"],
                        "apiurl": acfg["url"],
                        "apikey": acfg["apikey"],
                        "csv": acfg["csv"],
                    })

            else:
                # find any missing parameters
                missing = []
                for required_config in ["url", "apikey", "mpan", "serial"]:
                    if required_config not in cfg:
                        missing.append(required_config)
                if len(missing):
                    # abort if any missing
                    missing = ", ".join(missing)
                    _quit("Missing required configuration %s" % missing, 1)

                # remove trailing / from URL host
                if cfg["url"][-1] == '/':
                    cfg["url"] = cfg["url"][:-1]

                # set the CSV file name
                csvfn = "-".join(["octopus", cfg["mpan"], cfg["serial"]]) + ".csv"
                if "csv" in cfg:
                    csvfn = cfg["csv"]
                typ = "electricity"
                if "type" in cfg and cfg["type"].lower() in ["electricity", "gas"]:
                    typ = cfg["type"].lower()
                # encode the MPAN and serial number for later URL use
                mpan = _urlencode(cfg["mpan"])
                serial = _urlencode(cfg["serial"])
                self.accounts.append({
                    "name": typ.capitalize(),
                    "url": cfg["url"],
                    "apikey": cfg["apikey"],
                    "mpan": mpan,
                    "serial": serial,
                    "type": typ,
                    "apiurl": (
                        "%s/v1/electricity-meter-points/%s/meters/%s/consumption" % (cfg["url"], mpan, serial)
                        if typ == "electricity" else
                        "%s/v1/gas-meter-points/%s/meters/%s/consumption" % (cfg["url"], mpan, serial)
                    ),
                    "csv": csvfn,
                })
                if typ == "electricity":
                    self.accounts[-1]["apirul"] = "/v1/electricity-meter-points/%s/meters/%s/consumption" % (
                        mpan, serial)

            # set 'now' -- note that the API uses timezones
            self.now = datetime.now(LOCAL_TIMEZONE).replace(microsecond=0)
            # the time delta is the number of days to retrieve in one API request
            self.delta = timedelta(TIME_DELTA)
            if self.delta > timedelta(365):
                _quit("Source code constant error: time delta must be less than or equal to 365 days", 1)
            # each hour has two records, so each day has 48
            self.page_size = TIME_DELTA * 48

            self.cfg = cfg

        except Exception as ex:
            _quit("Error loading configuration file (config.json): " + str(ex), 1)

    def _set_state(self, state: str):
        """
        Convenience method to show and store the state

        Exceptions can then display the error state.

        :param state: a string with the state
        :return: no return
        """
        self.state = state.lower()
        print(state + "...")

    def _get_from_api(self, get_url: str, apikey: str, *, params: dict = None) -> dict:
        """
        Execute an HTTP REST API request

        Will abort the program if an error is encountered.

        Will use the configured protocol and host part of the URL
        and authenticate with the given bearer token.

        :param get_url: fully qualified API URL
        :param params: a dict of parameter name/value pairs to be added to the query string
        :return: the returned and deserialised JSON data
        """
        if params:
            param_string = "&".join(map(lambda x: "%s=%s" % (x[0], x[1]), params.items()))
            if param_string:
                get_url += "?" + param_string

        res = requests.get(get_url, auth=(apikey, ""))

        if res.status_code != 200:
            txt = res.text
            data = res.json()
            if data and "detail" in data:
                txt = data["detail"]
            _quit("Error %s: %d %s" % (self.state, res.status_code, txt), 2)

        return res.json()

    @staticmethod
    def _check_csv(acc) -> Optional[datetime]:
        """
        Check if the CSV file exists and find the end of the last interval

        :param acc: the account as a dict
        :return: end time of the last interval or None
        """
        csvfn = acc["csv"]
        csvpath = Path(csvfn)
        if csvpath.is_file():
            with open(csvfn, "r") as F:
                last_time = None
                for line in F:
                    rec = line.split(",")
                    if rec[0] == 'Start':
                        continue
                    if rec[1][0] == '"' and rec[1][-1] == '"':
                        rec[1] = rec[1][1:-1]
                    if last_time is None or last_time < rec[1]:
                        last_time = rec[1]
            if last_time is not None:
                return _from_octo8601(last_time)
            else:
                return None
        else:
            return None

    def _get_interval(self, forward, time):
        """
        Return an interval for the API parameters

        Takes into consideration whether the retrieval
        is going forward or backward in time.

        The returned next time can be supplied
        to this function to get the next interval.
        The next time will be None for forward
        retrievals going past 'now'.

        :param forward: True if going forward
        :param time: current last time
        :return: the start, end and next times
        """
        if forward:
            _start = time
            _end = time + self.delta
            _next = _end
            if _end > self.now:
                _end = self.now
                _next = None
            return _start, _end, _next
        else:
            _end = time
            _start = _end - self.delta
            _next = _start
            return _start, _end, _next

    def _read_consumption(self, acc, last_time=None) -> list:
        """
        Retrieve the consumption data from Octopus Energy

        Can retrieve all available historic data or
        do an incremental update.

        `last_time` needs to be set to None to do a full
        historic retrieval.

        :param acc: the account as a dict
        :param last_time: the end of the last timestamp in the CSV file or None
        :return: the list of retrieved records
        """
        going_forward = True  # forward = incremental, backward = historic
        if last_time is None:
            # if no time given, then retrieve all data from 'now' going backwards
            going_forward = False
            last_time = self.now

        all_readings = []  # all retrieved records

        while last_time is not None:
            # get the interval times for the current last time
            start_time, end_time, next_time = self._get_interval(going_forward, last_time)
            print("   from", start_time, "to", end_time)

            # retrieve the data from the API
            data = self._get_from_api(
                acc["apiurl"],
                acc["apikey"],
                params={
                    "period_from": _to_octo8601(start_time),
                    "period_to": _to_octo8601(end_time),
                    "order_by": "period",
                    "page_size": self.page_size,
                }
            )

            if len(data["results"]):
                all_readings += data["results"]
            else:
                # no data, so we are at the end of the available history
                break

            last_time = next_time

        return sorted(all_readings, key=lambda x: x["interval_start"])

    @staticmethod
    def _write_records(f, data):
        """
        Writes the records to the provided file

        :param f: open file handle
        :param data: list of consumption records
        :return: no return
        """
        for rec in data:
            f.write("\"%s\",\"%s\",%s\n" % (
                rec["interval_start"],
                rec["interval_end"],
                rec["consumption"]
            ))

    def _process_account(self, acc):
        """
        Main method: executes the data retrieval

        If it finds an existing CSV file, it will check the latest time
        and will try to incrementally download newer data.

        If there is no CSV file, then all available historic data
        is downloaded.

        :param acc:  the account as a dict
        :return: no return
        """
        print("Processing account %s" % acc["name"])
        try:
            # Check if data is already available
            self._set_state("Checking existing data")
            last_time = self._check_csv(acc)

            if last_time is None:
                # No data available, full history download required
                self._set_state("Downloading historic data")
                data = self._read_consumption(acc)

                if len(data) > 0:
                    # Create a new CSV file with the data
                    print("Retrieved", len(data), "historic consumption records.")
                    self._set_state("Saving historic data")
                    with open(acc["csv"], "w") as F:
                        F.write("Start,End,Consumption\n")
                        self._write_records(F, data)
                else:
                    print("No historic data.")
            else:
                # Data is already available, incremental update follows
                print("Last interval ended at", last_time)
                self._set_state("Downloading new data")
                data = self._read_consumption(acc, last_time)

                if len(data) > 0:
                    # Have new data, append to CSV
                    print("Retrieved", len(data), "new consumption records.")
                    self._set_state("Saving new data")
                    with open(acc["csv"], "a") as F:
                        self._write_records(F, data)
                else:
                    print("No new data.")

        except Exception as ex:
            _quit("Error %s: %s" % (self.state, str(ex)), 3)

    def main(self):

        for acc in self.accounts:
            self._process_account(acc)

        print("Done.")


# ---------------------------------------------------------------------- MAIN
if __name__ == "__main__":
    print("Download Octopus Energy Meter Readings\n")
    octoreader = OctoReader()
    octoreader.main()
