import requests
from os.path import join as pathjoin

from pathlib import Path
from typing import Optional
from datetime import timedelta

from .lib import *
from .stateful import Stateful
from .defaults import LOCAL_TIMEZONE, TIME_DELTA, CSV_FILE_LOCATION


class OctoReader(Stateful):
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
        Stateful.__init__(self)
        self.running = False
        self._set_state("Initialising")
        try:
            # remove trailing / from URL host
            if cfg["url"][-1] == '/':
                cfg["url"] = cfg["url"][:-1]

            # set the CSV file name
            self.csvfn = "-".join(["octopus", cfg["mpan"], cfg["serial"]]) + ".csv"
            if "csv" in cfg:
                self.csvfn = cfg["csv"]
            self.csvfn = pathjoin(CSV_FILE_LOCATION, self.csvfn)

            # encode the MPAN and serial number for later URL use
            self.mpan = urlencode(cfg["mpan"])
            self.serial = urlencode(cfg["serial"])

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

        try:
            self._load_csv()
        except Exception as ex:
            self._set_state("Error %s: %s" % (self.state, str(ex)), False)
            return

    def _get_from_api(self, endpoint: str, *, params: dict = None) -> Optional[dict]:
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
            self._set_state("Error %s: %d %s" % (self.state, res.status_code, txt), False)
            return None

        return res.json()

    def _load_csv(self):
        """
        Load the CSV file

        :return: no return
        """
        self.records = []
        self.incomplete_days = []
        self.missing_days = []
        self.first_time = None
        self.last_time = None
        csvpath = Path(self.csvfn)
        days_in_records = []
        if csvpath.is_file():
            self._set_state("Loading CSV file")
            with open(self.csvfn, "r") as F:
                day = None
                count = 0
                for line in F:
                    rec = line.split(",")
                    if rec[0] == 'Start':
                        continue
                    for i in [0, 1]:
                        if rec[i][0] == '"' and rec[i][-1] == '"':
                            rec[i] = rec[i][1:-1]
                    self.records.append(rec)
                    count += 1
                    if day is None or day != rec[0][:10]:
                        if day is not None:
                            if count != 48:
                                self.incomplete_days.append({
                                    "day": day,
                                    "recs": count,
                                })
                        day = rec[0][:10]
                        days_in_records.append(day)
                        count = 0

            if len(self.records):
                self.records = sorted(self.records, key=lambda x: x[0])
            self.first_time = from_octo8601(self.records[0][0])
            self.last_time = from_octo8601(self.records[-1][1])

            dt = self.first_time
            _one_day = timedelta(1)
            while dt <= self.last_time:
                day = to_ymd(dt)
                if day not in days_in_records:
                    self.missing_days.append(day)
                dt += _one_day

            self._set_state("Loaded %d records" % (len(self.records)))
        else:
            self._set_state("CSV file does not exist")

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
        going_forward = True  # forward = incremental, backward = historic
        l.getLogger("requests").setLevel(l.WARNING)
        l.getLogger("urllib").setLevel(l.WARNING)
        l.getLogger("urllib3").setLevel(l.WARNING)
        if last_time is None:
            # if no time given, then retrieve all data from 'now' going backwards
            going_forward = False
            last_time = self.now

        all_readings = []  # all retrieved records

        while last_time is not None:
            # get the interval times for the current last time
            start_time, end_time, next_time = self._get_interval(going_forward, last_time)
            self._set_state("Requesting from %s to %s " % (start_time, end_time))

            # retrieve the data from the API
            data = self._get_from_api(
                "/v1/electricity-meter-points/%s/meters/%s/consumption" %
                (self.mpan, self.serial),
                params={
                    "period_from": to_octo8601(start_time),
                    "period_to": to_octo8601(end_time),
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

    def _write_records(self, fh, data):
        """
        Writes the records to the provided file

        :param fh: open file handle
        :param data: list of consumption records
        :return: no return
        """
        for rec in data:
            fh.write("\"%s\",\"%s\",%s\n" % (
                rec["interval_start"],
                rec["interval_end"],
                rec["consumption"]
            ))
        self._set_state("Wrote %d records" % (len(data)))

    def update(self):
        """
        Main method: executes the data retrieval

        If it finds an existing CSV file, it will check the latest time
        and will try to incrementally download newer data.

        If there is no CSV file, then all available historic data
        is downloaded.
        :return: no return
        """
        if self.running:
            l.warning("OctoReader: update already running")
            return
        self.running = True
        try:
            # Check if data is already available

            if self.last_time is None:
                # No data available, full history download required
                self._set_state("Downloading historic data")
                data = self._read_consumption()

                if len(data) > 0:
                    # Create a new CSV file with the data
                    self._set_state("Saving %d historic consumption records" % len(data))
                    with open(self.csvfn, "w") as F:
                        F.write("Start,End,Consumption\n")
                        self._write_records(F, data)
                else:
                    self._set_state("No historic data.")
            else:
                # Data is already available, incremental update follows
                self._set_state("Downloading new data since %s" % self.last_time)
                data = self._read_consumption(self.last_time)

                if len(data) > 0:
                    # Have new data, append to CSV
                    self._set_state("Saving %d new consumption records" % len(data))
                    with open(self.csvfn, "a") as F:
                        self._write_records(F, data)
                else:
                    self._set_state("No new data.")

        except Exception as ex:
            self._set_state("Error %s: %s" % (self.state, str(ex)), False)
            self.running = False
            return

        try:
            self._load_csv()
        except Exception as ex:
            self._set_state("Error %s: %s" % (self.state, str(ex)), False)
            self.running = False
            return

        self.running = False
