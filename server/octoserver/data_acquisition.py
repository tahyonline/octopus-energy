import json
import requests

from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from .lib import _urlencode
from .defaults import LOCAL_TIMEZONE, TIME_DELTA


class OctoReader:
    """
    Class encapsulating the functionality to retrieve Octopus Energy readings
    """
    def __init__(self, cfg):
        """
        Sets up the new object

        Reads the configuration file,
        checks that required settings are in the configuration,
        initialises attributes.
        """
        self._set_state("Initialising")
        try:



            # remove trailing / from URL host
            if cfg["url"][-1] == '/':
                cfg["url"] = cfg["url"][:-1]

            # set the CSV file name
            self.csvfn = "-".join(["octopus", cfg["mpan"], cfg["serial"]]) + ".csv"
            if "csv" in cfg:
                self.csvfn = cfg["csv"]
            # encode the MPAN and serial number for later URL use
            self.mpan = _urlencode(cfg["mpan"])
            self.serial = _urlencode(cfg["serial"])

            # set 'now' -- note that the API uses timezones
            self.now = datetime.now(LOCAL_TIMEZONE).replace(microsecond=0)
            # the time delta is the number of days to retrieve in one API request
            self.delta = timedelta(TIME_DELTA)
            if self.delta > timedelta(365):
                self._set_state("Source code constant error: time delta must be less than or equal to 365 days", False)
                return
            # each hour has two records, so each day has 48
            self.page_size = TIME_DELTA * 48

            self.cfg = cfg

        except Exception as ex:
            self._set_state("Error loading configuration file (config.json): " + str(ex), False)
            return


    def _set_state(self, state: str, ok: bool = True):
        """
        Convenience method to show and store the state

        Exceptions can then display the error state.

        :param state: a string with the state
        :return: no return
        """
        self.state = state
        self.ok = ok

    def _get_from_api(self, endpoint: str, *, params: dict = None) -> dict:
        """
        Execute an HTTP REST API request

        Will abord the program if an error is encountered.

        Will use the configured protocol and host part of the URL
        and authenticate with the given bearer token.

        :param endpoint: the path portion of the API endpoint
        :param params: a dict of parameter name/value pairs to be added to the query string
        :return: the returned and deserialised JSON data
        """
        cfg = self.cfg
        if endpoint[0] == '/':
            endpoint = endpoint[1:]

        get_url = "%s/%s" % (cfg["url"], endpoint)

        if params:
            param_string = "&".join(map(lambda x: "%s=%s" % (x[0], x[1]), params.items()))
            if param_string:
                get_url += "?" + param_string

        res = requests.get(get_url, auth=(cfg["apikey"], ""))

        if res.status_code != 200:
            txt = res.text
            data = res.json()
            if data and "detail" in data:
                txt = data["detail"]
            _quit("Error %s: %d %s" % (self.state, res.status_code, txt), 2)

        return res.json()

    def _check_csv(self) -> Optional[datetime]:
        """
        Check if the CSV file exists and find the end of the last interval

        :return: end time of the last interval or None
        """
        csvpath = Path(self.csvfn)
        if csvpath.is_file():
            end_times = []
            with open(self.csvfn, "r") as F:
                for line in F:
                    rec = line.split(",")
                    if rec[0] == 'Start':
                        continue
                    if rec[1][0] == '"' and rec[1][-1] == '"':
                        rec[1] = rec[1][1:-1]
                    end_times.append(rec[1])
            if len(end_times):
                last_time = sorted(end_times)[-1]
                return _from_octo8601(last_time)
            else:
                return None
        else:
            return None

    def _get_interval(self, forward: bool, time: datetime) -> (datetime, datetime, datetime):
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

    def _read_consumption(self, last_time=None) -> list:
        """
        Retrieve the consumption data from Octopus Energy

        Can retrieve all available historic data or
        do an incremental update.

        `last_time` needs to be set to None to do a full
        historic retrieval.

        :param last_time: the end of the last timestamp in the CSV file or None
        :return: the list of retrieved records
        """
        going_forward = True # forward = incremental, backward = historic
        if last_time is None:
            # if no time given, then retrieve all data from 'now' going backwards
            going_forward = False
            last_time = self.now

        all_readings = [] # all retrieved records

        while last_time is not None:
            # get the interval times for the current last time
            start_time, end_time, next_time = self._get_interval(going_forward, last_time)
            print("   from", start_time, "to", end_time)

            # retrieve the data from the API
            data = self._get_from_api(
                "/v1/electricity-meter-points/%s/meters/%s/consumption" %
                (self.mpan, self.serial),
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

    def _write_records(self, F, data):
        """
        Writes the records to the provided file

        :param F: open file handle
        :param data: list of consumption records
        :return: no return
        """
        for rec in data:
            F.write("\"%s\",\"%s\",%s\n" % (
                rec["interval_start"],
                rec["interval_end"],
                rec["consumption"]
            ))

    def main(self):
        """
        Main method: executes the data retrieval

        If it finds an existing CSV file, it will check the latest time
        and will try to incrementally download newer data.

        If there is no CSV file, then all available historic data
        is downloaded.
        :return: no return
        """
        try:
            # Check if data is already available
            self._set_state("Checking existing data")
            last_time = self._check_csv()

            if last_time is None:
                # No data available, full history download required
                self._set_state("Downloading historic data")
                data = self._read_consumption()

                if len(data) > 0:
                    # Create a new CSV file with the data
                    print("Retrieved", len(data), "historic consumption records.")
                    self._set_state("Saving historic data")
                    with open(self.csvfn, "w") as F:
                        F.write("Start,End,Consumption\n")
                        self._write_records(F, data)
                else:
                    print("No historic data.")
            else:
                # Data is already available, incremental update follows
                print("Last interval ended at", last_time)
                self._set_state("Downloading new data")
                data = self._read_consumption(last_time)

                if len(data) > 0:
                    # Have new data, append to CSV
                    print("Retrieved", len(data), "new consumption records.")
                    self._set_state("Saving new data")
                    with open(self.csvfn, "a") as F:
                        self._write_records(F, data)
                else:
                    print("No new data.")

        except Exception as ex:
            _quit("Error %s: %s" % (self.state, str(ex)), 3)

        self._set_state("Done")

