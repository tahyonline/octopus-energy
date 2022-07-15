from datetime import datetime, timedelta

from .lib import from_octo8601, to_ymd, to_hm
from .stateful import Stateful
from .data_acquisition import OctoReader


class Day:
    def __init__(self, dt: datetime):
        self.date = dt
        self.consumption = []
        self.times = []
        self.total = 0
        self.base = 0
        self.max = 0

    def is_full_day(self):
        return len(self.consumption) == 48


class Analytics(Stateful):
    def __init__(self, octoreader: OctoReader):
        Stateful.__init__(self)
        self._set_state("Initialising")
        if octoreader is None or not octoreader.ok:
            self._set_state("OctoReader is invalid", False)
            return

        self._populate(octoreader)

        self._set_state("Analytics initialised")

    def same_period(self, octoreader: OctoReader):
        return self.first_time == octoreader.first_time and self.last_time == octoreader.last_time

    def _populate(self, octoreader: OctoReader):
        self.first_time = octoreader.first_time
        self.last_time = octoreader.last_time
        self.days = {}
        self.full_days = []

        self.averages = {}
        self.baseaverages = {}
        self.maxaverages = {}
        self.average_days = [7, 14, 30, 60, 90]
        sums = {}
        basesums = {}
        maxsums = {}
        for ad in self.average_days:
            self.averages[ad] = {}
            self.baseaverages[ad] = {}
            self.maxaverages[ad] = {}
            sums[ad] = 0
            basesums[ad] = 0
            maxsums[ad] = 0

        i = 0

        last_dt = None
        day = None
        self.first_full_day = None
        self.last_full_day = None

        for r in octoreader.records:
            dt = from_octo8601(r[0])

            if last_dt is None or dt.day != last_dt.day:
                if last_dt is not None:
                    day.total = sum(day.consumption)
                    day.base = min(day.consumption) * 48
                    day.max = max(day.consumption)
                    self.days[to_ymd(last_dt)] = day
                    if day.is_full_day():
                        ymd = to_ymd(last_dt)
                        self.full_days.append(ymd)
                        i += 1
                        for ad in self.average_days:
                            sums[ad] += day.total
                            basesums[ad] += day.base
                            maxsums[ad] += day.max
                            if i >= ad:
                                self.averages[ad][ymd] = sums[ad] / ad
                                sums[ad] -= self.days[self.full_days[i - ad]].total

                                self.baseaverages[ad][ymd] = basesums[ad] / ad
                                basesums[ad] -= self.days[self.full_days[i - ad]].base

                                self.maxaverages[ad][ymd] = maxsums[ad] / ad
                                maxsums[ad] -= self.days[self.full_days[i - ad]].max


                last_dt = dt
                day = Day(dt)

            day.consumption.append(float(r[2]))
            day.times.append(to_hm(dt))

        if len(self.full_days):
            self.first_full_day = self.full_days[0]
            self.last_full_day = self.full_days[-1]

        self.days_dates = list(self.days.keys())
        # noinspection PyTypeChecker
        self.days_dates = sorted(self.days_dates)
