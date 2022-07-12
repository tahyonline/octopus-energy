import sys
import json
from typing import Optional

import requests
from pathlib import Path
from urllib.parse import quote_plus
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------- LIB

TIME_DELTA = 90  # number of days to download in one call
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


def _quit(s, code):
    print(s)
    sys.exit(code)


def _to_octo8691(dt):
    return dt.isoformat()[:19] + "Z"


def _from_octo8680(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def _urlencode(x):
    return quote_plus(str(x).encode('utf-8'))


# ---------------------------------------------------------------------- OCTOREADER

class OctoReader:
    def __init__(self):
        try:
            with open("config.json", "r") as F:
                cfg = json.load(F)

            missing = []
            for required_config in ["url", "apikey", "mpan", "serial"]:
                if required_config not in cfg:
                    missing.append(required_config)
            if len(missing):
                missing = ", ".join(missing)
                _quit("Missing required configuration %s" % missing, 1)

            if cfg["url"][-1] == '/':
                cfg["url"] = cfg["url"][:-1]

            self.csvfn = "-".join(["octopus", cfg["mpan"], cfg["serial"]]) + ".csv"
            if "csv" in cfg:
                self.csvfn = cfg["csv"]
            self.mpan = _urlencode(cfg["mpan"])
            self.serial = _urlencode(cfg["serial"])

            self.now = datetime.now(LOCAL_TIMEZONE)
            print(self.now)
            self.delta = timedelta(TIME_DELTA)
            if self.delta > timedelta(365):
                _quit("Source code constant error: time delta must be less than or equal to 365 days", 1)
            self.page_size = TIME_DELTA * 48

            self.cfg = cfg

        except Exception as ex:
            _quit("Error loading configuration file (config.json): " + str(ex), 1)

    def _set_state(self, state: str):
        self.state = state.lower()
        print(state + "...")

    def _get(self, endpoint: str, *, params: dict = None) -> dict:
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
            if data and data["detail"]:
                txt = data["detail"]
            _quit("Error %s: %d %s" % (self.state, res.status_code, txt), 2)

        return res.json()

    def _check_csv(self) -> Optional[datetime]:
        csvpath = Path(self.csvfn)
        if csvpath.is_file():
            with open(self.csvfn, "r") as F:
                for line in F:
                    pass
            eoi = line.split(",")[1].strip()
            if eoi[0] == '"' and eoi[-1] == '"':
                eoi = eoi[1:]
                eoi = eoi[:-1]
            if eoi == "Start":
                return None
            return _from_octo8680(eoi)
        else:
            return None

    def _get_interval(self, forward, time):
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
        going_forward = True
        if last_time is None:
            going_forward = False
            last_time = self.now

        all_readings = []

        while last_time is not None:
            start_time, end_time, next_time = self._get_interval(going_forward, last_time)

            data = self._get(
                "/v1/electricity-meter-points/%s/meters/%s/consumption" %
                (self.mpan, self.serial),
                params={
                    "period_from": _to_octo8691(start_time),
                    "period_to": _to_octo8691(end_time),
                    "order_by": "period",
                    "page_size": self.page_size,
                }
            )
            if len(data["results"]):
                all_readings += data["results"]
            else:
                break

            last_time = next_time

        return sorted(all_readings, key=lambda x: x["interval_start"])

    def main(self):
        try:
            self._set_state("Checking existing data")

            last_time = self._check_csv()

            if last_time is None:
                self._set_state("Downloading historic data")
                data = self._read_consumption()

                self._set_state("Saving historic data")
                with open(self.csvfn, "w") as F:
                    F.write("Start,End,Consumption\n")
                    for rec in data:
                        F.write("\"%s\",\"%s\",%s\n" % (
                            rec["interval_start"],
                            rec["interval_end"],
                            rec["consumption"]
                        ))
            else:
                print("Last interval available:", last_time)
                self._set_state("Downloading new data")
                data = self._read_consumption(last_time)

                if len(data) > 0:
                    self._set_state("Saving new data")
                    with open(self.csvfn, "a") as F:
                        for rec in data:
                            F.write("\"%s\",\"%s\",%s\n" % (
                                rec["interval_start"],
                                rec["interval_end"],
                                rec["consumption"]
                            ))
                else:
                    print("No new data")

        except Exception as ex:
            _quit("Error %s: %s" % (self.state, str(ex)), 3)

        print("Done.")


# ---------------------------------------------------------------------- MAIN
if __name__ == "__main__":
    print("Download Octopus Energy Meter Readings\n")
    octoreader = OctoReader()
    octoreader.main()
